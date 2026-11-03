# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2026 Univention GmbH


from httpx2 import Auth, Client, HTTPStatusError
from loguru import logger
from pydantic import HttpUrl
from scim2_client import RequestNetworkException, SCIMClientException
from scim2_client.engines.httpx2 import SyncSCIMClient
from scim2_models import (
    Error,
    Group,
    Resource,
    ResourceType,
    SCIMException,
    ScimPolicy,
    ScimProvider,
    SearchRequest,
    ServiceProviderConfig,
    User,
)

from univention.scim.client.authentication import required_scim_scheme_types
from univention.scim.client.helper import cust_pformat
from univention.scim.client.scim_client_settings import ScimConsumerSettings


# Mapping from UDM module/topic to SCIM resource type name
_TOPIC_TO_SCIM_TYPE: dict[str, str] = {
    "users/user": "User",
    "groups/group": "Group",
}


class ScimClientNoDataFoundException(Exception): ...


class ScimClientTooManyResultsException(Exception): ...


class ScimClientInvalidServerResponseException(Exception):
    """Raised when a server response isn't even a valid SCIM error."""


class ScimClient:
    """
    SCIM client wrapper.

    Wrapper class around a SCIM client that configures it with our settings.

    The underlying client is configured with check_response_content_type=False
    and check_response_payload=False, which means on the one hand that
    responses are not validated, but also that they return raw dicts parsed
    from JSON rather than objects inheriting from scim2_models.Resource.
    """

    def __init__(self, auth: Auth | None, settings: ScimConsumerSettings):
        self.settings = settings
        self.auth = auth
        self._scim_client: SyncSCIMClient | None = None

    def _create_client(self) -> SyncSCIMClient:
        """
        Returns a connected SyncSCIMClient instance.

        Checks discovery (/ResourceTypes, /Schemas, /ServiceProviderConfig), filter
        search, the configured auth scheme, and the User (and, if group sync is
        enabled, Group) resource type.
        """
        logger.info("Connect to SCIM server ({}).", self.settings.scim_server_base_url)

        http_client, scim_client = self._make_clients()

        try:
            scim_client.discover(schemas=True, service_provider_config=False, resource_types=True)
        except RequestNetworkException:
            # Let task processing retry instead of caching incomplete capabilities.
            http_client.close()
            raise
        except SCIMClientException as e:
            logger.warning(
                "Scim server does not support ResourceType/Schema discovery.",
                capability="discovery",
                error=str(e),
            )

        try:
            scim_client.discover(schemas=False, service_provider_config=True, resource_types=False)
        except RequestNetworkException:
            http_client.close()
            raise
        except SCIMClientException as e:
            logger.warning(
                "Scim server does not support ServiceProviderConfig discovery.",
                capability="service_provider_config",
                error=str(e),
            )

        service_provider_config = scim_client.provider.config

        if service_provider_config is None:
            logger.warning(
                "Scim server did not return a ServiceProviderConfig.",
                capability="service_provider_config",
            )
        elif not (service_provider_config.filter and service_provider_config.filter.supported):
            logger.warning(
                "Scim server does not support attribute filtering, required for externalId lookups.",
                capability="filter",
            )

        self._verify_auth_scheme(service_provider_config)

        if scim_client.get_resource_model("User") is None:
            logger.warning("Scim server does not support User resource.", capability="User resource type")

        if scim_client.get_resource_model("Group") is None:
            if self.settings.group_sync_enabled:
                logger.warning("Scim server does not support Group resource.", capability="Group resource type")
            else:
                logger.info("Scim server does not support Group resource. Continuing in users-only mode.")

        return scim_client

    def _make_clients(self) -> tuple[Client, SyncSCIMClient]:
        http_client = Client(
            auth=self.auth,
            base_url=str(self.settings.scim_server_base_url),
            headers={
                "Accept": "application/scim+json",
                "Content-Type": "application/scim+json",
            },
        )
        scim_client = SyncSCIMClient(
            client=http_client, check_response_content_type=False, check_response_payload=False
        )
        return http_client, scim_client

    def _verify_auth_scheme(self, service_provider_config: ServiceProviderConfig | None) -> None:
        """
        Checks the configured auth method is among the server's advertised
        authenticationSchemes. Only logs a warning when it isn't, or can't be checked.
        """
        required_scheme_types = required_scim_scheme_types(self.settings.scim_auth_method)
        if not required_scheme_types:
            return

        if service_provider_config is None:
            logger.warning(
                "Scim server did not return a ServiceProviderConfig; "
                "cannot verify it supports the configured authentication method.",
                capability="authentication_schemes",
                configured_auth_method=self.settings.scim_auth_method,
            )
            return

        advertised_scheme_types = {
            scheme.type for scheme in (service_provider_config.authentication_schemes or []) if scheme.type
        }
        if advertised_scheme_types.isdisjoint(required_scheme_types):
            logger.warning(
                "Scim server does not advertise an authentication scheme for the configured auth method.",
                capability="authentication_schemes",
                configured_auth_method=self.settings.scim_auth_method,
                required_scheme_types=[scheme_type.value for scheme_type in required_scheme_types],
                advertised_scheme_types=sorted(scheme_type.value for scheme_type in advertised_scheme_types),
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

        response = self.get_client().create(target=resource)

        logger.debug("Response:\n{}", cust_pformat(response))
        self._raise_for_response_error(response)

    def update_resource(self, resource: Resource) -> None:
        """
        Updates one SCIM resource.

        Fetches the current data from the SCIM server via the external_id (univentionObjectIdentifier),
        merges the data and write it back to the SCIM server.
        """
        logger.info("Update SCIM resource {}", resource.external_id)
        logger.debug("Resource data:\n{}", cust_pformat(resource.model_dump()))

        response = self.get_client().replace(target=resource)

        logger.debug("Response:\n{}", cust_pformat(response))
        self._raise_for_response_error(response)

    def delete_resource(self, id: str, resource_model: type[Resource]) -> None:
        """
        Deletes a SCIM resource by id.
        """
        response = self.get_client().delete(target=resource_model, id=id)

        logger.debug("Delete response:\n{}", cust_pformat(response))
        self._raise_for_response_error(response)

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
        response = self.get_client().query(target=resource_model, query_parameters=search_request)

        logger.debug("SCIM query response:\n{}", response)
        self._raise_for_response_error(response)

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

    def _raise_for_response_error(self, response: object) -> None:
        """
        Raise an exception if the response looks like an error.

        Normally, the scim2_client library would do this for us, but since
        we're using check_response_payload=False it skips this check.
        """
        if isinstance(response, dict):
            if response.get("schemas") == [Error.__schema__]:
                try:
                    error = Error.model_validate(response)
                except Exception as e:
                    raise ScimClientInvalidServerResponseException(
                        "error parsing response that looked like a SCIM error"
                    ) from e
                raise SCIMException.from_error(error)
        elif isinstance(response, Resource):
            logger.warning("Was expecting raw JSON response, but found already-parsed SCIM resource.")
        elif isinstance(response, Error):
            logger.warning("Was expecting raw JSON response, but found already-parsed SCIM error.")
            raise SCIMException.from_error(response)
        elif response is not None:
            # None can be returned on success.
            raise ScimClientInvalidServerResponseException(f"invalid SCIM payload {response}")


class WireComScimClient(ScimClient):
    """
    SCIM client with quirks for wire.com.

    wire.com's SCIM server is not standard-compliant in a few ways that would
    break our client. This class implements workarounds.
    """

    def __init__(self, auth: Auth | None, settings: ScimConsumerSettings):
        if not _is_wire_com_base_url(settings.scim_server_base_url):
            logger.warning(
                "Using a wire.com-specific client for non-wire.com base URL.", base_url=settings.scim_server_base_url
            )
        super().__init__(auth, settings)

    def _make_clients(self) -> tuple[Client, SyncSCIMClient]:
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

        http_client = Client(
            auth=self.auth,
            base_url=str(self.settings.scim_server_base_url),
            headers={
                "Accept": "application/scim+json",
                "Content-Type": "application/scim+json",
            },
            event_hooks={"response": [manipulate_response_to_be_RFC_compliant]},
        )

        # wire.com's schema discovery is broken because their /ServiceProviderConfig endpoint returns an invalid schemas
        # array and extensions are missing from /Schemas. Provide the basic user and group models here explicitly so the
        # client skips schema discovery. Use a policy to keep any unknown attributes from their extensions.
        provider = ScimProvider(models=[User, Group], policy=ScimPolicy(unknown=ScimPolicy.Unknown.keep))
        scim_client = SyncSCIMClient(
            client=http_client, check_response_content_type=False, check_response_payload=False, provider=provider
        )
        return http_client, scim_client


def make_scim_client(auth: Auth | None, settings: ScimConsumerSettings) -> ScimClient:
    """
    Create a SCIM client.

    Returns the correct subclass based on base URL.
    """
    client_class = ScimClient
    if _is_wire_com_base_url(settings.scim_server_base_url):
        client_class = WireComScimClient
    return client_class(auth, settings)


def _is_wire_com_base_url(url: HttpUrl) -> bool:
    return bool(url.host and url.host.endswith("wire.com"))
