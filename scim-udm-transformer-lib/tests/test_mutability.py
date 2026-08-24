# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2026 Univention GmbH
"""Attributes the target declares `readOnly` are not sent in a write request.

Uses a singular complex attribute so that only mutability, and not name-based
filtering, decides whether the sub-attribute survives.
"""

from scim2_models import Attribute, Mutability, Resource, Schema

from univention.scim.transformation.udm2scim import UdmToScimMapper, supported_attribute_names


def _string(name: str, **kwargs: object) -> Attribute:
    return Attribute(name=name, type=Attribute.Type.string, multi_valued=False, **kwargs)


def test_read_only_sub_attribute_is_not_sent() -> None:
    """`name.formatted` is declared readOnly, so the mapped user omits it."""
    schema = Schema(
        id="urn:ietf:params:scim:schemas:core:2.0:User",
        name="User",
        attributes=[
            _string("userName"),
            Attribute(
                name="name",
                type=Attribute.Type.complex,
                multi_valued=False,
                sub_attributes=[_string("givenName"), _string("formatted", mutability=Mutability.read_only)],
            ),
        ],
    )
    resource_model = Resource.from_schema(schema)
    mapper = UdmToScimMapper(user_type=resource_model, supported_attributes=supported_attribute_names(resource_model))
    udm_user = type(
        "Obj",
        (object,),
        {"dn": "cn=test", "properties": {"univentionObjectIdentifier": "u1", "firstname": "Jane", "lastname": "Doe"}},
    )()

    user = mapper.map_user(udm_user)

    assert "formatted" not in user.model_dump(exclude_none=True)["name"]


def test_immutable_sub_attribute_is_sent_on_create_but_not_on_update() -> None:
    """`name.formatted` is declared immutable: settable at creation, not on update."""
    schema = Schema(
        id="urn:ietf:params:scim:schemas:core:2.0:User",
        name="User",
        attributes=[
            _string("userName"),
            Attribute(
                name="name",
                type=Attribute.Type.complex,
                multi_valued=False,
                sub_attributes=[_string("givenName"), _string("formatted", mutability=Mutability.immutable)],
            ),
        ],
    )
    resource_model = Resource.from_schema(schema)
    udm_user = type(
        "Obj",
        (object,),
        {"dn": "cn=test", "properties": {"univentionObjectIdentifier": "u1", "firstname": "Jane", "lastname": "Doe"}},
    )()

    for_create = UdmToScimMapper(
        user_type=resource_model, supported_attributes=supported_attribute_names(resource_model)
    ).map_user(udm_user)
    for_update = UdmToScimMapper(
        user_type=resource_model,
        supported_attributes=supported_attribute_names(resource_model, exclude_immutable=True),
    ).map_user(udm_user)

    assert "formatted" in for_create.model_dump(exclude_none=True)["name"]
    assert "formatted" not in for_update.model_dump(exclude_none=True)["name"]
