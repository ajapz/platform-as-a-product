variable "environment" {
  description = "Environment name, for example prod or stage."
  type        = string
}

variable "namespaces" {
  description = "Namespace configuration map keyed by namespace name."
  type = map(object({
    owner           = string
    tier            = string
    cost_center     = string
    oncall          = string
    data_class      = string
    cpu_limit       = string
    memory_limit    = string
    cpu_request     = string
    memory_request  = string
    pod_limit       = string
    pvc_limit       = string
    storage_request = string
  }))
}
