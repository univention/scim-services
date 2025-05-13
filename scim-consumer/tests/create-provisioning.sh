#!/bin/sh

curl --user admin:provisioning \
  --basic \
  -X 'POST' \
  'http://localhost:7777/v1/subscriptions' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "scim-consumer",
    "realms_topics": [
        {
            "realm": "udm",
            "topic": "users/user"
        }
    ],
    "request_prefill": true,
    "password": "univention"
}'