# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

from httpx import Client
from loguru import logger
from scim2_client import SCIMResponseError
from scim2_client.engines.httpx import SyncSCIMClient
from scim2_models import Group, Resource, ResourceType, SchemaExtension, SearchRequest
from scim2_tester import check_server

from univention.scim.consumer.helper import cust_pformat
from univention.scim.consumer.scim_consumer_settings import ScimConsumerSettings
from univention.scim.server.models.user import User as UniventionScimUser


class ScimClientNoDataFoundException(Exception): ...


class ScimClientTooManyResultsException(Exception): ...


class ScimClient:
    _scim_client: SyncSCIMClient = None

    def __new__(cls, *args, **kwargs):
        """
        Singleton pattern
        """
        if not hasattr(cls, "instance"):
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(
        self,
        settings: ScimConsumerSettings | None = None,
    ):
        self.settings = settings or ScimConsumerSettings()

    def _create_client(self) -> SyncSCIMClient:
        """
        Returns a connected SyncSCIMClient instance.

        """
        logger.info("Connect to SCIM server ({}).", self.settings.scim_server_base_url)

        client = Client(base_url=self.settings.scim_server_base_url)

        scim = SyncSCIMClient(
            client=client,
            resource_models=[UniventionScimUser, Group],
            resource_types=[
                ResourceType(
                    id="User",
                    name="User",
                    schemas=[
                        "urn:ietf:params:scim:schemas:core:2.0:ResourceType",
                    ],
                    schema_extensions=[
                        SchemaExtension(_schema="urn:ietf:params:scim:schemas:extension:enterprise:2.0:User"),
                        SchemaExtension(_schema="urn:ietf:params:scim:schemas:extension:Univention:1.0:User"),
                        SchemaExtension(_schema="urn:ietf:params:scim:schemas:extension:DapUser:2.0:User"),
                    ],
                    endpoint="/Users",
                    description="User Account",
                    schema="urn:ietf:params:scim:schemas:core:2.0:User",
                ),
                ResourceType(
                    id="Group",
                    name="Group",
                    schemas=[
                        "urn:ietf:params:scim:schemas:core:2.0:ResourceType",
                    ],
                    endpoint="/Groups",
                    description="User groups",
                    schema="urn:ietf:params:scim:schemas:core:2.0:Group",
                ),
            ],
        )

        # TODO Ask SCIM team why this is not working
        # Discover resources
        # scim = SyncSCIMClient(client=client, resource_models=[User, Group])
        # scim.discover(schemas=True, resource_types=True, service_provider_config=True)
        #
        # Result: At the moment, the Univention SCIM Server doesen't support the
        # discover function. This topic has to be clearified ...

        return scim

    def get_client(self) -> SyncSCIMClient:
        """
        Returns a connected SCIM client instance.

        If the connection did not exists it would be created.
        If the connection exists already, it is checked for health and
        reconnected if necessary.

        """
        if not self._scim_client or (self.settings.health_check_enabled and not self.health_check()):
            self._scim_client = self._create_client()

        return self._scim_client

    def health_check(self) -> bool:
        """
        Checks the state of the SCIM server.

        """
        try:
            check_server(self._scim_client)
        except Exception:
            return False
        else:
            return True

    def create_resource(self, resource: Resource):
        """
        Creates a SCIM resource.

        """
        logger.info("Create SCIM resource {}", resource.external_id)
        logger.debug("Resource data:\n{}", cust_pformat(resource.model_dump()))

        try:
            response = self.get_client().create(resource)
            logger.debug("Response:\n{}", cust_pformat(response))
        
        # FIXME Happens when the object exists, but without externalId
        #       e.g. group "Domain Users" when the SCIM server is an
        #       Univention SCIM server.
        #
        #       Maybe trigger an update here ... But could be dangerous?!
        except SCIMResponseError as e:
            logger.warning(e)

    def update_resource(self, resource: Resource):
        """
        Updates one SCIM resource.

        Fetches the current data from the SCIM server via the external_id (univentionObjectIdentifier),
        merges the data and write it back to the SCIM server.
        """
        logger.info("Update SCIM resource {}", resource.external_id)
        logger.debug("Resource data:\n{}", cust_pformat(resource.model_dump()))

        response = self.get_client().replace(resource)

        logger.debug("Response:\n{}", cust_pformat(response))

    def delete_resource(self, resource: Resource):
        """
        Deletes a SCIM resource.

        Fetches the current data from the SCIM server via the external_id (univentionObjectIdentifier)
        and then delete it via SCIM id and resource type.
        """
        logger.info("Delete resource {}", resource.external_id)
        logger.debug("Resource data:\n{}", cust_pformat(resource.model_dump()))

        response = self.get_client().delete(resource_model=type(resource), id=resource.id)

        logger.debug("Response:\n{}", cust_pformat(response))

    def get_resource_by_external_id(self, external_id: str) -> Resource:
        """
        Returns a SCIM resource with the given external ID.

        Raises
        ------
        ScimClientNoDataFoundException
            If no record with the given external_id is found.
        ScimClientTooManyResultsException
            If more then one record with the given external_id is found.
        """
        search_request = SearchRequest(filter=f'externalId eq "{external_id}"')
        response = self.get_client().query(search_request=search_request)
        logger.debug("SCIM query response:\n{}", response)
        
        if response.total_results == 1:
            return response.resources[0]

        elif response.total_results == 0:
            raise ScimClientNoDataFoundException(f"No data found for record with external_id = {external_id}!")

        else:
            raise ScimClientTooManyResultsException(
                f"Too many results for record with external_id = {external_id}! Epected 1 got {response.total_results}."
            )
