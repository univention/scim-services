# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

from httpx import Client
from icecream import ic
from loguru import logger
from pydantic_settings import BaseSettings
from scim2_client.engines.httpx import SyncSCIMClient
from scim2_models import Group, Resource, ResourceType, SearchRequest, User
from scim2_tester import check_server

from univention.scim.consumer.helper import vars_recursive


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
        if not self._scim_client or (self.settings.health_check_enabled and not self.health_check(self._scim_client)):
            self._scim_client = self._create_client()

        return self._scim_client

    def health_check(self, client: SyncSCIMClient) -> bool:
        results = check_server(client)
        for result in results:
            logger.debug("SCIM server state: {}: {}", result.status.name, result.title)
        return True

    def create_resource(self, resource: Resource):
        logger.info("Create resource")
        logger.debug("Resource:\n{}", ic.format(resource.model_dump()))

        response = self.get_client().create(resource)

        logger.debug("Response:\n{}", ic.format(vars_recursive(response)))

    def update_resource(self, resource: Resource):
        logger.info("Update resource")
        logger.debug("Resource type: {}", type(resource))
        logger.debug("Resource:\n{}", ic.format(vars_recursive(resource)))

        # Get the existing user from SCIM server
        try:
            scim_resource = self.get_resource_by_external_id(resource.external_id)
        except Exception as e:
            logger.error(e)
            return

        logger.debug("SCIM resource type: {}", type(scim_resource))
        logger.debug("SCIM resource:\n{}", ic.format(vars_recursive(scim_resource)))

        # Add the ID and the meta data from the SCIM server.
        #   The ID must be set, because we only have the external ID at this point
        #   and the update URL will be generated, the meta.location URL is not used!
        resource.id = scim_resource.id
        resource.meta = scim_resource.meta

        logger.debug("Resource merged:\n{}", ic.format(vars_recursive(resource)))

        response = self.get_client().replace(resource)

        logger.debug("Response:\n{}", ic.format(vars_recursive(response)))

    def delete_resource(self, resource: Resource):
        logger.info("Delete resource")
        logger.debug("Resource type: {}", type(resource))
        logger.debug("Resource:\n{}", ic.format(vars_recursive(resource)))

        # Get the existing user from SCIM server
        try:
            scim_resource = self.get_resource_by_external_id(resource.external_id)
        except Exception as e:
            logger.error(e)
            return

        logger.debug("SCIM resource type: {}", type(scim_resource))
        logger.debug("SCIM resource:\n{}", ic.format(vars_recursive(scim_resource)))

        if scim_resource.meta.resource_type == "User":
            response = self.get_client().delete(resource_model=User, id=scim_resource.id)
        elif scim_resource.meta.resource_type == "Group":
            response = self.get_client().delete(resource_model=Group, id=scim_resource.id)
        else:
            raise Exception(f"Resource type {scim_resource.meta.resource_type} is not implemented yet!")

        logger.debug("Response:\n{}", ic.format(vars_recursive(response)))

    def get_resource_by_external_id(self, external_id: str) -> Resource:
        search_request = SearchRequest(filter=f'externalId eq "{external_id}"')
        response = self.get_client().query(search_request=search_request)

        if response.total_results == 1:
            return response.resources[0]

        elif response.total_results == 0:
            raise Exception("No data found!")

        else:
            logger.error("SCIM query resources result:\n{}", ic.format(response.resources))
            raise Exception("To many results!")
