variable "kubeconfig_path" {
  description = "Path to kubeconfig file used by Terraform."
  type        = string
}

variable "kube_context" {
  description = "Kubernetes context for the target development cluster."
  type        = string
}
