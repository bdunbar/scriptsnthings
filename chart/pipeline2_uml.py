import json

data = {
  "name": "build-doc",
  "attributes": {
    "rules": [
      { "if": "$CI_COMMIT_BRANCH == \"development\"" }
    ],
    "stage": "build",
    "image": "$AWS_REGISTRY/irad/augustus/vitis:$VITIS_VER",
    "before_script": [
      "apt-get update && apt-get install -y doxygen"
    ],
    "script": [
      "source /etc/profile.d/settings64-Vitis.sh",
      "make O=build-doc doc"
    ],
    "tags": [
      "env=$RUNNER_ENV",
      "project=$PROJECT",
      "dept=$DEPT",
      "cluster=$CLUSTER",
      "arch=amd64"
    ],
    "artifacts": {
      "paths": [
        "build-doc/docs"
      ],
      "when": "always",
      "expire_in": "1 month"
    }
  }
}

uml = "@startuml\n"
uml += f"class {data['name']} {{\n"

for key, value in data['attributes'].items():
    if isinstance(value, list):
        uml += f"  {key}: {value}\n"
    elif isinstance(value, dict):
        uml += f"  {key}: {json.dumps(value)}\n"
    else:
        uml += f"  {key}: {value}\n"

uml += "}\n"
uml += "@enduml"

# Save the UML to a file
with open('diagram.puml', 'w') as file:
    file.write(uml)
