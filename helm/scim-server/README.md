# scim-server

![Version: 0.0.1](https://img.shields.io/badge/Version-0.0.1-informational?style=flat-square) ![Type: application](https://img.shields.io/badge/Type-application-informational?style=flat-square)

A Helm chart for the scim server

**Homepage:** <https://www.univention.de/>

## Requirements

| Repository | Name | Version |
|------------|------|---------|
| oci://registry-1.docker.io/bitnamicharts | common | ^2.x.x |

## Values

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| config.logLevel | string | `"INFO"` |  |
| config.loggingConfig | string | `nil` |  |
| config.repeat | bool | `true` |  |
| config.repeatDelay | int | `300` |  |
| configFile.source.bind_dn | string | `"CN=readonly-ad-machine-user,CN=Users,DC=ad,DC=test"` |  |
| configFile.source.group_base | string | `"CN=Groups,DC=ad,DC=test"` |  |
| configFile.source.group_scope | string | `"sub"` |  |
| configFile.source.ldap_uri | string | `"ldap://my_active_directory_server.test:1234"` |  |
| configFile.source.password | string | `nil` |  |
| configFile.source.search_pagesize | int | `500` |  |
| configFile.source.timeout | int | `5` |  |
| configFile.source.user_attrs[0] | string | `"objectGUID"` |  |
| configFile.source.user_attrs[10] | string | `"st"` |  |
| configFile.source.user_attrs[1] | string | `"sAMAccountName"` |  |
| configFile.source.user_attrs[2] | string | `"givenName"` |  |
| configFile.source.user_attrs[3] | string | `"description"` |  |
| configFile.source.user_attrs[4] | string | `"sn"` |  |
| configFile.source.user_attrs[5] | string | `"ou"` |  |
| configFile.source.user_attrs[6] | string | `"o"` |  |
| configFile.source.user_attrs[7] | string | `"street"` |  |
| configFile.source.user_attrs[8] | string | `"l"` |  |
| configFile.source.user_attrs[9] | string | `"postalCode"` |  |
| configFile.source.user_base | string | `"CN=Users,DC=ad,DC=test"` |  |
| configFile.source.user_filter | string | `"(&(objectClass=user)(sAMAccountType=805306368)(givenName=*)(sn=*)(!(userAccountControl:1.2.840.113556.1.4.803:=2)))"` |  |
| configFile.source.user_scope | string | `"sub"` |  |
| configFile.udm.group_ou | string | `"ou=ad-domain-example"` |  |
| configFile.udm.group_primary_key_property | string | `"univentionObjectIdentifier"` |  |
| configFile.udm.password | string | `nil` |  |
| configFile.udm.skip_writes | bool | `false` |  |
| configFile.udm.uri | string | `"https://nubus-kubernetes-deployment.test/univention/udm/"` |  |
| configFile.udm.user | string | `"Administrator"` |  |
| configFile.udm.user_ou | string | `"ou=ad-domain-example"` |  |
| configFile.udm.user_primary_key_property | string | `"univentionObjectIdentifier"` |  |
| containerSecurityContext.allowPrivilegeEscalation | bool | `false` |  |
| containerSecurityContext.capabilities.drop[0] | string | `"ALL"` |  |
| containerSecurityContext.enabled | bool | `false` |  |
| containerSecurityContext.privileged | bool | `false` |  |
| containerSecurityContext.readOnlyRootFilesystem | bool | `true` |  |
| containerSecurityContext.runAsGroup | int | `1000` |  |
| containerSecurityContext.runAsNonRoot | bool | `true` |  |
| containerSecurityContext.runAsUser | int | `1000` |  |
| containerSecurityContext.seccompProfile.type | string | `"RuntimeDefault"` |  |
| extraEnvVars | list | `[]` | Array with extra environment variables to add to containers.  extraEnvVars:   - name: FOO     value: "bar" |
| extraSecrets | list | `[]` | Optionally specify a secret to create (primarily intended to be used in development environments to provide custom certificates) |
| extraVolumeMounts | list | `[]` | Optionally specify an extra list of additional volumeMounts. |
| extraVolumes | list | `[]` | Optionally specify an extra list of additional volumes. |
| global.imagePullPolicy | string | `"IfNotPresent"` | Define an ImagePullPolicy.  Ref.: https://kubernetes.io/docs/concepts/containers/images/#image-pull-policy  |
| global.imagePullSecrets | list | `[]` | Credentials to fetch images from private registry. Ref: https://kubernetes.io/docs/tasks/configure-pod-container/pull-image-private-registry/  imagePullSecrets:   - "docker-registry" |
| global.imageRegistry | string | `"artifacts.software-univention.de"` | Container registry address. |
| image | object | `{"imagePullPolicy":"","registry":"","repository":"nubus-dev/images/scim-server","sha256":null,"tag":"latest"}` | Container image configuration |
| image.sha256 | string | `nil` | Define image sha256 as an alternative to `tag` |
| podSecurityContext.enabled | bool | `false` |  |
| replicaCount | int | `1` |  |
| resources.limits.cpu | string | `"4"` |  |
| resources.limits.memory | string | `"4Gi"` |  |
| serviceAccount.annotations | object | `{}` |  |
| serviceAccount.automountServiceAccountToken | bool | `false` |  |
| serviceAccount.create | bool | `true` |  |
| serviceAccount.labels | object | `{}` | Additional custom labels for the ServiceAccount. |
| serviceAccount.name | string | `""` |  |
| sourceDirectory | object | `{"auth":{"existingSecret":{"keyMapping":{"password":null},"name":null},"password":null}}` | Source connection configuration that is not part of the main config file |
| sourceDirectory.auth.existingSecret.keyMapping.password | string | `nil` | The key to retrieve the password from. Setting this value allows to use a key with a different name. |
| sourceDirectory.auth.existingSecret.name | string | `nil` | The name of an existing Secret to use for retrieving the password to authenticate with the source LDAP directory.  "udm.auth.password" will be ignored if this value is set. |
| sourceDirectory.auth.password | string | `nil` | The password used to authenticate with the source LDAP directory. Either this value or an existing Secret has to be specified. |
| udm | object | `{"auth":{"existingSecret":{"keyMapping":{"password":null},"name":null},"password":null}}` | UDM REST API connection configuration that is not part of the main config file |
| udm.auth.existingSecret.keyMapping.password | string | `nil` | The key to retrieve the password from. Setting this value allows to use a key with a different name. |
| udm.auth.existingSecret.name | string | `nil` | The name of an existing Secret to use for retrieving the password to use with the UDM Rest API.  "udm.auth.password" will be ignored if this value is set. |
| udm.auth.password | string | `nil` | The password used to authenticate with the UDM Rest API. Either this value or an existing Secret has to be specified. |

----------------------------------------------
Autogenerated from chart metadata using [helm-docs v1.14.2](https://github.com/norwoodj/helm-docs/releases/v1.14.2)
