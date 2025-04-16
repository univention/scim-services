# Mapping UDM <-> SCIM v2

[[_TOC_]]

## Notice

- This is work in progress!
- TODO: add column for UDM code reference
- TODO: add column for comments
- TODO: make table a separate CSV file that gets displayed inline in the Markdown page
- TODO: add columns to distinguish between an attribute being required at read and write time
- Dash (`-`) means attribute not available.
  - TODO: Investigate third party SCIM schema extensions that can be used to map UDM properties.
  - TODO: Create new schema extension for UDM properties that cannot be mapped to any existing SCIM schema.
- Slash (`/`) means no such structure (complex / nested attributes). Mappable sub-attributes may exist.
- `REQUIRED` means it must always be supplied or is always set (by the system).
- A lot of UDM properties with type `string` have a more specific type in UDM REST API.
  - TODO: Look at runtime OpenAPI schema
    or [UDM encoders](https://git.knut.univention.de/univention/ucs/-/blob/5.2-0/management/univention-directory-manager-modules/modules/univention/udm/modules/users_user.py#L45)
    and update `type` column.

## All Resources

- UDM: No specification. See UDM
  code → [../user.py](https://git.knut.univention.de/univention/ucs/-/blob/5.2-0/management/univention-directory-manager-modules/modules/univention/admin/handlers/users/user.py)
  and [../syntax.py](https://git.knut.univention.de/univention/ucs/-/blob/5.2-0/management/univention-directory-manager-modules/modules/univention/admin/syntax.py).
  - Attention: UDM `type=string`  usually has constraints.
    See [syntax.py](https://git.knut.univention.de/univention/ucs/-/blob/5.2-0/management/univention-directory-manager-modules/modules/univention/admin/syntax.py).
- SCIM: [RFC 7643 section "3. SCIM Resources"](https://datatracker.ietf.org/doc/html/rfc7643#section-3): Each SCIM
  resource is a JSON object that has the following components: Resource Type, "Schemas" Attribute, Common Attributes,
  Core Attributes, Extended Attributes.

| UDM REST API field                | avail    | type                 | SCIM attribute     | avail    | type            | RFC 7643          |
|-----------------------------------|----------|----------------------|--------------------|----------|-----------------|-------------------|
| -                                 | -        | -                    | schemas            | REQUIRED | list of strings | 3. SCIM Resources |
| uuid (entryUUID)                  | REQUIRED | string (UUID)        | -                  | -        | -               | -                 |
| univentionObjectIdentifier        | REQUIRED | UUID                 | id                 | REQUIRED | string (UUID)   | 3.1 Common Attrs  |
| *configurable*                    | optional | string               | externalId         | optional | string          | 3.1 Common Attrs  |
| /                                 | /        | /                    | meta               | REQUIRED | complex         | 3.1 Common Attrs  |
| objectType (univentionObjectType) | REQUIRED | string               | meta .resourceType | REQUIRED | string          |                   |
| createTimestamp                   | optional | string (*2)          | meta. created      | REQUIRED | DateTime        |                   |
| modifyTimestamp                   | optional | string (*2)          | meta. lastModified | REQUIRED | DateTime        |                   |
| uri                               | REQUIRED | URI                  | meta. location     | REQUIRED | URI             |                   |
| HTTP ETag header                  | optional | string (ETag *1 ?)   | meta. version      | optional | string (*1)     |                   |
| dn                                | optional | string (DN)          | - **TODO**         | -        | -               |                   |
| id (RDN, e.g. cn / uid)           | REQUIRED | string               | -                  | -        | -               |                   |
| options                           | REQUIRED | complex              | -                  | -        | -               |                   |
| options .posix, .samba, etc       | optional | boolean              | -                  | -        | -               |                   |
| policies                          | REQUIRED | complex              | -                  | -        | -               |                   |
| policies .policies/umc, etc       | optional | list of strings (DN) | -                  | -        | -               |                   |
| position                          | REQUIRED | string (DN)          | -                  | -        | -               |                   |
| properties                        | REQUIRED | complex              | /                  | /        | /               |                   |
| superordinate                     | optional | string (DN)          | -                  | -        | -               |                   |

- (*1) ETag, [RFC7232](https://datatracker.ietf.org/doc/html/rfc7232) sections 2.1 and 2.3.
- (*2) [Generalized Time, RFC 4517](https://datatracker.ietf.org/doc/html/rfc4517#section-3.3.13)

## Users

- UDM: No specification. See UDM
  code → [../user.py](https://git.knut.univention.de/univention/ucs/-/blob/5.2-0/management/univention-directory-manager-modules/modules/univention/admin/handlers/users/user.py)
  and [../syntax.py](https://git.knut.univention.de/univention/ucs/-/blob/5.2-0/management/univention-directory-manager-modules/modules/univention/admin/syntax.py).
  Password recovery properties are created
  in [a join script](https://git.knut.univention.de/univention/ucs/-/blob/5.2-0/management/univention-self-service/35univention-self-service-passwordreset-umc.inst?ref_type=heads#L102).
- SCIM: [RFC 7643 4.1 "User" Resource Schema](https://datatracker.ietf.org/doc/html/rfc7643#section-4.1)
  - [4.1.1 Singular Attributes](https://datatracker.ietf.org/doc/html/rfc7643#section-4.1.1)
  - [4.1.2 Multi-Valued Attributes](https://datatracker.ietf.org/doc/html/rfc7643#section-4.1.2)

| UDM property                                       | avail    | type                     | SCIM attribute                             | avail    | type                                  | RFC 7643 |
|----------------------------------------------------|----------|--------------------------|--------------------------------------------|----------|---------------------------------------|----------|
| accountActivationDate                              | optional | string (complex)         | -                                          | -        | -                                     |          |
| homePostalAddress                                  | optional | list of string (complex) | addresses                                  | optional | list of complex                       | 4.1.2    |
| -                                                  | -        | -                        | addresses. formatted                       | optional | string                                |          |
| street                                             | optional | string                   | addresses. streetAddress                   | optional | string                                |          |
| city                                               | optional | string                   | addresses. locality                        | optional | string                                |          |
| -                                                  | -        | -                        | addresses. region                          | optional | string                                |          |
| postcode                                           | optional | string                   | addresses. postalCode                      | optional | string                                |          |
| country                                            | optional | string                   | addresses. country                         | optional | string (*3)                           |          |
| -                                                  | -        | -                        | addresses. type                            | optional | string ("work", "home", "other")      |          |
| birthday                                           | optional | string                   | -                                          | -        | -                                     |          |
| departmentNumber                                   | optional | list of string           | -> Enterprise User -> department           | optional | string                                | 4.3      |
| DeregistrationTimestamp                            | optional | string                   | -                                          | -        | -                                     |          |
| DeregisteredThroughSelfService                     | optional | boolean                  |                                            |          |                                       |          |
| description                                        | optional | string                   | -                                          | -        | -                                     |          |
| disabled                                           |          |                          | active                                     | optional | boolean                               | 4.1.1    |
| displayName                                        |          | string                   | displayName _and/or_ name. formatted       | optional | string                                | 4.1.1    |
| /                                                  | /        | /                        | emails                                     | optional | complex                               | 4.1.2    |
| e-mail, mailPrimaryAddress, mailAlternativeAddress | optional | list of strings, string  | emails. value                              | optional | string (*4)                           |          |
| -                                                  | -        | -                        | emails. display                            | optional | string                                |          |
| -                                                  | -        | -                        | emails. type                               | optional | string ("work", "home", "other", ...) |          |
| - (→ mailPrimaryAddress)                           | optional | string                   | emails. primary                            | optional | boolean                               |          |
| employeeNumber                                     | optional | string                   | -> Enterprise User -> employeeNumber       | optional | string                                | 4.3      |
| employeeType                                       | optional |                          | userType                                   | optional | string                                | 4.1.1    |
| /                                                  | /        | /                        | entitlements                               | optional | list of complex                       | 4.1.2    |
| -                                                  | -        | -                        | entitlements. value                        | optional | string                                |          |
| -                                                  | -        | -                        | entitlements. display                      | optional | string                                |          |
| -                                                  | -        | -                        | entitlements. type                         | optional | string                                |          |
| -                                                  | -        | -                        | entitlements. primary                      | optional | boolean                               |          |
| firstname                                          |          | string                   | name. givenName                            | optional | string                                | 4.1.1    |
| gecos                                              | optional | string                   | displayName or name. formatted ?           | optional | string                                |          |
| gidNumber                                          | REQUIRED | int                      | -                                          | -        | -                                     |          |
| groups                                             | REQUIRED | list of strings (DN)     | -                                          | -        | -                                     |          |
| /                                                  | /        | /                        | groups                                     | optional | list of complex                       | 4.1.2    |
| $group. entryUUID                                  | -        | -                        | groups. value                              | optional | string (UUID)                         |          |
| -                                                  | -        | -                        | groups. $ref                               | optional | URI                                   |          |
| $group. description                                | optional | string                   | groups. display                            | optional | string                                |          |
| -                                                  | -        | -                        | groups. type                               | optional | string ("direct", "indirect")         |          |
| guardianRoles                                      | optional | list of strings          | -                                          | -        | -                                     |          |
| guardianInheritedRoles                             | optional | list of strings          | -                                          | -        | -                                     |          |
| jpegPhoto                                          | optional | string                   | - (→ )                                     |          |                                       |          |
| homeShare                                          | optional | string (DN)              | -                                          | -        | -                                     |          |
| homeSharePath                                      | optional | string                   | -                                          | -        | -                                     |          |
| homeTelephoneNumber                                | optional | list of strings          |                                            |          |                                       |          |
| homedrive                                          | optional | string                   | -                                          | -        | -                                     |          |
| /                                                  | /        | /                        | ims                                        | optional | list of complex                       | 4.1.2    |
| -                                                  | -        | -                        | ims. value                                 | optional | string                                |          |
|                                                    |          |                          | ims. display                               | optional | string                                |          |
| -                                                  | -        | -                        | ims. type                                  | optional | string (*6)                           |          |
| -                                                  | -        | -                        | ims. primary                               | optional | boolean                               |          |
| jpegPhoto                                          | optional | string                   | - (→ photos)                               | -        | -                                     |          |
| -                                                  | -        | -                        | locale                                     | optional | string                                | 4.1.1    |
| lastname                                           | REQUIRED | string                   | name. familyName                           | optional | string                                | 4.1.1    |
| locked                                             |          | boolean                  | -                                          | -        | -                                     |          |
| lockedTime                                         |          | string                   | -                                          | -        | -                                     |          |
| mailAlternativeAddress                             | optional | list of strings          | → emails. value + emails. type             | optional | string + boolean                      |          |
| mailForwardAddress                                 | optional | list of strings          | -                                          | -        | -                                     |          |
| mailForwardCopyToSelf                              | optional | string                   | -                                          | -        | -                                     |          |
| mailHomeServer                                     | optional | string                   | -                                          | -        | -                                     |          |
| mailPrimaryAddress                                 | optional | string                   | → emails. value + emails. type             | optional | string + boolean                      | 4.1.2    |
| mailUserQuota (where is this defined?)             | optional | string (int)             | -                                          | -        | -                                     |          |
| -                                                  | -        | -                        | name. middleName                           | optional | string                                | 4.1.1    |
| mobileTelephoneNumber                              | optional | list of strings          | phoneNumbers. value _AND_ .type=mobile     | optional | string + string                       | 4.1.1    |
| /                                                  | /        | /                        | name (6 sub-attrs)                         | optional | complex                               | 4.1.1    |
| -                                                  | -        | -                        | name. honorificPrefix                      | optional | string                                | 4.1.1    |
| -                                                  | -        | -                        | name. honorificSuffix                      | optional | string                                | 4.1.1    |
| -                                                  | -        | -                        | nickName                                   | optional | string                                | 4.1.1    |
| objectFlag                                         |          | list of ???              | -                                          | -        | -                                     |          |
| organisation                                       | optional |                          | -> Enterprise User -> organization         | optional | string                                | 4.3      |
| overridePWHistory                                  | optional |                          | -                                          | -        | -                                     |          |
| overridePWLength                                   | optional |                          | -                                          | -        | -                                     |          |
| pagerTelephoneNumber                               | optional | list of strings          | phoneNumbers. value _AND_ .type=pager      | -        | string + string                       |          |
| password                                           | optional | string                   | password                                   | optional | string                                | 4.1.1    |
| passwordexpiry                                     | optional | string                   | -                                          | -        | -                                     |          |
| PasswordRecoveryEmailVerified                      | optional | boolean                  | -                                          | -        | -                                     |          |
| PasswordRecoveryMobile                             | optional | string                   | -                                          | -        | -                                     |          |
| PasswordRecoveryEmail                              | optional | string                   | -                                          | -        | -                                     |          |
| /                                                  | /        | /                        | phoneNumbers                               | optional | list of complex                       | 4.1.2    |
| phone                                              | optional | list of string           | phoneNumbers. value                        | optional | string (*5)                           | 4.1.1    |
| -                                                  | -        | -                        | phoneNumbers. display                      | optional | string                                |          |
| -                                                  | -        | -                        | phoneNumbers. type                         | optional | string (*7)                           |          |
| -                                                  | -        | -                        | phoneNumbers. primary                      | optional | boolean                               |          |
| /                                                  | /        | /                        | photos                                     | optional | list of complex                       | 4.1.2    |
| -                                                  | -        | -                        | photos. value                              | optional | URI                                   |          |
| -                                                  | -        | -                        | photos. display                            | optional | string                                |          |
| -                                                  | -        | -                        | photos. type                               | optional | string ("photo", "thumbnail")         |          |
| -                                                  | -        | -                        | photos. primary                            | optional | boolean                               |          |
| preferredLanguage                                  | optional | string                   | preferredLanguage                          | optional | string                                |          |
| primaryGroup                                       | REQUIRED | string                   | -                                          | -        | -                                     |          |
| profilepath                                        | optional | string                   | -                                          | -        | -                                     |          |
| -                                                  | -        | -                        | profileUrl                                 | optional | URI                                   | 4.1.1    |
| pwdChangeNextLogin                                 | optional | boolean                  | -                                          | -        | -                                     |          |
| RegisteredThroughSelfService                       | optional | boolean                  | -                                          | -        | -                                     |          |
| /                                                  | /        | /                        | roles                                      | optional | list of complex                       | 4.1.2    |
| -                                                  | -        | -                        | roles. value                               | optional | string                                |          |
| -                                                  | -        | -                        | roles. display                             | optional | string                                |          |
| -                                                  | -        | -                        | roles. type                                | optional | string                                |          |
| -                                                  | -        | -                        | roles. primary                             | optional | boolean                               |          |
| roomNumber                                         | optional | list of string           | -                                          | -        | -                                     |          |
| sambaLogonHours                                    | optional | list of int              | -                                          | -        | -                                     |          |
| sambaPrivileges                                    | optional | list of string           | -                                          | -        | -                                     |          |
| sambaRID                                           | optional | int                      | -                                          | -        | -                                     |          |
| sambaUserWorkstations                              | optional | list of string           | -                                          | -        | -                                     |          |
| sambahome                                          | optional | string                   | -                                          | -        | -                                     |          |
| scriptpath                                         | optional | string                   | -                                          | -        | -                                     |          |
| secretary                                          | optional | list of string           | -> Enterprise User -> manager. displayName | optional | string                                | 4.3      |
| serviceprovider (where is this defined?)           | optional | list of ???              | -                                          | -        | -                                     |          |
| shell                                              | optional | string                   | -                                          | -        | -                                     |          |
| -                                                  | -        | -                        | timezone                                   | optional | string                                | 4.1.1    |
| title                                              | optional | string                   | title                                      | optional | string                                | 4.1.1    |
| uidNumber                                          | REQUIRED | int                      | -                                          | -        | -                                     |          |
| umcProperty                                        | optional | complex                  | -                                          | -        | -                                     |          |
| unixhome                                           | REQUIRED | string                   | -                                          | -        | -                                     |          |
| unlock                                             | optional | boolean                  | -                                          | -        | -                                     |          |
| unlockTime                                         | optional | string                   | -                                          | -        | -                                     |          |
| userexpiry                                         | optional | string                   | -                                          | -        | -                                     |          |
| username                                           | REQUIRED | string                   | userName                                   | REQUIRED | string                                | 4.1.1    |
| /                                                  | /        | /                        | x509Certificates                           | optional | list of complex                       | 4.1.2    |
| userCertificate                                    | optional | string                   | x509Certificates. value                    | optional | string                                |          |
| certificateSubjectCommonName                       | optional | string                   | x509Certificates. display                  | optional | string                                |          |
| -                                                  | -        | -                        | x509Certificates. type                     | optional | string                                |          |
| -                                                  | -        | -                        | x509Certificates. primary                  | optional | boolean                               |          |
| certificateSubjectMail                             | optional | string                   | -                                          | -        | -                                     |          |
| certificateSubjectOrganisation                     | optional | string                   | -                                          | -        | -                                     |          |
| certificateSubjectOrganisationalUnit               | optional | string                   | -                                          | -        | -                                     |          |
| certificateSubjectLocation                         | optional | string                   | -                                          | -        | -                                     |          |
| certificateSubjectState                            | optional | string                   | -                                          | -        | -                                     |          |
| certificateSubjectCountry                          | optional | string                   | -                                          | -        | -                                     |          |
| certificateIssuerCommonName                        | optional | string                   | -                                          | -        | -                                     |          |
| certificateIssuerMail                              | optional | string                   | -                                          | -        | -                                     |          |
| certificateIssuerOrganisation                      | optional | string                   | -                                          | -        | -                                     |          |
| certificateIssuerOrganisationalUnit                | optional | string                   | -                                          | -        | -                                     |          |
| certificateIssuerLocation                          | optional | string                   | -                                          | -        | -                                     |          |
| certificateIssuerState                             | optional | string                   | -                                          | -        | -                                     |          |
| certificateIssuerCountry                           | optional | string                   | -                                          | -        | -                                     |          |
| certificateDateNotBefore                           | optional | string or DateTime       | -                                          | -        | -                                     |          |
| certificateDateNotAfter                            | optional | string or DateTime       | -                                          | -        | -                                     |          |
| certificateVersion                                 | optional | string                   | -                                          | -        | -                                     |          |
| certificateSerial                                  | optional | string                   | -                                          | -        | -                                     |          |

- (*3) [ISO3166](https://datatracker.ietf.org/doc/html/rfc7643#ref-ISO3166)
- (*4) [RFC5321](https://datatracker.ietf.org/doc/html/rfc5321)
- (*5) [RFC3966](https://datatracker.ietf.org/doc/html/rfc3966)
- (*6) Literal values: "aim", "gtalk", "icq", "xmpp", "msn", "skype", "qq", "yahoo", "other", ...
- (*7) Literal values: "work", "home", "mobile", "fax", "pager", "other", ...

### Enterprise User

- UDM: No specification. See UDM
  code → [../user.py](https://git.knut.univention.de/univention/ucs/-/blob/5.2-0/management/univention-directory-manager-modules/modules/univention/admin/handlers/users/user.py)
  and [../syntax.py](https://git.knut.univention.de/univention/ucs/-/blob/5.2-0/management/univention-directory-manager-modules/modules/univention/admin/syntax.py).
- SCIM: [RFC 7643 4.3 Enterprise User Schema Extension](https://datatracker.ietf.org/doc/html/rfc7643#section-4.3)

| UDM property     | avail    | type            | SCIM attribute       | avail    | type    | RFC 7643 |
|------------------|----------|-----------------|----------------------|----------|---------|----------|
| employeeNumber   | optional | string          | employeeNumber       | optional | string  | 4.3      |
| -                | -        | -               | costCenter           | optional | string  | 4.3      |
| organisation     | optional | string          | organization         | optional | string  | 4.3      |
| -                | -        | -               | division             | optional | string  | 4.3      |
| departmentNumber | optional | list of strings | department           | optional | string  | 4.3      |
| /                | /        | /               | manager              | optional | complex | 4.3      |
| -                | -        | -               | manager. value       | REQUIRED | UUID    |          |
| -                | -        | -               | manager. $ref        | REQUIRED | URI     |          |
| secretary (*8)   | optional | string          | manager. displayName | optional | string  |          |

- (*8) See [Bug 53741](https://forge.univention.org/bugzilla/show_bug.cgi?id=53741).

## Groups

- UDM: No specification. See UDM
  code → [../group.py](https://git.knut.univention.de/univention/ucs/-/blob/5.2-0/management/univention-directory-manager-modules/modules/univention/admin/handlers/groups/group.py)
  and [../syntax.py](https://git.knut.univention.de/univention/ucs/-/blob/5.2-0/management/univention-directory-manager-modules/modules/univention/admin/syntax.py).
- SCIM: [RFC 7643 4.2  "Group" Resource Schema](https://datatracker.ietf.org/doc/html/rfc7643#section-4.2)

| UDM property              | avail    | type                 | SCIM attribute       | avail    | type              | RFC 7643             |
|---------------------------|----------|----------------------|----------------------|----------|-------------------|----------------------|
| adGroupType               | optional | string               | -                    | -        | -                 |                      |
| allowedEmailGroups        | optional | list of strings (DN) | -                    | -        | -                 |                      |
| allowedEmailUsers         | optional | list of strings (DN) | -                    | -        | -                 |                      |
| description               | optional | string               | - (use →displayName) | -        | -                 |                      |
| guardianMemberRoles       | optional | list of strings      | -                    | -        | -                 |                      |
| gidNumber                 | optional | int                  | -                    | -        | -                 |                      |
| hosts                     | optional | list of strings (DN) | -                    | -        | -                 |                      |
| name                      | REQUIRED | string               | displayName          | REQUIRED | string            | 4.2 "Group" Resource |
| mailAddress               | optional | string               | -                    | -        | -                 |                      |
| /                         | /        | /                    | members              | REQUIRED | list of complex   | 4.2 "Group" Resource |
| - (from → users)          | -        | -                    | members. value       | REQUIRED | string (UUID)     |                      |
| -                         | -        | -                    | members. $ref        | REQUIRED | URI               |                      |
| - (see nestedGroup)       | -        | -                    | members. type        | optional | "User" or "Group" |                      |
| memberOf                  | optional | string (DN)          | -                    | -        | -                 |                      |
| nestedGroup               | optional | list of strings (DN) | - (see members.type) | -        | -                 |                      |
| sambaRID                  | optional | int                  | -                    | -        | -                 |                      |
| sambaGroupType            | optional | string               | -                    | -        | -                 |                      |
| sambaPrivileges           | optional | string               | -                    | -        | -                 |                      |
| serviceprovidergroup (*9) | optional | list of strings (DN) | -                    | -        | -                 |                      |
| users                     | optional | list of strings (DN) | - (→members)         | -        | -                 |                      |

- (*9) Property exists for SAML in UCS 5.0, but is non-existent in UCS 5.2.
