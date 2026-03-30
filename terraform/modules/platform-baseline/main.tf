resource "kubernetes_namespace_v1" "managed" {
  for_each = var.namespaces

  metadata {
    name = each.key
    labels = {
      "platform.company.io/managed"     = "true"
      "platform.company.io/environment" = var.environment
      "platform.company.io/owner"       = each.value.owner
      "platform.company.io/tier"        = each.value.tier
      "istio-injection"                 = "enabled"
    }
    annotations = {
      "platform.company.io/cost-center"         = each.value.cost_center
      "platform.company.io/oncall"              = each.value.oncall
      "platform.company.io/data-classification" = each.value.data_class
    }
  }
}

resource "kubernetes_resource_quota_v1" "namespace_quota" {
  for_each = var.namespaces

  metadata {
    name      = "compute-quota"
    namespace = kubernetes_namespace_v1.managed[each.key].metadata[0].name
  }

  spec {
    hard = {
      "limits.cpu"             = each.value.cpu_limit
      "limits.memory"          = each.value.memory_limit
      "requests.cpu"           = each.value.cpu_request
      "requests.memory"        = each.value.memory_request
      "requests.storage"       = each.value.storage_request
      "persistentvolumeclaims" = each.value.pvc_limit
      "pods"                   = each.value.pod_limit
    }
  }
}

resource "kubernetes_limit_range_v1" "default_limits" {
  for_each = var.namespaces

  metadata {
    name      = "default-limits"
    namespace = kubernetes_namespace_v1.managed[each.key].metadata[0].name
  }

  spec {
    limit {
      type = "Container"

      default = {
        cpu    = "500m"
        memory = "512Mi"
      }

      default_request = {
        cpu    = "100m"
        memory = "128Mi"
      }
    }
  }
}
