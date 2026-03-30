module "platform_baseline" {
  source      = "../../modules/platform-baseline"
  environment = "dev"

  namespaces = {
    "payments-dev" = {
      owner           = "payments"
      tier            = "standard"
      cost_center     = "cc-payments"
      oncall          = "payments-oncall"
      data_class      = "internal"
      cpu_limit       = "12"
      memory_limit    = "24Gi"
      cpu_request     = "8"
      memory_request  = "16Gi"
      pod_limit       = "180"
      pvc_limit       = "30"
      storage_request = "500Gi"
    }
    "search-dev" = {
      owner           = "search"
      tier            = "standard"
      cost_center     = "cc-search"
      oncall          = "search-oncall"
      data_class      = "internal"
      cpu_limit       = "16"
      memory_limit    = "32Gi"
      cpu_request     = "10"
      memory_request  = "20Gi"
      pod_limit       = "220"
      pvc_limit       = "40"
      storage_request = "700Gi"
    }
    "platform-dev" = {
      owner           = "platform"
      tier            = "core"
      cost_center     = "cc-platform"
      oncall          = "platform-oncall"
      data_class      = "internal"
      cpu_limit       = "10"
      memory_limit    = "20Gi"
      cpu_request     = "6"
      memory_request  = "12Gi"
      pod_limit       = "150"
      pvc_limit       = "25"
      storage_request = "400Gi"
    }
  }
}

output "managed_namespaces" {
  value = module.platform_baseline.managed_namespaces
}
