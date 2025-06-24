# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

from typing import Any

from scim2_models import Address, PhoneNumber, Role, X509Certificate

from univention.scim.server.models.user import Email, Name
from univention.scim.transformation.udm2scim import UdmToScimMapper


def test_map_emails(udm2scim_mapper: UdmToScimMapper) -> None:
    props = {
        "mailPrimaryAddress": "test@test.de",
        "mailAlternativeAddress": ["test.alt@test.de"],
        "e-mail": ["test.two@test.de"],
    }
    expected_emails = [
        Email(value="test@test.de", type="mailbox", primary=False),
        Email(value="test.alt@test.de", type="alias", primary=False),
        Email(value="test.two@test.de", type="other", primary=False),
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
        PhoneNumber(value="1111111", type="work"),
        PhoneNumber(value="2222222", type="mobile"),
        PhoneNumber(value="3333333", type="home"),
        PhoneNumber(value="4444444", type="pager"),
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
        Address(
            formatted="Beispielstraße 4711\nMusterhausen 12345\nNRW DE",
            street_address="Beispielstraße 4711",
            locality="Musterhausen",
            postal_code="12345",
            country="DE",
            region="NRW",
            type="work",
        ),
        Address(
            formatted="Beispielstraße 0815\nMusterhausen 12345\nNRW DE",
            street_address="Beispielstraße 0815",
            locality="Musterhausen",
            postal_code="12345",
            type="home",
        ),
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
        Role(value="testRoleDirect", type="guardian-direct"),
        Role(value="testRoleIndirect", type="guardian-indirect"),
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
    expected_name = Name(
        given_name="Test",
        family_name="User",
        formatted="Test User",
    )
    name = udm2scim_mapper._map_username(props)

    assert name == expected_name


def test_map_username_none(udm2scim_mapper: UdmToScimMapper) -> None:
    props = {"firstname": None, "lastname": None}
    name = udm2scim_mapper._map_username(props)

    assert name is None


def test_map_certificates(udm2scim_mapper: UdmToScimMapper) -> None:
    props = {"userCertificate": "###################", "certificateSubjectCommonName": "testCertificate"}
    expected_certificates = [X509Certificate(value="###################", display="testCertificate")]
    certificates = udm2scim_mapper._map_certificates(props)

    assert certificates == expected_certificates


def test_map_certificates_none(udm2scim_mapper: UdmToScimMapper) -> None:
    props = {"userCertificate": None, "certificateSubjectCommonName": None}
    certificates = udm2scim_mapper._map_certificates(props)

    assert certificates is None
