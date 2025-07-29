load("ext://helm_resource", "helm_resource")

helm_resource(
    "scim-client",
    chart="./helm/scim-client/",
    deps=[
      "tilt-values.yaml",
      "helm/scim-client/",
    ],
    flags=[
      "--values", "tilt-values.yaml",
      "--set", "global.secrets.masterPassword=univention"
    ],
    image_deps=[
      "artifacts.software-univention.de/nubus-dev/images/scim-client:latest",
    ],
    image_keys=[
      ("scimClient.image.registry", "scimClient.image.repository", "scimClient.image.tag"),
    ],
)

docker_build(
    "artifacts.software-univention.de/nubus-dev/images/scim-client:latest",
    "./",
    dockerfile="./docker/scim-client/Dockerfile",
)

helm_resource(
    "scim-dev-server",
    chart="./helm/scim-dev-server/",
    deps=[
      "tilt-values.yaml",
      "helm/scim-dev-server/",
    ],
    flags=[
      "--values", "tilt-values.yaml",
      "--set", "global.secrets.masterPassword=univention"
    ],
    image_deps=[
      "artifacts.software-univention.de/nubus-dev/images/scim-dev-server:latest",
    ],
    image_keys=[
      ("scimDevServer.image.registry", "scimDevServer.image.repository", "scimDevServer.image.tag"),
    ],
)

docker_build(
    "artifacts.software-univention.de/nubus-dev/images/scim-dev-server:latest",
    "./",
    dockerfile="./docker/scim-dev-server/Dockerfile",
)
