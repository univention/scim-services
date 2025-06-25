# scim-consumer

A Helm chart for the Nubus SCIM consumer

- **Version**: 0.0.1
- **Type**: application
- **AppVersion**:
- **Homepage:** <https://www.univention.de/>

## TL;DR

```console
helm upgrade --install scim-consumer oci://artifacts.software-univention.de/nubus/charts/scim-consumer
```

## Introduction

This chart does install the Nubus Provisioning SCIM Consumer.

The service provides a way to provision downstream systems via the SCIM Protocol.

## Installing

To install the chart with the release name `scim-consumer`:

```console
helm upgrade --install scim-consumer oci://artifacts.software-univention.de/nubus/charts/scim-consumer
```

## Uninstalling

To uninstall the chart with the release name `scim-consumer`:

```console
helm uninstall scim-consumer
```

## Requirements

| Repository | Name | Version |
|------------|------|---------|
| oci://artifacts.software-univention.de/nubus/charts | nubus-common | ^0.21.x |

## Values

<table>
	<thead>
		<th>Key</th>
		<th>Type</th>
		<th>Default</th>
		<th>Description</th>
	</thead>
	<tbody>
		<tr>
			<td>containerSecurityContext.allowPrivilegeEscalation</td>
			<td>bool</td>
			<td><pre lang="json">
false
</pre>
</td>
			<td>Enable container privileged escalation.</td>
		</tr>
		<tr>
			<td>containerSecurityContext.capabilities</td>
			<td>object</td>
			<td><pre lang="json">
{
  "drop": [
    "ALL"
  ]
}
</pre>
</td>
			<td>Security capabilities for container.</td>
		</tr>
		<tr>
			<td>containerSecurityContext.enabled</td>
			<td>bool</td>
			<td><pre lang="json">
true
</pre>
</td>
			<td>Enable security context.</td>
		</tr>
		<tr>
			<td>containerSecurityContext.privileged</td>
			<td>bool</td>
			<td><pre lang="json">
false
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>containerSecurityContext.readOnlyRootFilesystem</td>
			<td>bool</td>
			<td><pre lang="json">
true
</pre>
</td>
			<td>Mounts the container's root filesystem as read-only.</td>
		</tr>
		<tr>
			<td>containerSecurityContext.runAsGroup</td>
			<td>int</td>
			<td><pre lang="json">
1000
</pre>
</td>
			<td>Process group id.</td>
		</tr>
		<tr>
			<td>containerSecurityContext.runAsNonRoot</td>
			<td>bool</td>
			<td><pre lang="json">
true
</pre>
</td>
			<td>Run container as a user.</td>
		</tr>
		<tr>
			<td>containerSecurityContext.runAsUser</td>
			<td>int</td>
			<td><pre lang="json">
1000
</pre>
</td>
			<td>Process user id.</td>
		</tr>
		<tr>
			<td>containerSecurityContext.seccompProfile.type</td>
			<td>string</td>
			<td><pre lang="json">
"RuntimeDefault"
</pre>
</td>
			<td>Disallow custom Seccomp profile by setting it to RuntimeDefault.</td>
		</tr>
		<tr>
			<td>extraEnvVars</td>
			<td>list</td>
			<td><pre lang="json">
[]
</pre>
</td>
			<td>Array with extra environment variables to add to containers.  extraEnvVars:   - name: FOO     value: "bar"</td>
		</tr>
		<tr>
			<td>extraSecrets</td>
			<td>list</td>
			<td><pre lang="json">
[]
</pre>
</td>
			<td>Optionally specify a secret to create (primarily intended to be used in development environments to provide custom certificates)</td>
		</tr>
		<tr>
			<td>extraVolumeMounts</td>
			<td>list</td>
			<td><pre lang="json">
[]
</pre>
</td>
			<td>Optionally specify an extra list of additional volumeMounts.</td>
		</tr>
		<tr>
			<td>extraVolumes</td>
			<td>list</td>
			<td><pre lang="json">
[]
</pre>
</td>
			<td>Optionally specify an extra list of additional volumes.</td>
		</tr>
		<tr>
			<td>global.imagePullPolicy</td>
			<td>string</td>
			<td><pre lang="json">
"IfNotPresent"
</pre>
</td>
			<td>Define an ImagePullPolicy.  Ref.: https://kubernetes.io/docs/concepts/containers/images/#image-pull-policy </td>
		</tr>
		<tr>
			<td>global.imagePullSecrets</td>
			<td>list</td>
			<td><pre lang="json">
[]
</pre>
</td>
			<td>Credentials to fetch images from private registry. Ref: https://kubernetes.io/docs/tasks/configure-pod-container/pull-image-private-registry/  imagePullSecrets:   - "docker-registry"</td>
		</tr>
		<tr>
			<td>global.imageRegistry</td>
			<td>string</td>
			<td><pre lang="json">
"artifacts.software-univention.de"
</pre>
</td>
			<td>Container registry address.</td>
		</tr>
		<tr>
			<td>global.secrets.masterPassword</td>
			<td>string</td>
			<td><pre lang="json">
null
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>ldap</td>
			<td>object</td>
			<td><pre lang="json">
{
  "auth": {
    "bindDn": null,
    "existingSecret": {
      "keyMapping": {
        "password": null
      },
      "name": null
    }
  },
  "connection": {
    "host": null
  }
}
</pre>
</td>
			<td>Upstream LDAP server to resolve group member DN's</td>
		</tr>
		<tr>
			<td>ldap.auth.existingSecret.keyMapping.password</td>
			<td>string</td>
			<td><pre lang="json">
null
</pre>
</td>
			<td>The key to retrieve the password from. Setting this value allows to use a key with a different name.</td>
		</tr>
		<tr>
			<td>ldap.auth.existingSecret.name</td>
			<td>string</td>
			<td><pre lang="json">
null
</pre>
</td>
			<td>The name of an existing Secret to use for retrieving the password to authenticate with the source LDAP directory.  "udm.auth.password" will be ignored if this value is set.</td>
		</tr>
		<tr>
			<td>ldap.connection.host</td>
			<td>string</td>
			<td><pre lang="json">
null
</pre>
</td>
			<td>LDAP Server hostname (e.g. "nubus-ldap-server")</td>
		</tr>
		<tr>
			<td>podSecurityContext.enabled</td>
			<td>bool</td>
			<td><pre lang="json">
true
</pre>
</td>
			<td>Enable security context.</td>
		</tr>
		<tr>
			<td>podSecurityContext.fsGroup</td>
			<td>int</td>
			<td><pre lang="json">
1000
</pre>
</td>
			<td>If specified, all processes of the container are also part of the supplementary group.</td>
		</tr>
		<tr>
			<td>podSecurityContext.fsGroupChangePolicy</td>
			<td>string</td>
			<td><pre lang="json">
"Always"
</pre>
</td>
			<td>Change ownership and permission of the volume before being exposed inside a Pod.</td>
		</tr>
		<tr>
			<td>podSecurityContext.sysctls</td>
			<td>list</td>
			<td><pre lang="json">
[
  {
    "name": "net.ipv4.ip_unprivileged_port_start",
    "value": "1"
  }
]
</pre>
</td>
			<td>Allow binding to ports below 1024 without root access.</td>
		</tr>
		<tr>
			<td>provisioningApi</td>
			<td>object</td>
			<td><pre lang="json">
{
  "auth": {
    "existingSecret": {
      "keyMapping": {
        "password": null
      },
      "name": null
    },
    "password": null,
    "username": null
  },
  "config": {
    "maxAcknowledgementRetries": 3
  },
  "connection": {
    "url": null
  }
}
</pre>
</td>
			<td>Upstream Nubus Provisioning connection configuration</td>
		</tr>
		<tr>
			<td>provisioningApi.auth.existingSecret.keyMapping.password</td>
			<td>string</td>
			<td><pre lang="json">
null
</pre>
</td>
			<td>The key to retrieve the password from. Setting this value allows to use a key with a different name.</td>
		</tr>
		<tr>
			<td>provisioningApi.auth.existingSecret.name</td>
			<td>string</td>
			<td><pre lang="json">
null
</pre>
</td>
			<td>The name of an existing Secret to use for retrieving the password to authenticate with the Provisionig API.  "provisioningApi.auth.password" will be ignored if this value is set.</td>
		</tr>
		<tr>
			<td>provisioningApi.auth.password</td>
			<td>string</td>
			<td><pre lang="json">
null
</pre>
</td>
			<td>The password used to authenticate with the Provisioning API. Either this value or an existing Secret has to be specified.</td>
		</tr>
		<tr>
			<td>provisioningApi.auth.username</td>
			<td>string</td>
			<td><pre lang="json">
null
</pre>
</td>
			<td>Username of the nubus provisioning subscription / this consumer For a given nubus deployment, all provisioning subscription names must be unique.</td>
		</tr>
		<tr>
			<td>provisioningApi.config.maxAcknowledgementRetries</td>
			<td>int</td>
			<td><pre lang="json">
3
</pre>
</td>
			<td>The maximum number of retries for acknowledging a message</td>
		</tr>
		<tr>
			<td>provisioningApi.connection.url</td>
			<td>string</td>
			<td><pre lang="json">
null
</pre>
</td>
			<td>The base URL the provisioning API is reachable at. (e.g. "http://provisioning-api")</td>
		</tr>
		<tr>
			<td>resources.limits.cpu</td>
			<td>string</td>
			<td><pre lang="json">
"4"
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>resources.limits.memory</td>
			<td>string</td>
			<td><pre lang="json">
"4Gi"
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>resources.requests.cpu</td>
			<td>string</td>
			<td><pre lang="json">
"250m"
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>resources.requests.memory</td>
			<td>string</td>
			<td><pre lang="json">
"512Mi"
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>scimConsumer</td>
			<td>object</td>
			<td><pre lang="json">
{
  "config": {
    "groupSync": true,
    "logLevel": "INFO",
    "prefill": true
  },
  "image": {
    "imagePullPolicy": "",
    "registry": "",
    "repository": "nubus-dev/images/scim-consumer",
    "sha256": null,
    "tag": "latest"
  }
}
</pre>
</td>
			<td>Container image configuration</td>
		</tr>
		<tr>
			<td>scimConsumer.config.prefill</td>
			<td>bool</td>
			<td><pre lang="json">
true
</pre>
</td>
			<td>Toggle prefill for the provisioning subscription If activated, the consumer will recieve a synthetic "create" event for all existing objets in the Domain before recieving live events.</td>
		</tr>
		<tr>
			<td>scimConsumer.image.sha256</td>
			<td>string</td>
			<td><pre lang="json">
null
</pre>
</td>
			<td>Define image sha256 as an alternative to `tag`</td>
		</tr>
		<tr>
			<td>scimServer</td>
			<td>object</td>
			<td><pre lang="json">
{
  "auth": {
    "clientId": null,
    "enabled": true,
    "existingSecret": {
      "keyMapping": {
        "password": null
      },
      "name": null
    },
    "oidcTokenUrl": null,
    "password": null
  },
  "connection": {
    "url": null
  }
}
</pre>
</td>
			<td>Downstream SCIM Service connection configuration</td>
		</tr>
		<tr>
			<td>scimServer.auth.clientId</td>
			<td>string</td>
			<td><pre lang="json">
null
</pre>
</td>
			<td>Service account client ID (username)</td>
		</tr>
		<tr>
			<td>scimServer.auth.enabled</td>
			<td>bool</td>
			<td><pre lang="json">
true
</pre>
</td>
			<td>Disable authentication with the SCIM Server for testing purposes</td>
		</tr>
		<tr>
			<td>scimServer.auth.existingSecret.keyMapping.password</td>
			<td>string</td>
			<td><pre lang="json">
null
</pre>
</td>
			<td>The key to retrieve the password from. Setting this value allows to use a key with a different name.</td>
		</tr>
		<tr>
			<td>scimServer.auth.existingSecret.name</td>
			<td>string</td>
			<td><pre lang="json">
null
</pre>
</td>
			<td>The name of an existing Secret to use for retrieving the password to authenticate with the SCIM Server.  "scimServer.auth.password" will be ignored if this value is set.</td>
		</tr>
		<tr>
			<td>scimServer.auth.oidcTokenUrl</td>
			<td>string</td>
			<td><pre lang="json">
null
</pre>
</td>
			<td>URL to obtain an OIDC access token from the Identity Provider using the client-credentials-flow.</td>
		</tr>
		<tr>
			<td>scimServer.auth.password</td>
			<td>string</td>
			<td><pre lang="json">
null
</pre>
</td>
			<td>The password used to authenticate with the SCIM Server. Either this value or an existing Secret has to be specified.</td>
		</tr>
		<tr>
			<td>scimServer.connection.url</td>
			<td>string</td>
			<td><pre lang="json">
null
</pre>
</td>
			<td>The base URL the SCIM server is reachable at. (e.g. "http://scim-server")</td>
		</tr>
		<tr>
			<td>serviceAccount.annotations</td>
			<td>object</td>
			<td><pre lang="json">
{}
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>serviceAccount.automountServiceAccountToken</td>
			<td>bool</td>
			<td><pre lang="json">
false
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>serviceAccount.create</td>
			<td>bool</td>
			<td><pre lang="json">
true
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>serviceAccount.labels</td>
			<td>object</td>
			<td><pre lang="json">
{}
</pre>
</td>
			<td>Additional custom labels for the ServiceAccount.</td>
		</tr>
		<tr>
			<td>serviceAccount.name</td>
			<td>string</td>
			<td><pre lang="json">
""
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>tolerations</td>
			<td>list</td>
			<td><pre lang="json">
[]
</pre>
</td>
			<td></td>
		</tr>
	</tbody>
</table>

