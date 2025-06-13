# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

import base64
import time
from datetime import UTC, datetime

import pytest
from faker import Faker
from fastapi.testclient import TestClient

from helpers.udm_client import MockUdm
from univention.scim.server.models.types import UserWithExtensions


# Always use the mock UDM for mapping tests to allow easy adding of groups or users
# for the invalid members test it is required because real UDM does not allow to add
# a invalid user to a group
@pytest.fixture
def force_mock() -> bool:
    return True


udm_properties = {
    "username": "test_user",
    "description": "This is a test user",
    "disabled": True,
    "displayName": "Test User",
    "title": "CEO",
    "employeeNumber": "99999",
    "employeeType": "Cheffe",
    "preferredLanguage": "EN",
    "firstname": "Jane",
    "lastname": "Doe",
    "mailPrimaryAddress": "primary@testmail.org",
    "mailAlternativeAddress": [
        "alternative2@testmail.org",
        "alternative42@testmail.org",
    ],
    "e-mail": [
        "other5@testmail.org",
        "other1337@testmail.org",
    ],
    "phone": ["1234", "2345"],
    "mobileTelephoneNumber": ["3456", "4567"],
    "homeTelephoneNumber": ["5678", "6789"],
    "pagerTelephoneNumber": ["9876", "8765"],
    "street": "The Univention Way 1",
    "city": "Uni",
    "postcode": "11111",
    "country": "Germany",
    "state": "TheLand",
    "homePostalAddress": [{"street": "Home Stree 42", "city": "Home", "zipcode": "22222"}],
    "userCertificate": base64.b64encode(b"data").decode("utf-8"),
    "certificateSubjectCommonName": "Test User cert",
    "guardianRoles": ["Role1", "Role2"],
    "guardianInheritedRoles": ["InheritedRole1", "InheritedRole2"],
    "PasswordRecoveryEmail": "recovery@testmail.org",
    "primaryOrgUnit": "Sales",
    "secondaryOrgUnits": ["Marketing", "CustomerService"],
}

scim_schema = {
    "schemas": [
        "urn:ietf:params:scim:schemas:core:2.0:User",
        "urn:ietf:params:scim:schemas:extension:enterprise:2.0:User",
        "urn:ietf:params:scim:schemas:extension:Univention:1.0:User",
        "urn:ietf:params:scim:schemas:extension:DapUser:2.0:User",
    ],
    "userName": "test_user",
    "name": {"formatted": "Jane Doe", "familyName": "Doe", "givenName": "Jane"},
    "displayName": "Test User",
    "title": "CEO",
    "userType": "Cheffe",
    "preferredLanguage": "EN",
    "active": False,
    "emails": [
        {"type": "mailbox", "primary": False, "value": "primary@testmail.org"},
        {"type": "alias", "primary": False, "value": "alternative2@testmail.org"},
        {"type": "alias", "primary": False, "value": "alternative42@testmail.org"},
        {"type": "other", "primary": False, "value": "other5@testmail.org"},
        {"type": "other", "primary": False, "value": "other1337@testmail.org"},
    ],
    "phoneNumbers": [
        {"type": "work", "value": "1234"},
        {"type": "work", "value": "2345"},
        {"type": "mobile", "value": "3456"},
        {"type": "mobile", "value": "4567"},
        {"type": "home", "value": "5678"},
        {"type": "home", "value": "6789"},
        {"type": "pager", "value": "9876"},
        {"type": "pager", "value": "8765"},
    ],
    "addresses": [
        {
            "type": "work",
            "formatted": "The Univention Way 1\nUni 11111\nTheLand Germany",
            "streetAddress": "The Univention Way 1",
            "locality": "Uni",
            "region": "TheLand",
            "postalCode": "11111",
            "country": "Germany",
        },
        {
            "type": "home",
            "streetAddress": "Home Stree 42",
            "locality": "Home",
            "postalCode": "22222",
            "formatted": "Home Stree 42\nHome 22222",
        },
    ],
    "roles": [
        {"type": "guardian-direct", "value": "Role1"},
        {"type": "guardian-direct", "value": "Role2"},
        {"type": "guardian-indirect", "value": "InheritedRole1"},
        {"type": "guardian-indirect", "value": "InheritedRole2"},
    ],
    "x509Certificates": [
        {
            "display": "Test User cert",
            "value": base64.b64encode(b"data").decode("utf-8"),
        },
    ],
    "urn:ietf:params:scim:schemas:extension:enterprise:2.0:User": {
        "employeeNumber": "99999",
    },
    "urn:ietf:params:scim:schemas:extension:Univention:1.0:User": {
        "description": "This is a test user",
        "passwordRecoveryEmail": "recovery@testmail.org",
    },
    "urn:ietf:params:scim:schemas:extension:DapUser:2.0:User": {
        "primaryOrgUnit": "Sales",
        "secondaryOrgUnits": ["Marketing", "CustomerService"],
    },
}


def test_get_user_mapping(udm_client: MockUdm, client: TestClient) -> None:
    fake = Faker()

    user = udm_client.add_raw_user(
        {
            **udm_properties,
            "createTimestamp": int(time.time()),
            "modifyTimestamp": int(time.time()),
            "univentionObjectIdentifier": fake.uuid4(),
            "testExternalId": fake.uuid4(),
        }
    )

    create_date_time = datetime.fromtimestamp(user.properties["createTimestamp"], tz=UTC)
    modify_date_time = datetime.fromtimestamp(user.properties["modifyTimestamp"], tz=UTC)
    expected_data = {
        **scim_schema,
        "id": user.properties["univentionObjectIdentifier"],
        "externalId": user.properties["testExternalId"],
        "meta": {
            "resourceType": "User",
            "created": f"{create_date_time.replace(microsecond=0, tzinfo=None).isoformat()}Z",
            "lastModified": f"{modify_date_time.replace(microsecond=0, tzinfo=None).isoformat()}Z",
            "location": f"https://scim.unit.test/scim/v2/Users/{user.properties['univentionObjectIdentifier']}",
            "version": "1.0",
        },
    }

    # Get the user
    response = client.get(f"/scim/v2/Users/{user.properties['univentionObjectIdentifier']}")

    assert response.status_code == 200
    assert expected_data == response.json()


def test_create_user_mapping(udm_client: MockUdm, client: TestClient) -> None:
    fake = Faker()

    test_user = UserWithExtensions.model_validate({**scim_schema, "externalId": fake.uuid4()})

    response = client.post("/scim/v2/Users", json=test_user.model_dump(by_alias=True, exclude_none=True))
    assert response.status_code == 201
    response_data = response.json()

    print(response_data)
    expected_properties = {
        **udm_properties,
        "univentionObjectIdentifier": response_data["id"],
        "testExternalId": response_data["externalId"],
    }

    created_user = next(
        x.open()
        for x in udm_client.users.values()
        if x.open().properties["univentionObjectIdentifier"] == response_data["id"]
    )
    assert created_user is not None
    # password is auto generated so just check if it is there
    assert "password" in created_user.properties
    del created_user.properties["password"]
    assert expected_properties == created_user.properties
