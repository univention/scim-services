# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH


from httpx import Auth, Client, HTTPStatusError
from loguru import logger
from scim2_client import SCIMResponseError
from scim2_client.engines.httpx import SyncSCIMClient
from scim2_models import AuthenticationScheme, Resource, ResourceType, SearchRequest, ServiceProviderConfig

from univention.scim.client.authentication import AuthMethod
from univention.scim.client.helper import cust_pformat
from univention.scim.client.scim_client_settings import ScimConsumerSettings


# Mapping from UDM module/topic to SCIM resource type name
_TOPIC_TO_SCIM_TYPE: dict[str, str] = {
    "users/user": "User",
    "groups/group": "Group",
}

# SCIM authenticationSchemes.type values that satisfy each configured AuthMethod.
# AuthMethod.NONE has no entry: nothing is configured, so there's nothing to verify.
_AUTH_METHOD_TO_SCHEME_TYPES: dict[AuthMethod, tuple[AuthenticationScheme.Type, ...]] = {
    AuthMethod.OIDC: (AuthenticationScheme.Type.oauthbearertoken,),
    AuthMethod.BEARER: (AuthenticationScheme.Type.oauthbearertoken,),
    AuthMethod.BASIC: (AuthenticationScheme.Type.httpbasic,),
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
        self.service_provider_config: ServiceProviderConfig | None = None

    def _create_client(self) -> SyncSCIMClient:
        """
        Returns a connected SyncSCIMClient instance.

        Verifies discovery (/ResourceTypes, /Schemas, /ServiceProviderConfig),
        filter search, the configured auth scheme, and the User (and, if group
        sync is enabled, Group) resource type.
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

        try:
            scim.discover(schemas=True, service_provider_config=False, resource_types=True)
        except Exception as e:
            logger.error(
                "Scim server does not support ResourceType/Schema discovery.",
                capability="discovery",
                error=str(e),
            )
            raise RuntimeError("Scim server does not support ResourceType/Schema discovery") from e

        try:
            scim.discover(schemas=False, service_provider_config=True, resource_types=False)
        except Exception as e:
            logger.error(
                "Scim server does not support ServiceProviderConfig discovery.",
                capability="service_provider_config",
                error=str(e),
            )
            raise RuntimeError("Scim server does not support ServiceProviderConfig discovery") from e

        service_provider_config = scim.service_provider_config
        if service_provider_config is None:
            logger.error(
                "Scim server did not return a ServiceProviderConfig.",
                capability="service_provider_config",
            )
            raise RuntimeError("Scim server did not return a ServiceProviderConfig")
        self.service_provider_config = service_provider_config

        if not (service_provider_config.filter and service_provider_config.filter.supported):
            logger.error(
                "Scim server does not support attribute filtering, required for externalId lookups.",
                capability="filter",
            )
            raise RuntimeError("Scim server does not support attribute filtering")

        self._verify_auth_scheme(service_provider_config)

        if scim.get_resource_model("User") is None:
            logger.error("Scim server does not support User resource.", capability="User resource type")
            raise RuntimeError("Scim server does not support User resource")

        if scim.get_resource_model("Group") is None:
            if self.settings.group_sync_enabled:
                logger.error("Scim server does not support Group resource.", capability="Group resource type")
                raise RuntimeError("Scim server does not support Group resource")
            logger.info("Scim server does not support Group resource. Continuing in users-only mode.")

        return scim

    def _verify_auth_scheme(self, service_provider_config: ServiceProviderConfig) -> None:
        """
        Verifies the configured auth method is among the server's advertised
        authenticationSchemes.
        """
        required_scheme_types = _AUTH_METHOD_TO_SCHEME_TYPES.get(self.settings.scim_auth_method)
        if not required_scheme_types:
            return

        advertised_scheme_types = {
            scheme.type for scheme in (service_provider_config.authentication_schemes or []) if scheme.type
        }
        if advertised_scheme_types.isdisjoint(required_scheme_types):
            logger.error(
                "Scim server does not advertise an authentication scheme for the configured auth method.",
                capability="authentication_schemes",
                configured_auth_method=self.settings.scim_auth_method,
                required_scheme_types=[scheme_type.value for scheme_type in required_scheme_types],
                advertised_scheme_types=sorted(scheme_type.value for scheme_type in advertised_scheme_types),
            )
            raise RuntimeError(
                f"Scim server does not advertise an authentication scheme for '{self.settings.scim_auth_method}'"
            )

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

    def get_resource_model_for_topic(self, topic: str) -> type[Resource]:
        scim_type_name = _TOPIC_TO_SCIM_TYPE.get(topic)
        if scim_type_name is None:
            raise ValueError(f"Unknown UDM topic '{topic}', cannot determine SCIM resource type")
        resource_model = self.get_client().get_resource_model(scim_type_name)
        if resource_model is None:
            raise RuntimeError(f"SCIM server does not support {scim_type_name} resource")
        return resource_model

    def health_check(self) -> bool:
        """
        Checks the state of the SCIM server by performing a simple ResourceType request.

        This performs a minimal health check without generating any test data.
        """
        try:
            if not self._scim_client:
                return False
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

    def delete_resource(self, id: str, resource_model: type[Resource]) -> None:
        """
        Deletes a SCIM resource by id.
        """
        response = self.get_client().delete(resource_model=resource_model, id=id, check_response_payload=False)

        logger.debug("Delete response:\n{}", cust_pformat(response))

    def get_resource(self, external_id: str, resource_model: type[Resource]) -> dict:
        """
        Returns the SCIM resource data as a dict for the given external_id.

        Parameters
        ----------
        external_id : str
            The external identifier (e.g. univentionObjectIdentifier).
        resource_model : type[Resource]

        Raises
        ------
        ScimClientNoDataFoundException
            If no record with the given external_id is found.
        ScimClientTooManyResultsException
            If more than one record with the given external_id is found.
        """
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
        return self.get_resource(external_id, self.get_resource_model_for_topic("users/user"))

    def get_group(self, external_id: str) -> dict:
        """
        Returns the SCIM group data as a dict for the given external_id.
        """
        return self.get_resource(external_id, self.get_resource_model_for_topic("groups/group"))
