{{- /*
PROVISIONING Keycloak
*/}}

{{- define "scim-server.provisioning.config.nubusBaseUrl" -}}
{{- if .Values.provisioning.config.nubusBaseUrl -}}
{{ .Values.provisioning.config.nubusBaseUrl -}}
{{- else if .Values.global.nubusDeployment -}}
{{ printf "https://%s.%s" .Values.global.subDomains.scim .Values.global.domain }}
{{- else -}}
{{ required ".Values.provisioning.config.nubusBaseUrl is required" .Values.provisioning.config.nubusBaseUrl -}}
{{- end -}}
{{- end -}}

{{- define "scim-server.provisioning.keycloak.connection.protocol" -}}
{{- if .Values.provisioning.keycloak.connection.protocol -}}
{{- .Values.provisioning.keycloak.connection.protocol -}}
{{- else -}}
http
{{- end -}}
{{- end -}}

{{- define "scim-server.provisioning.keycloak.connection.host" -}}
{{- if .Values.provisioning.keycloak.connection.host -}}
{{- .Values.provisioning.keycloak.connection.host -}}
{{- else if .Values.global.nubusDeployment -}}
{{- printf "%s-keycloak" .Release.Name -}}
{{- else if not .Values.provisioning.keycloak.connection.baseUrl -}}
{{- required ".Values.provisioning.keycloak.connection.host must be defined." .Values.provisioning.keycloak.connection.host -}}
{{- end -}}
{{- end -}}

{{- define "scim-server.provisioning.keycloak.connection.port" -}}
{{- if .Values.provisioning.keycloak.connection.port -}}
{{- .Values.provisioning.keycloak.connection.port -}}
{{- else -}}
8080
{{- end -}}
{{- end -}}

{{- define "scim-server.provisioning.keycloak.connection.baseUrl" -}}
{{- if .Values.provisioning.keycloak.connection.baseUrl -}}
{{- .Values.provisioning.keycloak.connection.baseUrl -}}
{{- else if .Values.global.nubusDeployment -}}
{{- $protocol := include "scim-server.provisioning.keycloak.connection.protocol" . -}}
{{- $host := include "scim-server.provisioning.keycloak.connection.host" . -}}
{{- $port := include "scim-server.provisioning.keycloak.connection.port" . -}}
{{- printf "%s://%s:%s" $protocol $host $port -}}
{{- else -}}
{{- required ".Values.provisioning.keycloak.connection.baseUrl must be defined." .Values.provisioning.keycloak.connection.baseUrl -}}
{{- end -}}
{{- end -}}

{{- /*
Keycloak
*/}}

{{- define "scim-server.keycloak.url" -}}
{{- if .Values.config.keycloak.url -}}
{{ .Values.config.keycloak.url -}}
{{- else if .Values.global.nubusDeployment -}}
{{ printf "https://%s.%s/realms/%s" .Values.global.subDomains.keycloak .Values.global.domain (include "scim-server.keycloak.realm" .) }}
{{- else -}}
{{ required ".Values.config.keycloak.url is required" .Values.config.keycloak.url -}}
{{- end -}}
{{- end -}}

{{- define "scim-server.keycloak.realm" -}}
{{- if .Values.config.keycloak.realm -}}
{{- .Values.config.keycloak.realm -}}
{{- else if .Values.global.nubusDeployment -}}
{{- coalesce .Values.config.keycloak.realm .Values.global.keycloak.realm "nubus" -}}
{{- else -}}
{{- required ".Values.config.keycloak.realm must be defined." .Values.config.keycloak.realm -}}
{{- end -}}
{{- end -}}

{{- /*
ingress
*/}}

{{- define "scim-server.ingress.tls.secretName" -}}
{{- if .Values.ingress.tls.secretName -}}
{{- tpl .Values.ingress.tls.secretName . -}}
{{- else if .Values.global.nubusDeployment -}}
{{- printf "%s-scim-server-tls" .Release.Name -}}
{{- else -}}
{{- required ".Values.ingress.tls.secretName must be defined" .Values.ingress.tls.secretName -}}
{{- end -}}
{{- end -}}

{{- /*
udm
*/}}

{{- define "scim-server.udm.url" -}}
{{- if .Values.config.udm.url -}}
{{- .Values.config.udm.url -}}
{{- else if .Values.global.nubusDeployment -}}
{{- printf "http://%s-udm-rest-api:9979/udm/" .Release.Name -}}
{{- else -}}
{{- required ".Values.config.udm.url be defined" .Values.config.udm.url -}}
{{- end -}}
{{- end -}}
