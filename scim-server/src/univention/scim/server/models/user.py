# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

from typing import Annotated

from pydantic import Field
from scim2_models import (
    AnyExtension,
    Email as ScimEmail,
    Name as ScimName,
    Required,
    User as ScimUser,
)


class Email(ScimEmail):
    # original type is an enum and only allows "work", "home" and "other" loosen this
    # restriction to allow mapping any type, currently we use mailbox and alias for
    # some special mail addresses in UDM
    type: str | None = Field(None, examples=["work", "home", "other", "mailbox", "alias"])


class Name(ScimName):
    # UDM requires a lastname so mark it as required also in the scim model
    family_name: Annotated[str | None, Required.true] = None


class User(ScimUser[AnyExtension]):
    name: Annotated[Name | ScimName | None, Required.true] = None
    emails: list[Email | ScimEmail] | None = None

    # FIXME: Remove when empty passwords are handled by UDM
    ignore_password_policy: Annotated[bool, Field(exclude=True)] = False
