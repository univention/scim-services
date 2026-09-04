# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

import asyncio
import json
import traceback
from typing import cast

from loguru import logger
from scim2_client import RequestNetworkError
from scim2_models import Resource
from univention.provisioning.models import Message

from univention.provisioning.error_handling.db import DBSession, normalized_dn
from univention.scim.client.group_membership_resolver import GroupMembershipLdapResolver
from univention.scim.client.helper import cust_pformat
from univention.scim.client.scim_client_settings import ScimConsumerSettings
from univention.scim.client.scim_http_client import ScimClient, ScimClientNoDataFoundException
from univention.scim.transformation.udm2scim import UdmToScimMapper, supported_attribute_names


class ScimConsumer:
    """ """

    def __init__(
        self,
        scim_http_client: ScimClient,
        group_membership_resolver: GroupMembershipLdapResolver | None,
        settings: ScimConsumerSettings,
        database: DBSession,
    ):
        self.scim_http_client = scim_http_client
        self.group_membership_resolver = group_membership_resolver
        self.settings = settings
        self.database = database

    def _external_id_mapping_for_topic(self, topic: str) -> str | None:
        if topic == "users/user":
            return cast(str | None, self.settings.external_id_user_mapping)
        if topic == "groups/group":
            return cast(str | None, self.settings.external_id_group_mapping)
        return None

    def _external_id_for(self, udm_object: object, topic: str) -> str | None:
        """Value of the UDM property that maps to SCIM externalId for `topic`."""
        mapping = self._external_id_mapping_for_topic(topic)
        if not mapping:
            return None
        return getattr(udm_object, "properties", {}).get(mapping)

    def write_udm_object(self, udm_object: object, topic: str) -> None:
        """
        Writes the record to the SCIM server.

        raises:
            ValueError: If no external_id is given.
        """
        resource_model = self.scim_http_client.get_resource_model_for_topic(topic)

        external_id = self._external_id_for(udm_object, topic)
        if not external_id:
            raise ValueError("No external_id given!")

        try:
            existing = self.scim_http_client.get_resource(external_id, resource_model)
            scim_resource = self.prepare_data(udm_object, topic, resource_model, exclude_immutable=True)
            scim_resource.id = existing["id"]
            scim_resource.meta = existing.get("meta")
            self.scim_http_client.update_resource(scim_resource)
        except ScimClientNoDataFoundException:
            scim_resource = self.prepare_data(udm_object, topic, resource_model, exclude_immutable=False)
            # id and meta are assigned by the service provider (RFC 7644 SS3.3) and must
            # not be sent on create.
            scim_resource.id = None
            scim_resource.meta = None
            self.scim_http_client.create_resource(scim_resource)

    def delete(self, udm_object: object, topic: str) -> None:
        """
        Deletes the record in the SCIM server.

        raises:
            ValueError: If the UDM property mapped to externalId for `topic` is not given.
        """
        external_id = self._external_id_for(udm_object, topic)
        if not external_id:
            raise ValueError(f"No {self._external_id_mapping_for_topic(topic)} given!")

        resource_model = self.scim_http_client.get_resource_model_for_topic(topic)

        try:
            existing = self.scim_http_client.get_resource(external_id, resource_model)
        except ScimClientNoDataFoundException:
            return

        logger.info("Delete SCIM resource {} ({}).", existing["id"], existing["externalId"])

        self.scim_http_client.delete_resource(existing["id"], resource_model)

    def prepare_data(
        self, udm_object: object, topic: str, resource_model: type[Resource], *, exclude_immutable: bool = False
    ) -> Resource:
        """
        Maps the data from UDM to SCIM

        `exclude_immutable`: pass `True` when the resource is being built for an update
        (PUT) rather than a create -- immutable attributes may only be set at creation
        (RFC 7643 SS7).

        raises:
            ValueError: If topic is not users/user or groups/group
        """
        mapper_kwargs = {
            "cache": self.group_membership_resolver,
            "external_id_user_mapping": self.settings.external_id_user_mapping,
            "external_id_group_mapping": self.settings.external_id_group_mapping,
            "username_mapping": self.settings.username_mapping,
        }

        supported_attributes = supported_attribute_names(resource_model, exclude_immutable=exclude_immutable)

        if topic == "users/user":
            mapper = UdmToScimMapper(
                user_type=resource_model, supported_attributes=supported_attributes, **mapper_kwargs
            )
            scim_resource = mapper.map_user(udm_user=udm_object)
            logger.debug("Mapped resource:\n{}", cust_pformat(scim_resource))
            return scim_resource

        if topic == "groups/group":
            mapper = UdmToScimMapper(
                group_type=resource_model, supported_attributes=supported_attributes, **mapper_kwargs
            )
            scim_resource = mapper.map_group(udm_group=udm_object)
            logger.debug("Mapped resource:\n{}", cust_pformat(scim_resource))
            return scim_resource

        raise ValueError(f"Unsupported message topic {topic}")

    async def handle_udm_message(self, message: Message) -> None:
        """
        Handles provisioning messages for a SCIM client.

        The message is enqueued in the SQL task queue and all pending tasks are
        processed. If this method returns, the message will be acknowledged and
        this function will be called with the next message.
        If this method throws an exception, the message won't be acknowledged
        and the same message will be redelivered.
        """
        logger.debug("Message:\n{}", cust_pformat(message))

        if message.realm != "udm":
            raise ValueError(f"Unsupported message realm {message.realm}")

        if not message.body.new and not message.body.old:
            raise ValueError("Invalid message state.")

        if message.topic not in ("users/user", "groups/group"):
            return

        if message.topic == "groups/group" and not self.settings.group_sync_enabled:
            logger.debug("Skipping group message, group sync is disabled")
            return

        # We ignore body.old because it is read from the DB when processing the task
        # having attributes None in case of delete is required for task to behave correctly
        obj_attrs = None
        if message.body.new:
            obj_id = message.body.new["properties"]["univentionObjectIdentifier"]
            obj_dn = normalized_dn(message.body.new.get("dn"))
            obj_attrs = message.body.new.get("properties")
        else:
            obj_id = message.body.old["properties"]["univentionObjectIdentifier"]
            obj_dn = normalized_dn(message.body.old.get("dn"))

        # The context manager commits the task before it is processed.
        with self.database as db:
            logger.info("Enqueuing task", obj=obj_id, module=message.topic)
            db.enqueue_task(
                obj_id=obj_id,
                udm_module=message.topic,
                dn=obj_dn,
                attrs=obj_attrs,
            )

        await self.process_pending_tasks()

    async def process_pending_tasks(self) -> None:
        """Process queued tasks, retrying network failures after a delay."""
        while True:
            with self.database as db:
                retry_delay = self._process_all_tasks_with_db(db)

            if retry_delay is None:
                return

            await asyncio.sleep(retry_delay)

    def _process_all_tasks_with_db(self, db: DBSession) -> int | None:
        """
        Process all pending tasks from the queue using the provided DBSession.

        Network failures leave the task pending and stop this processing run
        until the returned delay has elapsed. Other failed tasks are moved to
        the morgue and processing continues.
        """
        for udm_module in ("users/user", "groups/group"):
            if udm_module == "groups/group" and not self.settings.group_sync_enabled:
                continue
            for task in db.get_tasks(udm_module, None):
                try:
                    logger.info("Processing Task", task=task)
                    udm_object = self._obj_from_task(task, db)
                    if should_exist(
                        task.udm_module,
                        json.loads(task.attrs) if task.attrs else None,
                        self.settings.scim_user_filter_attribute,
                        self.settings.scim_group_filter_attribute,
                    ):
                        self.write_udm_object(udm_object, task.udm_module)
                    else:
                        self.delete(udm_object, task.udm_module)
                except RequestNetworkError as exc:
                    logger.error("Error while handling", task=task)
                    num_errors = db.increment_error_count(task.id)
                    logger.exception(exc)
                    retry_delay = min(num_errors * 5, 20 * 60)
                    logger.info(
                        "Waiting for {} seconds before retrying task",
                        retry_delay,
                        task=task,
                    )
                    return retry_delay
                except Exception as exc:
                    db.increment_error_count(task.id)
                    logger.error("Error while handling", task=task)
                    logger.exception(exc)
                    db.move_task_to_morgue(task.id, traceback.format_exc())
                    # Continue to next task after morgue
                    continue
                else:
                    if task.attrs is None:
                        db.delete_old(dn=udm_object.old_distinguished_name)
                        db.remove_task(task.id)
                    else:
                        db.move_task_to_old(task.id, json.loads(task.attrs))

            # Persist progress before processing the next module.
            db.commit()

        return None

    def _obj_from_task(self, task, db: DBSession) -> object:
        """
        Create a UDM-like object from a DB task row.

        For delete tasks (attrs is None) the properties fall back to the last
        successfully synced state from the old table.
        """
        attrs = json.loads(task.attrs) if task.attrs else None
        old = db.get_old(None, task.obj_id)
        old_attrs = json.loads(old.attrs) if old and old.attrs else None

        if attrs is not None:
            properties = attrs
        elif old_attrs:
            properties = old_attrs
        elif external_id_mapping := self._external_id_mapping_for_topic(task.udm_module):
            properties = {external_id_mapping: task.obj_id}
        else:
            properties = None

        udm_object = type(
            "Obj",
            (object,),
            {"properties": properties, "dn": task.dn, "objectType": task.udm_module},
        )()
        udm_object.old_distinguished_name = old.dn if old else task.dn
        return udm_object


def should_exist(
    udm_module: str,
    properties: dict | None,
    user_filter_attribute: str | None,
    group_filter_attribute: str | None = None,
) -> bool:
    """
    Returns the expected state in SCIM after processing the given UDM state.
    """
    if user_filter_attribute and udm_module == "users/user":
        result = bool(properties and properties.get(user_filter_attribute))
        logger.debug("should_exist: {} - By user filter attribute", result)
        return result

    if group_filter_attribute and udm_module == "groups/group":
        result = bool(properties and properties.get(group_filter_attribute))
        logger.debug("should_exist: {} - By group filter attribute", result)
        return result

    result = bool(properties)
    logger.debug("should_exist: {} - By message body", result)
    return result


def should_exist_in_scim(
    message: Message, user_filter_attribute: str | None, group_filter_attribute: str | None = None
) -> bool:
    """
    Returns the expected state in SCIM after processing the message.
    """
    return should_exist(
        message.topic,
        message.body.new.get("properties") if message.body.new else None,
        user_filter_attribute,
        group_filter_attribute,
    )
