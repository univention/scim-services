# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

from typing import NamedTuple

from httpx import Client
from icecream import ic
from loguru import logger
from scim2_client.engines.httpx import SyncSCIMClient
from scim2_models import Address, Email, Error, Group, Name, PhoneNumber, SearchRequest, User, X509Certificate


class Config(NamedTuple):
    base_url: str
    bearar_token: str


def get_config() -> Config:
    base_url = "http://localhost:8888/"
    bearar_token = ""

    return Config(
        base_url=base_url,
        bearar_token=bearar_token,
    )

def get_client(config: Config):
    # client = Client(base_url=config.base_url, headers={"Authorization": f"Bearer {config.bearar_token}"})
    client = Client(base_url=config.base_url)
    scim = SyncSCIMClient(client)
    # Create resources
    scim.discover()
    
    return scim

# Query resources
# user = scim.query(User, "2819c223-7f76-453a-919d-413861904646")
# assert user.user_name == "bjensen@example.com"
# assert user.meta.last_updated == datetime.datetime(2024, 4, 13, 12, 0, 0, tzinfo=datetime.timezone.utc)

# Update resources
# user.display_name = "Babs Jensen"
# user = scim.replace(user)
# assert user.display_name == "Babs Jensen"
# assert user.meta.last_updated == datetime.datetime(2024, 4, 13, 12, 0, 30, tzinfo=datetime.timezone.utc)

def create_user(scim_client: SyncSCIMClient, user: User):
    
    # User = scim_client.get_resource_model("User")
    # request = User(user_name=user.user_name)
    logger.debug("Payload:\n{}", ic.format(user.model_dump()))
    response = scim_client.create(user.model_dump())
    logger.debug("Response:\n{}", ic.format(vars(response)))
    

def get_user_by_username(scim_client: SyncSCIMClient, username: str) -> User:
    search_request = SearchRequest(filter=f'userName sw "{username}"')
    response = scim_client.query(search_request=search_request)

    if response.total_results == 1:
        return response.resources[0]

    else:
        raise Exception("To many results!")
    