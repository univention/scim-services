load("ext://helm_resource", "helm_resource")

helm_resource(
    "scim-consumer",
    chart="./helm/scim-consumer/",
    deps=[
      "tilt-values.yaml",
      "helm/scim-consumer/",
    ],
    flags=[
      "--values", "tilt-values.yaml",
      "--set", "global.secrets.masterPassword=univention"
    ],
    image_deps=[
      "artifacts.software-univention.de/nubus-dev/images/scim-consumer:latest",
    ],
    image_keys=[
      ("scimConsumer.image.registry", "scimConsumer.image.repository", "scimConsumer.image.tag"),
    ],
)

docker_build(
    "artifacts.software-univention.de/nubus-dev/images/scim-consumer:latest",
    "./",
    dockerfile="./docker/scim-consumer/Dockerfile",
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
