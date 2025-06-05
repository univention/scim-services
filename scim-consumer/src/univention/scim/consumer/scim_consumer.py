# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

from loguru import logger
from scim2_models import Resource

from univention.scim.consumer.group_membership_resolver import GroupMembershipLdapResolver
from univention.scim.consumer.helper import cust_pformat
from univention.scim.consumer.scim_client import ScimClient, ScimClientNoDataFoundException
from univention.scim.server.models.user import User
from univention.scim.transformation.udm2scim import UdmToScimMapper


class ScimConsumer:
    """ """

    def __init__(self):
        self.scim_client = ScimClient()

    def write_udm_object(self, udm_object: object, topic: str) -> None:
        """
        Writes the record to the SCIM server.

        raises:
            ValueError: If no external_id is given.
        """
        scim_resource = self.prepare_data(udm_object, topic)

        if not scim_resource.external_id:
            raise ValueError("No external_id given!")

        try:
            existing_scim_resource = self.scim_client.get_resource_by_external_id(scim_resource.external_id)

        except ScimClientNoDataFoundException:
            self.scim_client.create_resource(scim_resource)

        else:
            scim_resource.id = existing_scim_resource.id
            scim_resource.meta = existing_scim_resource.meta

            self.scim_client.update_resource(scim_resource)

    def delete_udm_object(self, udm_object: object, topic: str) -> None:
        """
        Deletes the record in the SCIM server.

        raises:
            ValueError: If no external_id is given.
        """
        scim_resource = self.prepare_data(udm_object, topic)

        if not scim_resource.external_id:
            raise ValueError("No external_id given!")

        try:
            existing_scim_resource = self.scim_client.get_resource_by_external_id(scim_resource.external_id)

        except ScimClientNoDataFoundException:
            pass

        else:
            self.scim_client.delete_resource(existing_scim_resource)

    def prepare_data(self, udm_object: object, topic: str) -> Resource:
        """
        Maps the data from UDM to SCIM

        raises:
            ValueError: If topic is not users/user or groups/group
        """
        # FIXME: Use correct properties for external ID mapping or set it manually after the mapping.
        #        For now use univentionObjectIdentifier to make the existing tests happy, it was also the
        #        previouse workaround.
        mapper = UdmToScimMapper(
            external_id_user_mapping="univentionObjectIdentifier",
            external_id_group_mapping="univentionObjectIdentifier",
        )
        if topic == "users/user":
            scim_resource = mapper.map_user(udm_user=udm_object)

        elif topic == "groups/group":
            scim_resource = mapper.map_group(udm_group=udm_object)
            # if scim_resource.members is None:
            #     scim_resource.members = []
        else:
            raise ValueError(f"Unsupported message topic {topic}")

        logger.debug("Mapped resource:\n{}", cust_pformat(scim_resource))

        return scim_resource
