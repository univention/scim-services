import random
import string
import urllib
import uuid
from pprint import pprint

import pytest
import pytest_asyncio
import requests
from univention.provisioning.consumer.api import (
    MessageHandler,
    MessageHandlerSettings,
    ProvisioningConsumerClient,
    ProvisioningConsumerClientSettings,
)

from univention.scim.consumer.message_handler import handle_udm_message


@pytest.fixture
def provisioning_subscription():
    subscription_data = {
        "name": "scim-consumer",
        "realms_topics": [{"realm": "udm", "topic": "users/user"}],
        "request_prefill": True,
        "password": "univention",
    }

    provisioning_base_url = "http://localhost:7777/v1/subscriptions"
    provisioning_username = "admin"
    provisioning_password = "provisioning"

    print("Create subscription.")
    response = requests.post(
        provisioning_base_url, json=subscription_data, auth=(provisioning_username, provisioning_password)
    )
    print(vars(response))

    yield

    print("Delete subscription.")
    requests.delete(f"{provisioning_base_url}/scim-consumer")


@pytest.fixture
def udm_user():
    def random_string_generator(str_size, allowed_chars):
        return "".join(random.choice(allowed_chars) for x in range(str_size))
    
    chars = string.ascii_letters
    size = 6
    random_string = random_string_generator(size, chars)

    return {
        "username": f"testuser.{random_string}",
        "firstname": "testuser",
        "lastname": random_string,
        "univentionObjectIdentifier": str(uuid.uuid4()),
        "password": "univention",
    }

@pytest.fixture
def create_udm_user(udm_user):
    
    udm_username = "cn=admin"
    udm_password = "univention"

    udm_url = "http://localhost:9979/udm/"
    url_users = urllib.parse.urljoin(udm_url, "users/user/")


    # base_dn = "dc=univention-organization,dc=intranet"
    # dn = f"uid={properties['username']},cn=users,{base_dn}"

    """Prepare requests to UDM REST API."""
    session = requests.Session()
    session.auth = (
        udm_username,
        udm_password,
    )
    session.headers["accept"] = "application/json"
    session.headers["content-type"] = "application/json"

    conn = session.post(url_users, json={"properties": udm_user})
    post_result = conn.json()
    pprint(conn)
    pprint(post_result)
    # new_dn = post_result["dn"]
    # new_uuid = post_result["uuid"]

    # conn = session.get(f"{url_users}{new_dn}")
    # result = conn.json()
    # pprint(result)


@pytest_asyncio.fixture
async def scim_consumer(provisioning_subscription, create_udm_user):
    pcc_settings = ProvisioningConsumerClientSettings(
        provisioning_api_base_url="http://localhost:7777/",
        provisioning_api_username="scim-consumer",
        provisioning_api_password="univention",
        log_level="INFO",
    )
    mh_settings = MessageHandlerSettings(max_acknowledgement_retries=1)

    async with ProvisioningConsumerClient(pcc_settings) as client:
        await MessageHandler(client, [handle_udm_message], mh_settings, message_limit=1).run()