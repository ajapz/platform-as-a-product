module "platform_baseline" {
  source      = "../../modules/platform-baseline"
  environment = "prod"

  namespaces = {
    "payments-prod" = {
      owner           = "payments"
      tier            = "critical"
      cost_center     = "cc-payments"
      oncall          = "payments-oncall"
      data_class      = "restricted"
      cpu_limit       = "40"
      memory_limit    = "80Gi"
      cpu_request     = "30"
      memory_request  = "64Gi"
      pod_limit       = "400"
      pvc_limit       = "80"
      storage_request = "2Ti"
    }
    "search-prod" = {
      owner           = "search"
      tier            = "critical"
      cost_center     = "cc-search"
      oncall          = "search-oncall"
      data_class      = "restricted"
      cpu_limit       = "60"
      memory_limit    = "120Gi"
      cpu_request     = "45"
      memory_request  = "96Gi"
      pod_limit       = "500"
      pvc_limit       = "100"
      storage_request = "4Ti"
    }
    "platform-prod" = {
      owner           = "platform"
      tier            = "core"
      cost_center     = "cc-platform"
      oncall          = "platform-oncall"
      data_class      = "confidential"
      cpu_limit       = "30"
      memory_limit    = "64Gi"
      cpu_request     = "20"
      memory_request  = "40Gi"
      pod_limit       = "300"
      pvc_limit       = "50"
      storage_request = "1Ti"
    }
  }
}

output "managed_namespaces" {
  value = module.platform_baseline.managed_namespaces
}
