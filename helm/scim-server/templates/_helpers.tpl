{{- /*
PROVISIONING Keycloak
*/}}

{{- define "scim-server.keycloak.url" -}}
{{- if .Values.config.keycloak.url -}}
{{ .Values.config.keycloak.url -}}
{{- else if .Values.global.nubusDeployment -}}
{{ printf "http://%s-keycloak:8080/realms/%s" .Release.Name  (include "scim-server.keycloak.realm" .) }}
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
PROVISIONING ingress
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
