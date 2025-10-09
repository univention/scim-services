# scim-server

A Helm chart for the scim server

- **Version**: 0.0.1
- **Type**: application
- **AppVersion**:
- **Homepage:** <https://www.univention.de/>

## TL;DR

```console
helm upgrade --install scim-server oci://artifacts.software-univention.de/nubus/charts/scim-server
```

## Introduction

This chart does install the Nubus SCIM Server.

This service provides a REST API implementing the SCIM Protocol.

## Installing

To install the chart with the release name `scim-server`:

```console
helm upgrade --install scim-server oci://artifacts.software-univention.de/nubus/charts/scim-server
```

## Uninstalling

To uninstall the chart with the release name `scim-server`:

```console
helm uninstall scim-server
```

## Requirements

| Repository | Name | Version |
|------------|------|---------|
| oci://artifacts.software-univention.de/nubus-dev/charts | nubus-common | 0.28.0-pre-dpapoutsis-nubus-common-templated-keymapping |

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
			<td>additionalAnnotations</td>
			<td>object</td>
			<td><pre lang="json">
{}
</pre>
</td>
			<td>Additional custom annotations to add to all deployed objects.</td>
		</tr>
		<tr>
			<td>additionalLabels</td>
			<td>object</td>
			<td><pre lang="json">
{}
</pre>
</td>
			<td>Additional custom labels to add to all deployed objects.</td>
		</tr>
		<tr>
			<td>config.apiPrefix</td>
			<td>string</td>
			<td><pre lang="json">
"/scim/v2"
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>config.auth.allowedAudience</td>
			<td>string</td>
			<td><pre lang="json">
""
</pre>
</td>
			<td>Only tokens with the given audience are valid</td>
		</tr>
		<tr>
			<td>config.auth.allowedCliendId</td>
			<td>string</td>
			<td><pre lang="json">
""
</pre>
</td>
			<td>Only tokens with the given clientId are valid</td>
		</tr>
		<tr>
			<td>config.auth.enabled</td>
			<td>bool</td>
			<td><pre lang="json">
true
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>config.corsOrigins</td>
			<td>string</td>
			<td><pre lang="json">
"[\"*\"]"
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>config.externalId</td>
			<td>object</td>
			<td><pre lang="json">
{
  "groupMapping": null,
  "userMapping": null
}
</pre>
</td>
			<td>External ID mapping configuration for SCIM filtering</td>
		</tr>
		<tr>
			<td>config.externalId.groupMapping</td>
			<td>string</td>
			<td><pre lang="json">
null
</pre>
</td>
			<td>UDM property to map to SCIM Group externalId. If not set, externalID will not be mapped. Example: "description"</td>
		</tr>
		<tr>
			<td>config.externalId.userMapping</td>
			<td>string</td>
			<td><pre lang="json">
null
</pre>
</td>
			<td>UDM property to map to SCIM User externalId. If not set, externalID will not be mapped. Example: "employeeNumber"</td>
		</tr>
		<tr>
			<td>config.host</td>
			<td>string</td>
			<td><pre lang="json">
"https://scim.example.test"
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>config.listenAddress</td>
			<td>string</td>
			<td><pre lang="json">
"0.0.0.0"
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>config.logLevel</td>
			<td>string</td>
			<td><pre lang="json">
"INFO"
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>config.port</td>
			<td>int</td>
			<td><pre lang="json">
80
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>config.roles.userMapping</td>
			<td>string</td>
			<td><pre lang="json">
null
</pre>
</td>
			<td>UDM property to map to SCIM User roles. If not set, roles will not be mapped. Example: "scimRoles"</td>
		</tr>
		<tr>
			<td>containerSecurityContext.allowPrivilegeEscalation</td>
			<td>bool</td>
			<td><pre lang="json">
false
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>containerSecurityContext.capabilities.drop[0]</td>
			<td>string</td>
			<td><pre lang="json">
"ALL"
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>containerSecurityContext.enabled</td>
			<td>bool</td>
			<td><pre lang="json">
true
</pre>
</td>
			<td></td>
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
			<td></td>
		</tr>
		<tr>
			<td>containerSecurityContext.runAsGroup</td>
			<td>int</td>
			<td><pre lang="json">
1000
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>containerSecurityContext.runAsNonRoot</td>
			<td>bool</td>
			<td><pre lang="json">
true
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>containerSecurityContext.runAsUser</td>
			<td>int</td>
			<td><pre lang="json">
1000
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>containerSecurityContext.seccompProfile.type</td>
			<td>string</td>
			<td><pre lang="json">
"RuntimeDefault"
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>docu.auth.clientId</td>
			<td>string</td>
			<td><pre lang="json">
null
</pre>
</td>
			<td>clientId and clientSecret will be used in swagger UI to allow login when testing the API</td>
		</tr>
		<tr>
			<td>docu.auth.existingSecret.keyMapping.clientSecret</td>
			<td>string</td>
			<td><pre lang="json">
null
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>docu.auth.existingSecret.name</td>
			<td>string</td>
			<td><pre lang="json">
null
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>docu.enabled</td>
			<td>bool</td>
			<td><pre lang="json">
false
</pre>
</td>
			<td>If enabled swagger UI will be availble at the /docs and /redoc endpoint</td>
		</tr>
		<tr>
			<td>extraEnvVars</td>
			<td>list</td>
			<td><pre lang="json">
[]
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>extraVolumeMounts</td>
			<td>list</td>
			<td><pre lang="json">
[]
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>extraVolumes</td>
			<td>list</td>
			<td><pre lang="json">
[]
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>global.certManagerIssuer</td>
			<td>string</td>
			<td><pre lang="json">
""
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>global.domain</td>
			<td>string</td>
			<td><pre lang="json">
""
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>global.imagePullPolicy</td>
			<td>string</td>
			<td><pre lang="json">
null
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
			<td>global.ingressClass</td>
			<td>string</td>
			<td><pre lang="json">
""
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>global.nubusDeployment</td>
			<td>bool</td>
			<td><pre lang="json">
false
</pre>
</td>
			<td></td>
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
			<td>ingress.annotations</td>
			<td>object</td>
			<td><pre lang="json">
{}
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>ingress.certManager.enabled</td>
			<td>bool</td>
			<td><pre lang="json">
true
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>ingress.certManager.issuerRef.kind</td>
			<td>string</td>
			<td><pre lang="json">
"ClusterIssuer"
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>ingress.certManager.issuerRef.name</td>
			<td>string</td>
			<td><pre lang="json">
""
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>ingress.enabled</td>
			<td>bool</td>
			<td><pre lang="json">
true
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>ingress.host</td>
			<td>string</td>
			<td><pre lang="json">
""
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>ingress.ingressClassName</td>
			<td>string</td>
			<td><pre lang="json">
""
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>ingress.tls.enabled</td>
			<td>bool</td>
			<td><pre lang="json">
true
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>ingress.tls.secretName</td>
			<td>string</td>
			<td><pre lang="json">
""
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>keycloak.connection.realm</td>
			<td>string</td>
			<td><pre lang="json">
""
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>keycloak.connection.url</td>
			<td>string</td>
			<td><pre lang="json">
""
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>podSecurityContext.enabled</td>
			<td>bool</td>
			<td><pre lang="json">
true
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>podSecurityContext.fsGroup</td>
			<td>int</td>
			<td><pre lang="json">
1000
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>podSecurityContext.fsGroupChangePolicy</td>
			<td>string</td>
			<td><pre lang="json">
"Always"
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>podSecurityContext.sysctls[0].name</td>
			<td>string</td>
			<td><pre lang="json">
"net.ipv4.ip_unprivileged_port_start"
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>podSecurityContext.sysctls[0].value</td>
			<td>string</td>
			<td><pre lang="json">
"1"
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>probes.liveness.enabled</td>
			<td>bool</td>
			<td><pre lang="json">
true
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>probes.liveness.failureThreshold</td>
			<td>int</td>
			<td><pre lang="json">
10
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>probes.liveness.initialDelaySeconds</td>
			<td>int</td>
			<td><pre lang="json">
15
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>probes.liveness.periodSeconds</td>
			<td>int</td>
			<td><pre lang="json">
20
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>probes.liveness.successThreshold</td>
			<td>int</td>
			<td><pre lang="json">
1
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>probes.liveness.tcpSocket.port</td>
			<td>int</td>
			<td><pre lang="json">
80
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>probes.liveness.timeoutSeconds</td>
			<td>int</td>
			<td><pre lang="json">
5
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>probes.readiness.enabled</td>
			<td>bool</td>
			<td><pre lang="json">
true
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>probes.readiness.failureThreshold</td>
			<td>int</td>
			<td><pre lang="json">
10
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>probes.readiness.initialDelaySeconds</td>
			<td>int</td>
			<td><pre lang="json">
15
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>probes.readiness.periodSeconds</td>
			<td>int</td>
			<td><pre lang="json">
20
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>probes.readiness.successThreshold</td>
			<td>int</td>
			<td><pre lang="json">
1
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>probes.readiness.tcpSocket.port</td>
			<td>int</td>
			<td><pre lang="json">
80
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>probes.readiness.timeoutSeconds</td>
			<td>int</td>
			<td><pre lang="json">
5
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>probes.startup.enabled</td>
			<td>bool</td>
			<td><pre lang="json">
true
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>probes.startup.failureThreshold</td>
			<td>int</td>
			<td><pre lang="json">
10
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>probes.startup.initialDelaySeconds</td>
			<td>int</td>
			<td><pre lang="json">
15
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>probes.startup.periodSeconds</td>
			<td>int</td>
			<td><pre lang="json">
20
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>probes.startup.successThreshold</td>
			<td>int</td>
			<td><pre lang="json">
1
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>probes.startup.tcpSocket.port</td>
			<td>int</td>
			<td><pre lang="json">
80
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>probes.startup.timeoutSeconds</td>
			<td>int</td>
			<td><pre lang="json">
5
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>replicaCount</td>
			<td>int</td>
			<td><pre lang="json">
1
</pre>
</td>
			<td></td>
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
			<td>scimServer.image.pullPolicy</td>
			<td>string</td>
			<td><pre lang="json">
""
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>scimServer.image.registry</td>
			<td>string</td>
			<td><pre lang="json">
""
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>scimServer.image.repository</td>
			<td>string</td>
			<td><pre lang="json">
"nubus-dev/images/scim-server"
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>scimServer.image.sha256</td>
			<td>string</td>
			<td><pre lang="json">
null
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>scimServer.image.tag</td>
			<td>string</td>
			<td><pre lang="json">
"latest"
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>scimServer.waitForDependency.image.pullPolicy</td>
			<td>string</td>
			<td><pre lang="json">
""
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>scimServer.waitForDependency.image.registry</td>
			<td>string</td>
			<td><pre lang="json">
""
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>scimServer.waitForDependency.image.repository</td>
			<td>string</td>
			<td><pre lang="json">
"nubus/images/wait-for-dependency"
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>scimServer.waitForDependency.image.sha256</td>
			<td>string</td>
			<td><pre lang="json">
null
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>scimServer.waitForDependency.image.tag</td>
			<td>string</td>
			<td><pre lang="json">
"0.35.0@sha256:61dfaea28a2b150459138dfd6a554ce53850cee05ef2a72ab47bbe23f2a92d0d"
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>service.annotations</td>
			<td>object</td>
			<td><pre lang="json">
{}
</pre>
</td>
			<td></td>
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
			<td></td>
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
		<tr>
			<td>udm.auth.existingSecret.keyMapping.password</td>
			<td>string</td>
			<td><pre lang="json">
null
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>udm.auth.existingSecret.name</td>
			<td>string</td>
			<td><pre lang="json">
null
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>udm.auth.password</td>
			<td>string</td>
			<td><pre lang="json">
null
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>udm.auth.username</td>
			<td>string</td>
			<td><pre lang="json">
"Administrator"
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>udm.connection.url</td>
			<td>string</td>
			<td><pre lang="json">
""
</pre>
</td>
			<td></td>
		</tr>
	</tbody>
</table>

