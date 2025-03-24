# Test SCIM server

https://github.com/python-scim/scim2-server

## Install server

```shell
git clone git@github.com:python-scim/scim2-server.git
```

## Run server

```shell
pipx install hatch
```

```shell
hatch run scim2-server
```

## Install tester

```shell
hatch shell
pip install scim2-cli
```

## Run tester

```shell
scim --url http://127.0.0.1:8080 test
```

## CLI: Create user

- Creating Resources: https://www.rfc-editor.org/rfc/rfc7644#section-3.3
- "User" Resource Schema: https://www.rfc-editor.org/rfc/rfc7643#section-4.1

```shell
scim --url http://127.0.0.1:8080 create user --help
```

```shell
scim --url http://127.0.0.1:8080 create user \
    --external-id "entry-uuid-0000-0001" \
    --user-name user1 \
    --name-formatted "Mr. User Uno One II" \
    --name-family-name One \
    --name-given-name User \
    --name-middle-name Uno \
    --name-honorific-prefix Mr. \
    --name-honorific-suffix II \
    --display-name "User One" \
    --nick-name One \
    --title Chefe \
    --user-type Employee \
    --preferred-language en_US \
    --locale en-US \
    --timezone Europe/Berlin \
    --active true \
    --password Univention.99 \
    --emails '[{"value": "user1@work.example.com", "primary": true, "type": "work"}, {"value": "user1@home.example.com", "type": "home"}]' \
    --phone-numbers '[{"value": "tel:+1-201-555-0123", "primary": true, "type": "work"}, {"value": "tel:+1-201-555-0124", "type": "mobile"}]' \
    --ims '[{"value": "user1@skype.com", "type": "skype"}, {"value": "+1-201-555-0124", "type": "signal"}]' \
    --photos '[{"value": "https://example.com/profile/user1/photo", "type": "photo"}, {"value": "https://example.com/profile/user1/photo?thumbnail=true", "type": "thumbnail"}]' \
    --addresses  '[{"streetAddress": "10 Downing Street\nZIP: SW1A 2AA\nUK", "type": "home"}]' \
    --entitlements '[{"value": "Nice house", "type": "housing"}, {"value": "Luck", "type": "meta"}, {"value": "Pet", "type": "hobby"}]' \
    --roles '[{"value": "Prime Minister", "type": "work"}, {"value": "Cousin", "type": "relation"}]'
```

Doesn't work as expected:

```shell
#    --profile-url "https://example.com/profile/user1" \

#    --enterpriseuser-employee-number "empl#1" \
#    --enterpriseuser-cost-center "cost#1" \
#    --enterpriseuser-organization "Gov" \
#    --enterpriseuser-division "Exec" \
#    --enterpriseuser-department "Ministry" \
#    --enterpriseuser-manager-value "manager-ID-001" \
#    --enterpriseuser-manager-ref "https://user.list/manager/001" \
#    --enterpriseuser-manager-display-name "The Queen"
#    --enterpriseuser-manager '{"value": "49d8ca9f808d", "$ref": "../Users/49d8ca9f808d", "display_name": "The Queen"}'
#    --enterpriseuser '{"employee_number": "empl#1", "cost_center": "cost#1", "organization": "Gov", "division": "Exec", "department": "Ministry"}'
```

## CLI list users

```shell
scim --url http://127.0.0.1:8080 query user | jq '.Resources.[] | {userName: .userName, id: .id, location: .meta.location}'
```

## CLI create group

- Creating Resources: https://www.rfc-editor.org/rfc/rfc7644#section-3.3
- "Group" Resource Schema: https://www.rfc-editor.org/rfc/rfc7643#section-4.2

```shell
scim --url http://127.0.0.1:8080 create group --help
```

```shell
scim --url http://127.0.0.1:8080 create group \
    --external-id an-id-0001 \
    --display-name "Group Nr. 1" \
    --members '[{"value": "e31e95c6daf549f79ccb02ad57c28e25", "$ref": "http://127.0.0.1:8080/v2/Users/e31e95c6daf549f79ccb02ad57c28e25", "type": "User", "display": "User One"}]'
```

## Add user to group

```shell
curl -X PATCH http://127.0.0.1:8080/v2/Groups/3aaf4b94e4114792bee33f676cfb049c -H "Content-Type: application/json" --data '{"schemas": ["urn:ietf:params:scim:api:messages:2.0:PatchOp"], "Operations": [{"op": "add", "path": "members", "value": [{"value": "57e21ab9e9254fd5aa2a77caae7a96bc", "$ref": "http://127.0.0.1:8080/v2/Users/57e21ab9e9254fd5aa2a77caae7a96bc"}]}]}'
```
