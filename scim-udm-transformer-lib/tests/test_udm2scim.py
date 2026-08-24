# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

from typing import Any

from scim2_models import Attribute, EnterpriseUser, Extension, Schema, User as ScimUser

from univention.scim.server.models.extensions.customer1_user import Customer1User
from univention.scim.server.models.extensions.univention_group import UniventionGroup
from univention.scim.server.models.extensions.univention_user import UniventionUser
from univention.scim.server.models.group import Group
from univention.scim.server.models.user import User
from univention.scim.transformation.udm2scim import UdmToScimMapper, supported_attribute_names


def _udm_object(properties: dict[str, Any], dn: str = "cn=test,dc=example,dc=com") -> Any:
    return type("Obj", (object,), {"dn": dn, "properties": properties})()


def test_map_emails(udm2scim_mapper: UdmToScimMapper) -> None:
    props = {
        "mailPrimaryAddress": "test@test.de",
        "mailAlternativeAddress": ["test.alt@test.de"],
        "e-mail": ["test.two@test.de"],
    }
    expected_emails = [
        {"value": "test@test.de", "type": "mailbox", "primary": False},
        {"value": "test.alt@test.de", "type": "alias", "primary": False},
        {"value": "test.two@test.de", "type": "other", "primary": False},
    ]
    emails = udm2scim_mapper._map_emails(props)

    assert emails == expected_emails


def test_map_emails_empty(udm2scim_mapper: UdmToScimMapper) -> None:
    props: dict[str, Any | None] = {"mailPrimaryAddress": None, "mailAlternativeAddress": [], "e-mail": []}
    emails = udm2scim_mapper._map_emails(props)

    assert emails == []


def test_map_emails_none(udm2scim_mapper: UdmToScimMapper) -> None:
    props: dict[str, Any | None] = {
        "mailPrimaryAddress": None,
        "mailAlternativeAddress": None,
        "e-mail": None,
    }
    emails = udm2scim_mapper._map_emails(props)

    assert emails is None


def test_map_phone_numbers(udm2scim_mapper: UdmToScimMapper) -> None:
    props = {
        "phone": ["1111111"],
        "mobileTelephoneNumber": ["2222222"],
        "homeTelephoneNumber": ["3333333"],
        "pagerTelephoneNumber": ["4444444"],
    }
    expected_phones = [
        {"value": "1111111", "type": "work"},
        {"value": "2222222", "type": "mobile"},
        {"value": "3333333", "type": "home"},
        {"value": "4444444", "type": "pager"},
    ]
    phones = udm2scim_mapper._map_phone_numbers(props)

    assert phones == expected_phones


def test_map_phone_numbers_empty(udm2scim_mapper: UdmToScimMapper) -> None:
    props: dict[str, list[str] | None] = {
        "phone": [],
        "mobileTelephoneNumber": [],
        "homeTelephoneNumber": [],
        "pagerTelephoneNumber": [],
    }
    phones = udm2scim_mapper._map_phone_numbers(props)

    assert phones == []


def test_map_phone_numbers_none(udm2scim_mapper: UdmToScimMapper) -> None:
    props: dict[str, list[str] | None] = {
        "phone": None,
        "mobileTelephoneNumber": None,
        "homeTelephoneNumber": None,
        "pagerTelephoneNumber": None,
    }
    phones = udm2scim_mapper._map_phone_numbers(props)

    assert phones is None


def test_map_addresses(udm2scim_mapper: UdmToScimMapper) -> None:
    props = {
        "street": "Beispielstraße 4711",
        "city": "Musterhausen",
        "postcode": "12345",
        "country": "DE",
        "state": "NRW",
        "homePostalAddress": [
            {
                "street": "Beispielstraße 0815",
                "city": "Musterhausen",
                "zipcode": "12345",
                "country": "DE",
                "state": "NRW",
            }
        ],
    }
    expected_addresses = [
        {
            "formatted": "Beispielstraße 4711\nMusterhausen 12345\nNRW DE",
            "streetAddress": "Beispielstraße 4711",
            "locality": "Musterhausen",
            "postalCode": "12345",
            "country": "DE",
            "region": "NRW",
            "type": "work",
        },
        {
            "formatted": "Beispielstraße 0815\nMusterhausen 12345\nNRW DE",
            "streetAddress": "Beispielstraße 0815",
            "locality": "Musterhausen",
            "postalCode": "12345",
            "type": "home",
        },
    ]
    addresses = udm2scim_mapper._map_addresses(props)

    assert addresses == expected_addresses


def test_map_addresses_empty(udm2scim_mapper: UdmToScimMapper) -> None:
    props: dict[str, Any | None] = {
        "street": None,
        "city": None,
        "postcode": None,
        "country": None,
        "state": None,
        "homePostalAddress": [],
    }
    addresses = udm2scim_mapper._map_addresses(props)

    assert addresses == []


def test_map_addresses_none(udm2scim_mapper: UdmToScimMapper) -> None:
    props: dict[str, Any | None] = {
        "street": None,
        "city": None,
        "postcode": None,
        "country": None,
        "state": None,
        "homePostalAddress": None,
    }
    addresses = udm2scim_mapper._map_addresses(props)

    assert addresses is None


def test_map_roles(udm2scim_mapper: UdmToScimMapper) -> None:
    props = {"guardianRoles": ["testRoleDirect"], "guardianInheritedRoles": ["testRoleIndirect"]}
    expected_roles = [
        {"value": "testRoleDirect", "type": "guardian-direct"},
        {"value": "testRoleIndirect", "type": "guardian-indirect"},
    ]
    roles = udm2scim_mapper._map_roles(props)

    assert roles == expected_roles


def test_map_roles_empty(udm2scim_mapper: UdmToScimMapper) -> None:
    props: dict[str, list[str]] = {"guardianRoles": [], "guardianInheritedRoles": []}
    roles = udm2scim_mapper._map_roles(props)

    assert roles == []


def test_map_roles_none(udm2scim_mapper: UdmToScimMapper) -> None:
    props = {"guardianRoles": None, "guardianInheritedRoles": None}
    roles = udm2scim_mapper._map_roles(props)

    assert roles is None


def test_map_username(udm2scim_mapper: UdmToScimMapper) -> None:
    props = {"firstname": "Test", "lastname": "User"}
    expected_name = {
        "givenName": "Test",
        "familyName": "User",
        "formatted": "Test User",
    }
    name = udm2scim_mapper._map_username(props)

    assert name == expected_name


def test_map_username_none(udm2scim_mapper: UdmToScimMapper) -> None:
    props = {"firstname": None, "lastname": None}
    name = udm2scim_mapper._map_username(props)

    assert name is None


def test_map_certificates(udm2scim_mapper: UdmToScimMapper) -> None:
    props = {"userCertificate": "###################", "certificateSubjectCommonName": "testCertificate"}
    expected_certificates = [{"value": "###################", "display": "testCertificate"}]
    certificates = udm2scim_mapper._map_certificates(props)

    assert certificates == expected_certificates


def test_map_certificates_none(udm2scim_mapper: UdmToScimMapper) -> None:
    props = {"userCertificate": None, "certificateSubjectCommonName": None}
    certificates = udm2scim_mapper._map_certificates(props)

    assert certificates is None


def test_map_photos(udm2scim_mapper: UdmToScimMapper) -> None:
    props = {"jpegPhoto": "base64encodedimagedata"}
    expected_photos = [{"value": "data:image/jpeg;base64,base64encodedimagedata", "type": "photo"}]

    photos = udm2scim_mapper._map_photos(props)

    assert photos == expected_photos


def test_map_photos_none(udm2scim_mapper: UdmToScimMapper) -> None:
    props: dict[str, Any] = {"jpegPhoto": None}

    photos = udm2scim_mapper._map_photos(props)

    assert photos is None


def test_map_user_only_populates_extensions_the_type_was_parameterized_with() -> None:
    mapper = UdmToScimMapper(user_type=User[EnterpriseUser])
    udm_user = _udm_object(
        {
            "univentionObjectIdentifier": "some-uuid",
            "username": "jdoe",
            "employeeNumber": "12345",
            "description": "should not appear",
            "primaryOrgUnit": "should not appear either",
        }
    )

    user = mapper.map_user(udm_user)
    schemas = user.model_dump()["schemas"]

    assert EnterpriseUser.to_schema().id in schemas
    assert UniventionUser.to_schema().id not in schemas
    assert Customer1User.to_schema().id not in schemas
    assert user.EnterpriseUser.employee_number == "12345"


def test_map_user_with_multiple_parameterized_extensions() -> None:
    mapper = UdmToScimMapper(user_type=User[EnterpriseUser | UniventionUser | Customer1User])
    udm_user = _udm_object(
        {
            "univentionObjectIdentifier": "some-uuid",
            "username": "jdoe",
            "employeeNumber": "12345",
            "description": "a description",
            "primaryOrgUnit": "Sales",
        }
    )

    user = mapper.map_user(udm_user)
    schemas = user.model_dump()["schemas"]

    assert EnterpriseUser.to_schema().id in schemas
    assert UniventionUser.to_schema().id in schemas
    assert Customer1User.to_schema().id in schemas
    assert user.EnterpriseUser.employee_number == "12345"
    assert user.UniventionUser.description == "a description"
    assert user.Customer1User.primary_org_unit == "Sales"


def test_map_user_drops_attributes_not_in_supported_attributes() -> None:
    mapper = UdmToScimMapper(user_type=User, supported_attributes={"id", "externalId", "meta", "schemas"})
    udm_user = _udm_object(
        {
            "univentionObjectIdentifier": "some-uuid",
            "username": "jdoe",
            "displayName": "Jane Doe",
            "phone": ["12345"],
        }
    )

    user = mapper.map_user(udm_user)

    assert user.display_name is None
    assert user.phone_numbers is None
    assert user.id == "some-uuid"


def test_map_user_drops_extension_attributes_not_supported_by_the_extension_itself() -> None:
    partial_schema = Schema(
        id="urn:ietf:params:scim:schemas:extension:Univention:1.0:User",
        name="UniventionUser",
        attributes=[Attribute(name="description", type=Attribute.Type.string, multi_valued=False)],
    )
    partial_univention_user = Extension.from_schema(partial_schema)
    resource_model = ScimUser[partial_univention_user]

    mapper = UdmToScimMapper(user_type=resource_model, supported_attributes=supported_attribute_names(resource_model))
    udm_user = _udm_object(
        {
            "univentionObjectIdentifier": "some-uuid",
            "username": "jdoe",
            "description": "a description",
            "PasswordRecoveryEmail": "recovery@example.org",
        }
    )

    user = mapper.map_user(udm_user)
    extension_data = user.model_dump(exclude_none=True)["urn:ietf:params:scim:schemas:extension:Univention:1.0:User"]

    assert extension_data == {"description": "a description"}


def test_map_user_keeps_attributes_declared_with_different_case() -> None:
    mapper = UdmToScimMapper(user_type=User, supported_attributes={"id", "displayname", "PHONENUMBERS"})
    udm_user = _udm_object(
        {
            "univentionObjectIdentifier": "some-uuid",
            "username": "jdoe",
            "displayName": "Jane Doe",
            "phone": ["12345"],
        }
    )

    user = mapper.map_user(udm_user)

    assert user.display_name == "Jane Doe"
    assert user.phone_numbers is not None


def test_map_user_drops_unsupported_sub_attributes_of_a_complex_attribute() -> None:
    # A server may declare "name" without advertising the "formatted" sub-attribute.
    mapper = UdmToScimMapper(user_type=User, supported_attributes={"id", "name", "name.givenName", "name.familyName"})
    udm_user = _udm_object(
        {
            "univentionObjectIdentifier": "some-uuid",
            "username": "jdoe",
            "firstname": "Jane",
            "lastname": "Doe",
        }
    )

    user = mapper.map_user(udm_user)

    assert user.name.given_name == "Jane"
    assert user.name.family_name == "Doe"
    assert user.name.formatted is None


def test_map_user_keeps_attributes_when_supported_attributes_is_none() -> None:
    mapper = UdmToScimMapper(user_type=User)
    udm_user = _udm_object(
        {
            "univentionObjectIdentifier": "some-uuid",
            "username": "jdoe",
            "displayName": "Jane Doe",
            "phone": ["12345"],
        }
    )

    user = mapper.map_user(udm_user)

    assert user.display_name == "Jane Doe"
    assert user.phone_numbers is not None


def test_map_group_only_populates_extension_the_type_was_parameterized_with() -> None:
    mapper = UdmToScimMapper(group_type=Group)
    udm_group = _udm_object(
        {
            "univentionObjectIdentifier": "some-uuid",
            "name": "Test Group",
            "description": "should not appear",
            "guardianMemberRoles": ["admin"],
        }
    )

    group = mapper.map_group(udm_group)

    assert UniventionGroup.to_schema().id not in group.schemas
    assert group.display_name == "Test Group"


def test_map_group_with_univention_extension() -> None:
    mapper = UdmToScimMapper(group_type=Group[UniventionGroup])
    udm_group = _udm_object(
        {
            "univentionObjectIdentifier": "some-uuid",
            "name": "Test Group",
            "description": "a description",
            "guardianMemberRoles": ["admin"],
        }
    )

    group = mapper.map_group(udm_group)

    assert UniventionGroup.to_schema().id in group.model_dump()["schemas"]
    assert group.UniventionGroup.description == "a description"
    assert group.UniventionGroup.member_roles[0].value == "admin"


def test_map_group_drops_attributes_not_in_supported_attributes() -> None:
    mapper = UdmToScimMapper(group_type=Group, supported_attributes={"id", "externalId", "meta", "schemas"})
    udm_group = _udm_object({"univentionObjectIdentifier": "some-uuid", "name": "Test Group"})

    group = mapper.map_group(udm_group)

    assert group.display_name is None
    assert group.id == "some-uuid"
