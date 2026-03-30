module "platform_baseline" {
  source      = "../../modules/platform-baseline"
  environment = "stage"

  namespaces = {
    "payments-stage" = {
      owner           = "payments"
      tier            = "critical"
      cost_center     = "cc-payments"
      oncall          = "payments-oncall"
      data_class      = "confidential"
      cpu_limit       = "24"
      memory_limit    = "48Gi"
      cpu_request     = "18"
      memory_request  = "36Gi"
      pod_limit       = "280"
      pvc_limit       = "50"
      storage_request = "1Ti"
    }
    "search-stage" = {
      owner           = "search"
      tier            = "critical"
      cost_center     = "cc-search"
      oncall          = "search-oncall"
      data_class      = "confidential"
      cpu_limit       = "32"
      memory_limit    = "64Gi"
      cpu_request     = "24"
      memory_request  = "48Gi"
      pod_limit       = "320"
      pvc_limit       = "60"
      storage_request = "1500Gi"
    }
    "platform-stage" = {
      owner           = "platform"
      tier            = "core"
      cost_center     = "cc-platform"
      oncall          = "platform-oncall"
      data_class      = "internal"
      cpu_limit       = "18"
      memory_limit    = "36Gi"
      cpu_request     = "12"
      memory_request  = "24Gi"
      pod_limit       = "220"
      pvc_limit       = "35"
      storage_request = "700Gi"
    }
  }
}

output "managed_namespaces" {
  value = module.platform_baseline.managed_namespaces
}
