package platform.kubernetes

deny[msg] {
  input.kind == "Deployment"
  some i
  container := input.spec.template.spec.containers[i]
  endswith(container.image, ":latest")
  msg := sprintf("deployment %s container %s uses latest image tag", [input.metadata.name, container.name])
}

deny[msg] {
  input.kind == "Deployment"
  some i
  container := input.spec.template.spec.containers[i]
  not container.readinessProbe
  msg := sprintf("deployment %s container %s missing readinessProbe", [input.metadata.name, container.name])
}

deny[msg] {
  input.kind == "Deployment"
  some i
  container := input.spec.template.spec.containers[i]
  not container.livenessProbe
  msg := sprintf("deployment %s container %s missing livenessProbe", [input.metadata.name, container.name])
}
