# Mapping UDM <-> SCIM v2

[[_TOC_]]

## Notice

- Dash (`-`) means attribute not available.
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
- `Uni:Core`: Abbreviation for the custom SCIM schema `urn:ietf:params:scim:schemas:extension:Univention:1.0:Core`
- `Uni:User`: Abbreviation for the custom SCIM schema `urn:ietf:params:scim:schemas:extension:Univention:1.0:User`
- `Uni:Group`: Abbreviation for the custom SCIM schema `urn:ietf:params:scim:schemas:extension:Univention:1.0:Group`
- `BaWü:User`: Abbreviation for the custom SCIM schema `urn:ietf:params:scim:schemas:extension:UniventionUser:2.0:User`

| UDM REST API field                | avail    | type                 | SCIM attribute     | avail    | type            | RFC 7643          | Comment   | MS | Impl |
|-----------------------------------|----------|----------------------|--------------------|----------|-----------------|-------------------|-----------|----|------|
| -                                 | -        | -                    | schemas            | REQUIRED | list of strings | 3. SCIM Resources |           | 1  | -    |
| uuid (entryUUID)                  | REQUIRED | string (UUID)        | -                  | -        | -               | -                 |           | 1  | -    |
| univentionObjectIdentifier        | REQUIRED | UUID                 | id                 | REQUIRED | string (UUID)   | 3.1 Common Attrs  |           | 1  | -    |
| *configurable*                    | optional | string               | externalId         | optional | string          | 3.1 Common Attrs  | (*4)      | 1  | -    |
| /                                 | /        | /                    | meta               | REQUIRED | complex         | 3.1 Common Attrs  |           | 1  | -    |
| objectType (univentionObjectType) | REQUIRED | string               | meta .resourceType | REQUIRED | string          |                   | (*5)      | 1  | -    |
| createTimestamp                   | optional | string (*2)          | meta. created      | REQUIRED | DateTime        |                   | (*8)      | 1  | -    |
| modifyTimestamp                   | optional | string (*2)          | meta. lastModified | REQUIRED | DateTime        |                   | (*8)      | 1  | -    |
| uri                               | REQUIRED | URI                  | meta. location     | REQUIRED | URI             |                   | (*6)      | 1  | -    |
| HTTP ETag header                  | optional | string (ETag *1 ?)   | meta. version      | optional | string (*1)     |                   | (*6) (*7) | 2  | x    |
| dn                                | optional | string (DN)          | -                  | -        | -               |                   |           |    |      |
| id (RDN, e.g. cn / uid)           | REQUIRED | string               | -                  | -        | -               |                   |           |    |      |
| options                           | REQUIRED | complex              | -                  | -        | -               |                   |           |    |      |
| options .posix, .samba, etc       | optional | boolean              | -                  | -        | -               |                   |           |    |      |
| policies                          | REQUIRED | complex              | -                  | -        | -               |                   |           |    |      |
| policies .policies/umc, etc       | optional | list of strings (DN) | -                  | -        | -               |                   |           |    |      |
| position                          | REQUIRED | string (DN)          | -                  | -        | -               |                   |           |    |      |
| properties                        | REQUIRED | complex              | /                  | /        | /               |                   |           |    |      |
| superordinate                     | optional | string (DN)          | -                  | -        | -               |                   |           |    |      |

- (*1) ETag, [RFC7232](https://datatracker.ietf.org/doc/html/rfc7232) sections 2.1 and 2.3.
- (*2) [Generalized Time, RFC 4517](https://datatracker.ietf.org/doc/html/rfc4517#section-3.3.13)
- ~~(*3) **TODO:** Discuss if we want this LDAP specific data to be available in SCIM (in a read-only field in a Univention custom schema).~~
- (*4) This mapping is configurable. By default, there is _no mapping_.
  - For details see [section "Identifiers" of the architecture overview page](architecture/Nubus-SCIM-service-architecture.md#identifiers).
  - Customer "BaWü" wants us to map `externalId` to the UDM property `dapExternalIdentifier`.
- (*5) Static rewrite of `users/user` to `User` and `groups/group` to `Group`.
- (*6) Values are _not_ synchronized. Each REST service generates them on their own. Just mentioned here, as they are the equivalent of one another.
- (*7) Already provided in MS1, although only required in MS2.
- (*8) The values in `createTimestamp` and `modifyTimestamp` are LDAP database internal and may change upon restore/backup.
  New metadata attributes may be introduced in the scope of [issue 2859 "Preserve LDAP Change-Metadata"](https://git.knut.univention.de/univention/dev/ucs/-/issues/2859).
  If that is done, we'll switch to them.

## Users

- UDM: No specification. See UDM
  code → [../user.py](https://git.knut.univention.de/univention/ucs/-/blob/5.2-0/management/univention-directory-manager-modules/modules/univention/admin/handlers/users/user.py)
  and [../syntax.py](https://git.knut.univention.de/univention/ucs/-/blob/5.2-0/management/univention-directory-manager-modules/modules/univention/admin/syntax.py).
  Password recovery properties are created
  in [a join script](https://git.knut.univention.de/univention/ucs/-/blob/5.2-0/management/univention-self-service/35univention-self-service-passwordreset-umc.inst?ref_type=heads#L102).
- SCIM: [RFC 7643 4.1 "User" Resource Schema](https://datatracker.ietf.org/doc/html/rfc7643#section-4.1)
  - [4.1.1 Singular Attributes](https://datatracker.ietf.org/doc/html/rfc7643#section-4.1.1)
  - [4.1.2 Multi-Valued Attributes](https://datatracker.ietf.org/doc/html/rfc7643#section-4.1.2)

| UDM property                                       | avail    | type                     | SCIM attribute                             | avail    | type                                           | RFC 7643 | Comment      | MS | Impl |
|----------------------------------------------------|----------|--------------------------|--------------------------------------------|----------|------------------------------------------------|----------|--------------|----|------|
| accountActivationDate                              | optional | string (complex)         | -                                          | -        | -                                              |          | (*1)         |    |      |
| homePostalAddress                                  | optional | list of string (complex) | addresses                                  | optional | list of complex                                | 4.1.2    | (*2)         |    |      |
| -                                                  | -        | -                        | addresses. formatted                       | optional | string                                         |          |              |    |      |
| street, homePostalAddress.street                   | optional | string                   | addresses. streetAddress                   | optional | string                                         |          |              |    |      |
| city, homePostalAddress.city                       | optional | string                   | addresses. locality                        | optional | string                                         |          |              |    |      |
| -                                                  | -        | -                        | addresses. region                          | optional | string                                         |          |              |    |      |
| postcode, homePostalAddress.zipcode                | optional | string                   | addresses. postalCode                      | optional | string                                         |          | (*2)         |    |      |
| country                                            | optional | string                   | addresses. country                         | optional | string (*3)                                    |          | (*2)         |    |      |
| -                                                  | -        | -                        | addresses. type                            | optional | string ("work", "home", "other")               |          |              |    |      |
| birthday                                           | optional | string                   | -                                          | -        | -                                              |          | (*1)         |    |      |
| departmentNumber                                   | optional | list of string           | -> Enterprise User -> department           | optional | string                                         | 4.3      | (*8)         |    |      |
| DeregistrationTimestamp                            | optional | string                   | -                                          | -        | -                                              |          | (*1)         |    |      |
| DeregisteredThroughSelfService                     | optional | boolean                  |                                            |          |                                                |          | (*1)         |    |      |
| description                                        | optional | string                   | Uni:User .description                      | optional | string                                         |          | direct       | 1  | -    |
| disabled                                           |          |                          | active                                     | optional | boolean                                        | 4.1.1    | direct (inv) |    |      |
| displayName                                        |          | string                   | displayName                                | optional | string                                         | 4.1.1    | (*14)        | 1  | -    |
| /                                                  | /        | /                        | emails (4 sub-attrs)                       | optional | complex                                        | 4.1.2    | (*10)        | 1  | -    |
| e-mail, mailPrimaryAddress, mailAlternativeAddress | optional | list of strings, string  | emails. value                              | optional | string (*4)                                    |          | (*10)        | 1  | -    |
| -                                                  | -        | -                        | emails. display                            | optional | string                                         |          | (*10)        | 1  | -    |
| -                                                  | -        | -                        | emails. type                               | optional | string ("work", "home", "other", ...)          |          | (*10)        | 1  | -    |
| -                                                  | optional | string                   | emails. primary                            | optional | boolean                                        |          | (*10)        | 1  | -    |
| employeeNumber                                     | optional | string                   | -> Enterprise User -> employeeNumber       | optional | string                                         | 4.3      | direct       |    |      |
| employeeType                                       | optional |                          | userType                                   | optional | string                                         | 4.1.1    | direct       |    |      |
| /                                                  | /        | /                        | entitlements                               | optional | list of complex                                | 4.1.2    | (*1)         |    |      |
| -                                                  | -        | -                        | entitlements. value                        | optional | string                                         |          |              |    |      |
| -                                                  | -        | -                        | entitlements. display                      | optional | string                                         |          |              |    |      |
| -                                                  | -        | -                        | entitlements. type                         | optional | string                                         |          |              |    |      |
| -                                                  | -        | -                        | entitlements. primary                      | optional | boolean                                        |          |              |    |      |
| firstname                                          |          | string                   | name. givenName                            | optional | string                                         | 4.1.1    | (*14)        | 1  | -    |
| gecos                                              | optional | string                   | -                                          | -        | -                                              |          | (*11)        |    |      |
| gidNumber                                          | REQUIRED | int                      | -> User.groups.primary=True                | -        | -                                              |          | (*21)        |    |      |
| groups                                             | REQUIRED | list of strings (DN)     | -                                          | -        | -                                              |          | (*12)        | 2  | -    |
| /                                                  | /        | /                        | groups                                     | optional | list of complex                                | 4.1.2    | (*12)        | 2  | -    |
| $group. univentionObjectIdentifier                 | -        | -                        | groups. value                              | optional | string (UUID)                                  |          |              | 2  | -    |
| -                                                  | -        | -                        | groups. $ref                               | optional | URI                                            |          |              | 2  | -    |
| $group. description                                | optional | string                   | groups. display                            | optional | string                                         |          |              | 2  | -    |
| -                                                  | -        | -                        | groups. type                               | optional | string ("direct", "indirect")                  |          |              | 2  | -    |
| guardianRoles                                      | optional | list of strings          | roles. value                               | -        | -                                              |          | (*19)        | 2  | -    |
| guardianInheritedRoles                             | optional | list of strings          | roles. value (merge)                       | -        | -                                              |          | (*19)        | 2  | -    |
| homeShare                                          | optional | string (DN)              | -                                          | -        | -                                              |          | (*1)         |    |      |
| homeSharePath                                      | optional | string                   | -                                          | -        | -                                              |          | (*1)         |    |      |
| homeTelephoneNumber                                | optional | list of strings          |                                            |          |                                                |          | (*1)         |    |      |
| homedrive                                          | optional | string                   | -                                          | -        | -                                              |          | (*1)         |    |      |
| /                                                  | /        | /                        | ims                                        | optional | list of complex                                | 4.1.2    | (*1)         |    |      |
| -                                                  | -        | -                        | ims. value                                 | optional | string                                         |          |              |    |      |
|                                                    |          |                          | ims. display                               | optional | string                                         |          |              |    |      |
| -                                                  | -        | -                        | ims. type                                  | optional | string (*6)                                    |          |              |    |      |
| -                                                  | -        | -                        | ims. primary                               | optional | boolean                                        |          |              |    |      |
| jpegPhoto                                          | optional | string                   | photos. value                              | -        | -                                              |          | (*8)         |    |      |
| locale (*22)                                       | optional | string (*13)             | locale                                     | optional | string (*13)                                   | 4.1.1    | (*13) (*22)  | 2  | -    |
| lastname                                           | REQUIRED | string                   | name. familyName                           | optional | string                                         | 4.1.1    | (*14)        | 1  | -    |
| locked                                             |          | boolean                  | -                                          | -        | -                                              |          | (*1)         |    |      |
| lockedTime                                         |          | string                   | -                                          | -        | -                                              |          | (*1)         |    |      |
| mailAlternativeAddress                             | optional | list of strings          | → emails. value + emails. type=alias       | optional | string + boolean                               |          | (*10)        | 1  | -    |
| mailForwardAddress                                 | optional | list of strings          | -                                          | -        | -                                              |          | (*1)         |    |      |
| mailForwardCopyToSelf                              | optional | string                   | -                                          | -        | -                                              |          | (*1)         |    |      |
| mailHomeServer                                     | optional | string                   | -                                          | -        | -                                              |          | (*1)         |    |      |
| mailPrimaryAddress                                 | optional | string                   | → emails. value + emails. type=mailbox     | optional | string + boolean                               | 4.1.2    | (*10)        | 1  | -    |
| mailUserQuota (where is this defined?)             | optional | string (int)             | -                                          | -        | -                                              |          | (*1)         |    |      |
| mobileTelephoneNumber                              | optional | list of strings          | phoneNumbers. value _AND_ .type=mobile     | optional | string + string                                | 4.1.1    | (*15)        |    |      |
| /                                                  | /        | /                        | name (6 sub-attrs)                         | optional | complex                                        | 4.1.1    | (*14)        | 1  | -    |
| (→ lastname)                                       | REQUIRED | string                   | name. familyName                           | optional | string                                         | 4.1.1    | (*14)        | 1  | -    |
| -                                                  |          | -                        | name. formatted                            | optional | string                                         | 4.1.1    | (*14)        | 1  | -    |
| (→ firstname)                                      |          | string                   | name. givenName                            | optional | string                                         | 4.1.1    | (*14)        | 1  | -    |
| -                                                  | -        | -                        | name. honorificPrefix                      | optional | string                                         | 4.1.1    | (*14)        |    |      |
| -                                                  | -        | -                        | name. honorificSuffix                      | optional | string                                         | 4.1.1    | (*14)        |    |      |
| -                                                  | -        | -                        | name. middleName                           | optional | string                                         | 4.1.1    | (*14)        |    |      |
| -                                                  | -        | -                        | nickName                                   | optional | string                                         | 4.1.1    | (*1)         |    |      |
| objectFlag                                         |          | list of ???              | -                                          | -        | -                                              |          | not mapped   |    |      |
| organisation                                       | optional |                          | -> Enterprise User -> organization         | optional | string                                         | 4.3      | direct       |    |      |
| overridePWHistory                                  | optional |                          | -                                          | -        | -                                              |          | (*1)         |    |      |
| overridePWLength                                   | optional |                          | -                                          | -        | -                                              |          | (*1)         |    |      |
| pagerTelephoneNumber                               | optional | list of strings          | phoneNumbers. value _AND_ .type=pager      | -        | string + string                                |          | (*8)         |    |      |
| password                                           | optional | string                   | password                                   | optional | string                                         | 4.1.1    | 1:1          | 1  | -    |
| passwordexpiry                                     | optional | string                   | -                                          | -        | -                                              |          | (*1)         |    |      |
| PasswordRecoveryEmailVerified                      | optional | boolean                  | -                                          | -        | -                                              |          | (*1)         |    |      |
| PasswordRecoveryMobile                             | optional | string                   | -                                          | -        | -                                              |          | (*1)         |    |      |
| PasswordRecoveryEmail                              | optional | string                   | Uni:User .passwordRecoveryEmail            | -        | -                                              |          |              | 2  | -    |
| /                                                  | /        | /                        | phoneNumbers                               | optional | list of complex                                | 4.1.2    | (*15)        |    |      |
| phone                                              | optional | list of string           | phoneNumbers. value                        | optional | string (*5)                                    | 4.1.1    | (*15)        |    |      |
| -                                                  | -        | -                        | phoneNumbers. display                      | optional | string                                         |          |              |    |      |
| -                                                  | -        | -                        | phoneNumbers. type                         | optional | string (*7)                                    |          |              |    |      |
| -                                                  | -        | -                        | phoneNumbers. primary                      | optional | boolean                                        |          |              |    |      |
| /                                                  | /        | /                        | photos                                     | optional | list of complex                                | 4.1.2    | (*16)        |    |      |
| -                                                  | -        | -                        | photos. value                              | optional | URI                                            |          |              |    |      |
| -                                                  | -        | -                        | photos. display                            | optional | string                                         |          |              |    |      |
| -                                                  | -        | -                        | photos. type                               | optional | string ("photo", "thumbnail")                  |          |              |    |      |
| -                                                  | -        | -                        | photos. primary                            | optional | boolean                                        |          |              |    |      |
| preferredLanguage                                  | optional | string                   | preferredLanguage                          | optional | string (*17)                                   |          | direct       |    |      |
| primaryGroup                                       | REQUIRED | string                   | -                                          | -        | -                                              |          | (*12) (*18)  |    |      |
| profilepath                                        | optional | string                   | -                                          | -        | -                                              |          | (*1)         |    |      |
| -                                                  | -        | -                        | profileUrl                                 | optional | URI                                            | 4.1.1    | (*1)         |    |      |
| pwdChangeNextLogin                                 | optional | boolean                  | -                                          | -        | -                                              |          | (*1)         |    |      |
| RegisteredThroughSelfService                       | optional | boolean                  | -                                          | -        | -                                              |          | (*1)         |    |      |
| /                                                  | /        | /                        | roles                                      | optional | list of complex                                | 4.1.2    | (*19)        | 1  | -    |
| -                                                  | -        | -                        | roles. value                               | optional | string                                         |          |              | 1  | -    |
| -                                                  | -        | -                        | roles. display                             | optional | string                                         |          |              | 1  | -    |
| -                                                  | -        | -                        | roles. type                                | optional | string ("guardian-direct", guardian-indirect") |          |              | 1  | -    |
| -                                                  | -        | -                        | roles. primary                             | optional | boolean                                        |          |              | 1  | -    |
| roomNumber                                         | optional | list of string           | -                                          | -        | -                                              |          | (*1)         |    |      |
| sambaLogonHours                                    | optional | list of int              | -                                          | -        | -                                              |          | (*1)         |    |      |
| sambaPrivileges                                    | optional | list of string           | -                                          | -        | -                                              |          | (*1)         |    |      |
| sambaRID                                           | optional | int                      | -                                          | -        | -                                              |          | (*1)         |    |      |
| sambaUserWorkstations                              | optional | list of string           | -                                          | -        | -                                              |          | (*1)         |    |      |
| sambahome                                          | optional | string                   | -                                          | -        | -                                              |          | (*1)         |    |      |
| scriptpath                                         | optional | string                   | -                                          | -        | -                                              |          | (*1)         |    |      |
| secretary                                          | optional | list of string           | -> Enterprise User -> manager. displayName | optional | string                                         | 4.3      | direct (*20) |    |      |
| serviceprovider (where is this defined?)           | optional | list of ???              | -                                          | -        | -                                              |          | (*1)         |    |      |
| shell                                              | optional | string                   | -                                          | -        | -                                              |          | (*1)         |    |      |
| -                                                  | -        | -                        | timezone                                   | optional | string                                         | 4.1.1    | (*1)         |    |      |
| title                                              | optional | string                   | title                                      | optional | string                                         | 4.1.1    | direct       |    |      |
| uidNumber                                          | REQUIRED | int                      | -                                          | -        | -                                              |          | (*1)         |    |      |
| umcProperty                                        | optional | complex                  | -                                          | -        | -                                              |          | (*1)         |    |      |
| unixhome                                           | REQUIRED | string                   | -                                          | -        | -                                              |          | (*1)         |    |      |
| unlock                                             | optional | boolean                  | -                                          | -        | -                                              |          | (*1)         |    |      |
| unlockTime                                         | optional | string                   | -                                          | -        | -                                              |          | (*1)         |    |      |
| userexpiry                                         | optional | string                   | -                                          | -        | -                                              |          | (*1)         |    |      |
| username                                           | REQUIRED | string                   | userName                                   | REQUIRED | string                                         | 4.1.1    | direct       | 1  | -    |
| /                                                  | /        | /                        | x509Certificates                           | optional | list of complex                                | 4.1.2    | (*1)         |    |      |
| userCertificate                                    | optional | string                   | x509Certificates. value                    | optional | string                                         |          | (*1) direct  |    |      |
| certificateSubjectCommonName                       | optional | string                   | x509Certificates. display                  | optional | string                                         |          | (*1) direct  |    |      |
| -                                                  | -        | -                        | x509Certificates. type                     | optional | string                                         |          | (*1)         |    |      |
| -                                                  | -        | -                        | x509Certificates. primary                  | optional | boolean                                        |          | (*1)         |    |      |
| certificateSubjectMail                             | optional | string                   | -                                          | -        | -                                              |          | (*1)         |    |      |
| certificateSubjectOrganisation                     | optional | string                   | -                                          | -        | -                                              |          | (*1)         |    |      |
| certificateSubjectOrganisationalUnit               | optional | string                   | -                                          | -        | -                                              |          | (*1)         |    |      |
| certificateSubjectLocation                         | optional | string                   | -                                          | -        | -                                              |          | (*1)         |    |      |
| certificateSubjectState                            | optional | string                   | -                                          | -        | -                                              |          | (*1)         |    |      |
| certificateSubjectCountry                          | optional | string                   | -                                          | -        | -                                              |          | (*1)         |    |      |
| certificateIssuerCommonName                        | optional | string                   | -                                          | -        | -                                              |          | (*1)         |    |      |
| certificateIssuerMail                              | optional | string                   | -                                          | -        | -                                              |          | (*1)         |    |      |
| certificateIssuerOrganisation                      | optional | string                   | -                                          | -        | -                                              |          | (*1)         |    |      |
| certificateIssuerOrganisationalUnit                | optional | string                   | -                                          | -        | -                                              |          | (*1)         |    |      |
| certificateIssuerLocation                          | optional | string                   | -                                          | -        | -                                              |          | (*1)         |    |      |
| certificateIssuerState                             | optional | string                   | -                                          | -        | -                                              |          | (*1)         |    |      |
| certificateIssuerCountry                           | optional | string                   | -                                          | -        | -                                              |          | (*1)         |    |      |
| certificateDateNotBefore                           | optional | string or DateTime       | -                                          | -        | -                                              |          | (*1)         |    |      |
| certificateDateNotAfter                            | optional | string or DateTime       | -                                          | -        | -                                              |          | (*1)         |    |      |
| certificateVersion                                 | optional | string                   | -                                          | -        | -                                              |          | (*1)         |    |      |
| certificateSerial                                  | optional | string                   | -                                          | -        | -                                              |          | (*1)         |    |      |
| primaryOrgUnit (*23)                               | optional | string                   | BaWü:User .primaryOrgUnit                  | optional | string                                         |          | (*23)        | 1  | -    |
| secondaryOrgUnits (*23)                            | optional | list of string           | BaWü:User .secondaryOrgUnits               | optional | list of string                                 |          | (*23)        | 1  | -    |

- (*1) **TODO:** Discuss if we want to map this field, adding either a field to a Univention custom SCIM schema or a UDM extended attribute.
- (*2) Postal addresses in SCIM are stored in a list of complex in the field `addresses`.
  Its sub-fields are `formatted`, `streetAddress`, `locality`, `region`, `postalCode`, `country`, and `type`.
  - In UDM there are two possibilities to store postal addresses:
    - Four single-attribute properties: `street`, `city`, `postcode`, and  `country`.
    - A list of complex in the field `homePostalAddress`. Its sub-fields are `street`, `city`, and `zipcode`.
    - **TODO**: Discuss how we want to map postal addresses. Options:
      - (a) Map _one_ postal address between _the first entry_ in SCIM's `addresses` and UDM's single-attribute properties
        `street`, `city`, `postcode`, and  `country`.
      - (b) Map the _complete list_ of postal addresses between SCIM's `addresses` and UDM's `homePostalAddress`.
      - (c) Do (a) and (b). (@dtroeder's choice)
      - We have to decide if we want to allow the customer to choose between (a), (b) and (c), or if we're hard coding this.
- (*3) [ISO3166](https://datatracker.ietf.org/doc/html/rfc7643#ref-ISO3166)
- (*4) [RFC5321](https://datatracker.ietf.org/doc/html/rfc5321)
- (*5) [RFC3966](https://datatracker.ietf.org/doc/html/rfc3966)
- (*6) Literal values: "aim", "gtalk", "icq", "xmpp", "msn", "skype", "qq", "yahoo", "other", ...
- (*7) Literal values: "work", "home", "mobile", "fax", "pager", "other", ...
- (*8) Mismatch between single-value and multi-value.
  - **TODO**: Discuss how to handle this. Options:
    - Map only one entry and document that publicly.
    - Create an extension with a multi-value field, on the side where it's single-value.
- (*9) Unused footnote.
- (*10) Email addresses in SCIM are stored in a list of complex in the field `emails`.
  Its sub-fields are `value`, `display`, `type`, and `primary`.
  - In UDM there are three properties to store email addresses:
    - `e-mail`: A list of email addresses used for address books. They can be hosted externally.
    - `mailPrimaryAddress`: A mailbox hosted by the UCS (Nubus?) mail server.
    - `mailAlternativeAddress`: A list of email aliases for the mailbox (`mailPrimaryAddress`) hosted by the UCS (Nubus?) mail server.
  - SCIM doesn't have a notion of email hosting, and it doesn't know about _hosted mail domains_.
    It just stores contact information.
    Thus, `e-mail` is the natural choice for mapping `emails`.
  - But we can use the `type` sub-field to define a mapping that allows clients to target
    `mailPrimaryAddress` (specifying `type=mailbox`) and `mailAlternativeAddress` (specifying `type=alias`).
    All other addresses (`email.type` is unset or not `alias|mailbox`) are mapped to `e-mail`.
    - We don't use `primary=true` to define the mapping to `mailPrimaryAddress`,
      because it's meant as a general way for users to sort their email addresses (in address books).
- (*11) Not mapped. The UDM property `gecos` could sync to SCUM `displayName` or `name.formatted`.
  But those are already synced from UDM's `displayName`.
  Syncing towards UDM isn't necessary, because the `users/user` module automatically generates (and updates) the value from `firstname` and `lastname`.
- (*12) The `groups` fields in SCIM and UDM have different formats and different features:
  - In SCIM, ...
    - All groups the user belongs to are listed, either through direct membership or through nested groups.
    - The field is a list of complex. Sub-fields are `value` (the groups `id`),
      `$ref` (the URI of the corresponding "Group" resource), `display` (human-readable name), and
      `type` (membership type, canonical values: `direct`, `indirect` (nested)).
    - The `groups` field is read-only. Membership can only be changed using the "Groups" resource.
  - In UDM, ...
    - Only those groups are listed, that the user is a direct member of. Nested groups are not listed.
    - The field is a list of strings. Each entry is the DN of a group the user is a direct member of.
    - The `groups` field is writable. Changes to it lead to UDM changing the corresponding group objects in LDAP.
  - The mapping of this field between SCIM and UDM is very expensive.
    In both directions one database search per group is required to map the IDs in one object to the IDs in the other object.
    - Caching of those requests is highly recommended.
  - In MS1 we will _not_ support this field in SCIM. It will always be an empty list.
  - In MS2 we will support it.
- (*13) Valid language tags are defined in [RFC5646](https://datatracker.ietf.org/doc/html/rfc5646).
- (*14) The SCIM `name` field is a multi-value complex type with 6 sub-attributes:
  `formatted`, `familyName`, `givenName`, `middleName`, `honorificPrefix`, `honorificSuffix`.
  - UDM's `displayName` is mapped to SCIM's `displayName`.
  - UDM's `firstname` is mapped to SCIM's `givenName`.
  - UDM's `lastname` is mapped to SCIM's `familyName`.
  - No UDM properties exist to map `middleName`, `honorificPrefix`, or `honorificSuffix`.
  - The SCIM attribute `name.formatted` will be auto-generated from the other `name` fields as described in the SCIM specification.
- (*15) `phoneNumbers`
- (*16) `photos`
- (*17) The format of `preferredLanguage` is the same as the HTTP `Accept-Language` header field (not including `Accept-Language:`)
  and is specified in [Section 5.3.5 of RFC7231](https://datatracker.ietf.org/doc/html/rfc7231#section-5.3.5).
- (*18) Instead of creating a dedicated field in a custom Univention schema,
  I suggest to map `primaryGroup` to an entry in the user's `groups` list (see (*12)),
  and add a boolean field `primary` to it.
  - We have to check, if adding a field is allowed.
- (*19) A list of roles for the user that collectively represent who the user is.
  No vocabulary, syntax, or canonical types are specified.
  - The SCIM `roles` field is a multi-value complex type with 4 sub-attributes: `value`, `display`, `type`, and `primary`.
  - I suggest to use this to map the Guardian properties `guardianRoles` and `guardianInheritedRoles`.
    - Values from both `guardianRoles` and `guardianInheritedRoles` are merged and stored in `roles.value`.
    - The `roles.type` sub-field is set to `guardian-direct` for roles from `guardianRole` and
      `guardian-indirect` for roles from `guardianInheritedRole`,
      with `guardian-direct` having preference if the same role exists on the user and group.
    - The `guardian-` prefix exists, so `roles` can also be used for other purposes (e.g., legacy UCS@school roles, customer organizational roles).
    - The set of entries with `type=guardian-direct` can be changed in update operations.
    - The set of entries with `type=guardian-indirect` is read-only. Attempts to change them will be ignored.
- (*20) See [Bug 53741](https://forge.univention.org/bugzilla/show_bug.cgi?id=53741) regarding the use of `secretary` in UDM.
- (*21) Map the `gidNumber` (primary Group) to the entry in `User.groups` with `User.groups.primary=True`.
- (*22) Create a new standard UDM property for `users/user` ([here](https://git.knut.univention.de/univention/dev/ucs/-/blob/5.2-1/management/univention-directory-manager-modules/modules/univention/admin/handlers/users/user.py?ref_type=heads#L99)).
  Requested by openDesk. It will be needed for the Portal and other applications in the future, too.
- (*23) `primaryOrgUnit` and `secondaryOrgUnits` are UDM extended attributes that customer BaWü requires in SCIM.
  - In MS1 we will create and deliver a custom SCIM schema and mapping for BaWü with the SCIM server software.
    The goal of MS1 is for the customer to test the servie. Thus, although this is a customer extension, we'll deliver it.
    - We will need to create those UDM extended attributes for testing.
      This can be done with the UDM module `settings/extended_attribute`.
      Use the LDAP attributes `univentionFreeAttribute1` and `univentionFreeAttribute2`.
  - In MS2 customers will get an interface to add their own schemas and mappings. We will then _not_ deliver this schema anymore.

### Enterprise User

- UDM: No specification. See UDM
  code → [../user.py](https://git.knut.univention.de/univention/ucs/-/blob/5.2-0/management/univention-directory-manager-modules/modules/univention/admin/handlers/users/user.py)
  and [../syntax.py](https://git.knut.univention.de/univention/ucs/-/blob/5.2-0/management/univention-directory-manager-modules/modules/univention/admin/syntax.py).
- SCIM: [RFC 7643 4.3 Enterprise User Schema Extension](https://datatracker.ietf.org/doc/html/rfc7643#section-4.3)

| UDM property     | avail    | type            | SCIM attribute       | avail    | type    | RFC 7643 | Comment   | MS | Impl |
|------------------|----------|-----------------|----------------------|----------|---------|----------|-----------|----|------|
| employeeNumber   | optional | string          | employeeNumber       | optional | string  | 4.3      | direct    |    |      |
| -                | -        | -               | costCenter           | optional | string  | 4.3      | (*1)      |    |      |
| organisation     | optional | string          | organization         | optional | string  | 4.3      | direct    |    |      |
| -                | -        | -               | division             | optional | string  | 4.3      | (*1)      |    |      |
| departmentNumber | optional | list of strings | department           | optional | string  | 4.3      | (*2)      |    |      |
| /                | /        | /               | manager              | optional | complex | 4.3      | (*1) (*3) |    |      |
| -                | -        | -               | manager. value       | REQUIRED | UUID    |          |           |    |      |
| -                | -        | -               | manager. $ref        | REQUIRED | URI     |          |           |    |      |
| secretary        | optional | string          | manager. displayName | optional | string  |          | (*4)      |    |      |

- (*1) **TODO:** Discuss if we want to map this field, adding either a field to a Univention custom SCIM schema or a UDM extended attribute.
- (*2) Mismatch between single-value and multi-value.
- (*3) The SCIM `manager` field is a multi-value complex type with 3 sub-attributes:
  `value` (`id` of the user's manager), `$ref` (URI of the user's manager), and `displayName` (`displayName` of the User's manager).
- (*4) See [Bug 53741](https://forge.univention.org/bugzilla/show_bug.cgi?id=53741) regarding the use of `secretary` in UDM.

## Groups

- UDM: No specification. See UDM
  code → [../group.py](https://git.knut.univention.de/univention/ucs/-/blob/5.2-0/management/univention-directory-manager-modules/modules/univention/admin/handlers/groups/group.py)
  and [../syntax.py](https://git.knut.univention.de/univention/ucs/-/blob/5.2-0/management/univention-directory-manager-modules/modules/univention/admin/syntax.py).
- SCIM: [RFC 7643 4.2  "Group" Resource Schema](https://datatracker.ietf.org/doc/html/rfc7643#section-4.2)

| UDM property         | avail    | type                 | SCIM attribute         | avail     | type                | RFC 7643 | Comment   | MS | Impl |
|----------------------|----------|----------------------|------------------------|-----------|---------------------|----------|-----------|----|------|
| adGroupType          | optional | string               | -                      | -         | -                   |          | (*1)      |    |      |
| allowedEmailGroups   | optional | list of strings (DN) | -                      | -         | -                   |          | (*1)      |    |      |
| allowedEmailUsers    | optional | list of strings (DN) | -                      | -         | -                   |          | (*1)      |    |      |
| description          | optional | string               | Uni:Group .description | -         | -                   |          | direct    | 1  | -    |
| guardianMemberRoles  | optional | list of strings      | Uni:Group .memberRoles | optional  | list of complex     |          | (*4)      | 1  | -    |
| -                    | -        | -                    | memberRoles. value     | optional  | string              |          |           | 1  | -    |
| -                    | -        | -                    | memberRoles. type      | optional  | string ("guardian") |          |           | 1  | -    |
| gidNumber            | optional | int                  | -                      | -         | -                   |          | (*1)      |    |      |
| hosts                | optional | list of strings (DN) | -                      | -         | -                   |          | ignore    |    |      |
| name                 | REQUIRED | string               | displayName            | REQUIRED  | string              | 4.2      | direct    | 1  | -    |
| mailAddress          | optional | string               | -                      | -         | -                   |          | (*1)      |    |      |
| /                    | /        | /                    | members                | REQUIRED  | list of complex     | 4.2      | (*2)      | 1  | -    |
| - (from → users)     | -        | -                    | members. value         | REQUIRED  | string (UUID)       |          |           | 1  | -    |
| -                    | -        | -                    | members. $ref          | REQUIRED  | URI                 |          |           | 1  | -    |
| -                    | -        | -                    | members. display       | optional  | string              |          |           | 1  | -    |
| - (see nestedGroup)  | -        | -                    | members. type          | optional  | "User" or "Group"   |          |           | 1  | -    |
| memberOf             | optional | string (DN)          | -                      | -         | -                   |          |           |    |      |
| nestedGroup          | optional | list of strings (DN) | - (see members.type)   | -         | -                   |          |           |    |      |
| sambaRID             | optional | int                  | -                      | -         | -                   |          | (*1)      |    |      |
| sambaGroupType       | optional | string               | -                      | -         | -                   |          | (*1)      |    |      |
| sambaPrivileges      | optional | string               | -                      | -         | -                   |          | (*1)      |    |      |
| serviceprovidergroup | optional | list of strings (DN) | -                      | -         | -                   |          | (*1) (*3) |    |      |
| users                | optional | list of strings (DN) | - (→members)           | -         | -                   |          |           | 1  | -    |

- (*1) **TODO:** Discuss if we want to map this field, adding either a field to a Univention custom SCIM schema or a UDM extended attribute.
- (*2) The SCIM `members` field is a multi-value complex type with 4 sub-attributes:
  `value` (`id` of the referenced object), `$ref` (URI of the referenced object),
  `type` (referenced object type: `User` or `Group` (nested)), and `displayName` (human-readable name of the referenced object).
  - While values MAY be added or removed, sub-attributes of members are "immutable".
- (*3) Property exists for SAML in UCS 5.0, but is non-existent in UCS 5.2.
- (*4) The values in a UDM group's `guardianMemberRoles` property are "inherited" by members of the group in the UDM users property `guardianInheritedRoles`.
  - The `roles.type` sub-field allows using this field for other purposes than the Guardian.
  - When mapping with UDM `guardianMemberRoles`, the `roles.type` sub-field is always `guardian`.
