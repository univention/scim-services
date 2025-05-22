# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

from httpx import Client
from loguru import logger
from pydantic_settings import BaseSettings
from scim2_client.engines.httpx import SyncSCIMClient
from scim2_models import Group, Resource, ResourceType, SearchRequest, User
from scim2_tester import check_server

from univention.scim.consumer.helper import cust_pformat


class ScimClientNoDataFoundException(Exception):
    pass


class ScimClientTooManyResultsException(Exception):
    pass


class ScimClientSettings(BaseSettings):
    scim_server_base_url: str
    health_check_enabled: bool = True
    # TODO Add auth settings


class ScimClientWrapper:
    _scim_client: SyncSCIMClient = None

    def __init__(
        self,
        settings: ScimClientSettings | None = None,
    ):
        self.settings = settings or ScimClientSettings()

    def _create_client(self) -> SyncSCIMClient:
        """
        Returns a connected SyncSCIMClient instance.

        Returns
        -------
        SyncSCIMClient
        """
        logger.info("Connect to SCIM server.")

        client = Client(base_url=self.settings.scim_server_base_url)

        scim = SyncSCIMClient(
            client=client,
            resource_models=[User, Group],
            resource_types=[
                ResourceType(
                    id="User",
                    name="User",
                    schemas=[
                        "urn:ietf:params:scim:schemas:core:2.0:ResourceType",
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

        return scim

    def get_client(self) -> SyncSCIMClient:
        """
        Returns a connected SCIM client instance.

        If the connection did not exists it would be created.
        If the connection exists already, it is checked for health and
        reconnected if necessary.

        Returns
        -------
        SyncSCIMClient
        """
        if not self._scim_client or (self.settings.health_check_enabled and not self.health_check(self._scim_client)):
            self._scim_client = self._create_client()

        return self._scim_client

    def health_check(self, client: SyncSCIMClient) -> bool:
        """
        Checks the state of the SCIM server.

        Parameters
        ----------
        client : SyncSCIMClient

        Returns
        -------
        bool
            True if the state is OK, False when an error occurs.
        """
        dirty = False
        try:
            # results = check_server(client)
            check_server(client)
        except Exception as e:
            logger.error(e)
            dirty = True
        # else:
        #     for result in results:
        #         # logger.debug("SCIM server state: {}: {}", result.status.name, result.title)
        #         # TODO Refactor! Very unclean solution!
        #         if result.status.name != "SUCCESS":
        #             logger.debug("SCIM server state: {}: {}", result.status.name, result.title)
        #             dirty = True

        return not dirty

    def create_resource(self, resource: Resource):
        """
        Creates a SCIM resource.

        Parameters
        ----------
        resource : Resource
            A filled scim2_models.Resource instance.
        """
        logger.info("Create SCIM resource {}", resource.external_id)
        logger.debug("Resource data:\n{}", cust_pformat(resource.model_dump()))

        response = self.get_client().create(resource)

        logger.debug("Response:\n{}", cust_pformat(response))

    def update_resource(self, resource: Resource):
        """
        Updates one SCIm resource.

        Fetches the current data from the SCIM server via the external_id (univentionObjectIdentifier),
        merges the data and write it back to the SCIM server.

        Parameters
        ----------
        resource : Resource
            A filled scim2_models.Resource instance.

        Raises
        ------
        ScimClientNoDataFoundException
            If no record with the given external_id is found.
        ScimClientTooManyResultsException
            If more then one record with the given external_id is found.
        """
        logger.info("Update SCIM resource {}", resource.external_id)
        logger.debug("Resource type: {}", type(resource))
        logger.debug("Resource data:\n{}", cust_pformat(resource))

        # Get the existing user from SCIM server
        scim_resource = self.get_resource_by_external_id(resource.external_id)

        logger.debug("SCIM response resource type: {}", type(scim_resource))
        logger.debug("SCIM response resource data:\n{}", cust_pformat(scim_resource))

        # Add the ID and the meta data from the SCIM server.
        #   The ID must be set, because we only have the external ID at this point
        #   and the update URL will be generated, the meta.location URL is not used!
        resource.id = scim_resource.id
        resource.meta = scim_resource.meta

        logger.debug("Merged data for update:\n{}", cust_pformat(resource))

        response = self.get_client().replace(resource)

        logger.debug("Response:\n{}", cust_pformat(response))

    def delete_resource(self, resource: Resource):
        """
        Deletes a SCIM resource.

        Fetches the current data from the SCIM server via the external_id (univentionObjectIdentifier)
        and then delete it via SCIM id and resource type.

        Raises
        ------
        ScimClientNoDataFoundException
            If no record with the given external_id is found.
        ScimClientTooManyResultsException
            If more then one record with the given external_id is found.
        """
        logger.info("Delete resource {}", resource.external_id)
        logger.debug("Resource type: {}", type(resource))
        logger.debug("Resource data:\n{}", cust_pformat(resource))

        # Get the existing user from SCIM server
        scim_resource = self.get_resource_by_external_id(resource.external_id)

        logger.debug("SCIM resource type: {}", type(scim_resource))
        logger.debug("SCIM resource:\n{}", cust_pformat(scim_resource))

        response = self.get_client().delete(resource_model=type(scim_resource), id=scim_resource.id)

        logger.debug("Response:\n{}", cust_pformat(response))

    def get_resource_by_external_id(self, external_id: str) -> Resource:
        """
        Returns a SCIM resource with the given external ID.


        Parameters
        ----------
        external_id :str
            The univentionObjectIdentifier (UUID)

        Raises
        ------
        ScimClientNoDataFoundException
            If no record with the given external_id is found.
        ScimClientTooManyResultsException
            If more then one record with the given external_id is found.
        """
        search_request = SearchRequest(filter=f'externalId eq "{external_id}"')
        response = self.get_client().query(search_request=search_request)

        if response.total_results == 1:
            return response.resources[0]

        elif response.total_results == 0:
            raise ScimClientNoDataFoundException(f"No data found for record with external_id = {external_id}!")

        else:
            raise ScimClientTooManyResultsException(
                f"Too many results for record with external_id = {external_id}! Epected 1 got {response.total_results}."
            )
