# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH


from httpx import Auth, Client, HTTPStatusError
from loguru import logger
from scim2_client import SCIMResponseError
from scim2_client.engines.httpx import SyncSCIMClient
from scim2_models import Resource, ResourceType, SearchRequest, ServiceProviderConfig

from univention.scim.client.helper import cust_pformat
from univention.scim.client.scim_client_settings import ScimConsumerSettings


# Mapping from UDM module/topic to SCIM resource type name
_TOPIC_TO_SCIM_TYPE: dict[str, str] = {
    "users/user": "User",
    "groups/group": "Group",
}


class ScimClientNoDataFoundException(Exception): ...


class ScimClientTooManyResultsException(Exception): ...


class ScimClient:
    _scim_client: SyncSCIMClient | None = None

    def __init__(
        self,
        auth: Auth | None,
        settings: ScimConsumerSettings,
    ):
        self.settings = settings
        self.auth = auth
        self.supports_service_provider_config = False

    def _create_client(self) -> SyncSCIMClient:
        """
        Returns a connected SyncSCIMClient instance.

        """
        logger.info("Connect to SCIM server ({}).", self.settings.scim_server_base_url)

        def manipulate_response_to_be_RFC_compliant(response):
            try:
                response.raise_for_status()
            except HTTPStatusError as e:
                if e.response.status_code == 404:
                    return

                e.response.read()
                json_payload = e.response.json()
                if json_payload and "message" in json_payload:
                    logger.warning("Rewrite response to be SCIM RFC compliant")
                    e.response._content = json_payload["message"].encode()

        client = Client(
            auth=self.auth,
            base_url=self.settings.scim_server_base_url,
            headers={
                "Accept": "application/scim+json",
                "Content-Type": "application/scim+json",
            },
            event_hooks={"response": [manipulate_response_to_be_RFC_compliant]},
        )

        scim = SyncSCIMClient(client=client, check_response_content_type=False)
        scim.discover(schemas=True, service_provider_config=False, resource_types=True)
        if scim.get_resource_model("ServiceProviderConfig") is not None:
            scim.discover(schemas=False, service_provider_config=True, resource_type=False)
            self.supports_service_provider_config = True
        else:
            logger.warning("Scim server does not support ServiceProviderConfig")

        if scim.get_resource_model("User") is None:
            logger.error("Scim server does not support User resource")
            raise RuntimeError("Scim server does not support User resource")
        if scim.get_resource_model("Group") is None:
            logger.error("Scim server does not support Group resource")
            raise RuntimeError("Scim server does not support Group resource")

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

    def _topic_to_resource_model(self, topic: str) -> type[Resource]:
        scim_type_name = _TOPIC_TO_SCIM_TYPE.get(topic)
        if scim_type_name is None:
            raise ValueError(f"Unknown UDM topic '{topic}', cannot determine SCIM resource type")
        resource_model = self._scim_client.get_resource_model(scim_type_name)
        if resource_model is None:
            raise RuntimeError(f"SCIM server does not support {scim_type_name} resource")
        return resource_model

    def health_check(self) -> bool:
        """
        Checks the state of the SCIM server by performing a simple ServiceProviderConfig request.

        This performs a minimal health check without generating any test data.
        """
        try:
            if not self._scim_client:
                return False
            # Perform a simple ServiceProviderConfig request to check if server is healthy
            # This is a read-only operation that doesn't create any test data
            if self.supports_service_provider_config:
                self._scim_client.query(ServiceProviderConfig)
            else:
                self._scim_client.query(ResourceType)

            return True
        except Exception as e:
            logger.debug("Health check failed: {}", e)
            return False

    def create_resource(self, resource: Resource) -> None:
        """
        Creates a SCIM resource.

        """
        logger.info("Create SCIM resource {}", resource.external_id)
        logger.debug("Resource data:\n{}", cust_pformat(resource.model_dump()))

        try:
            response = self.get_client().create(resource, check_response_payload=False)
            logger.debug("Response:\n{}", cust_pformat(response))

        # Happens when the object exists, but without externalId
        # e.g. group "Domain Users" when the SCIM server is an
        # Univention SCIM server.
        except SCIMResponseError as e:
            logger.warning(e)

    def update_resource(self, resource: Resource) -> None:
        """
        Updates one SCIM resource.

        Fetches the current data from the SCIM server via the external_id (univentionObjectIdentifier),
        merges the data and write it back to the SCIM server.
        """
        logger.info("Update SCIM resource {}", resource.external_id)
        logger.debug("Resource data:\n{}", cust_pformat(resource.model_dump()))

        response = self.get_client().replace(resource, check_response_payload=False)

        logger.debug("Response:\n{}", cust_pformat(response))

    def delete_resource(self, id: str, udm_module: str) -> None:
        """
        Deletes a SCIM resource by id and UDM module.
        """
        scim_type_name = _TOPIC_TO_SCIM_TYPE.get(udm_module)
        if scim_type_name is None:
            raise ValueError(f"Unknown UDM module '{udm_module}', must be 'users/user' or 'groups/group'")
        resource_model = self.get_client().get_resource_model(scim_type_name)
        if resource_model is None:
            raise RuntimeError(f"SCIM server does not support {scim_type_name} resource")

        response = self.get_client().delete(resource_model=resource_model, id=id, check_response_payload=False)

        logger.debug("Delete response:\n{}", cust_pformat(response))

    def get_resource(self, external_id: str, udm_module: str) -> dict:
        """
        Returns the SCIM resource data as a dict for the given external_id.

        Parameters
        ----------
        external_id : str
            The external identifier (e.g. univentionObjectIdentifier).
        udm_module : str
            The UDM module/topic: "users/user" or "groups/group".

        Raises
        ------
        ScimClientNoDataFoundException
            If no record with the given external_id is found.
        ScimClientTooManyResultsException
            If more than one record with the given external_id is found.
        """
        scim_type_name = _TOPIC_TO_SCIM_TYPE.get(udm_module)
        if scim_type_name is None:
            raise ValueError(f"Unknown UDM module '{udm_module}', must be 'users/user' or 'groups/group'")
        resource_model = self.get_client().get_resource_model(scim_type_name)
        if resource_model is None:
            raise RuntimeError(f"SCIM server does not support {scim_type_name} resource")
        search_request = SearchRequest(filter=f'externalId eq "{external_id}"')
        response = self.get_client().query(
            search_request=search_request,
            resource_model=resource_model,
            check_response_payload=False,
        )
        logger.debug("SCIM query response:\n{}", response)

        if response["totalResults"] == 0:
            raise ScimClientNoDataFoundException(f"No data found for record with external_id = {external_id}!")

        if response["totalResults"] == 1:
            return response["Resources"][0]

        raise ScimClientTooManyResultsException(
            f"Too many results for record with external_id = {external_id}! Expected 1 got {response['totalResults']}."
        )

    def get_user(self, external_id: str) -> dict:
        """
        Returns the SCIM user data as a dict for the given external_id.
        """
        return self.get_resource(external_id, "users/user")

    def get_group(self, external_id: str) -> dict:
        """
        Returns the SCIM group data as a dict for the given external_id.
        """
        return self.get_resource(external_id, "groups/group")
