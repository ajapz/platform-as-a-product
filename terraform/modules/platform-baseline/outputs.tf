output "managed_namespaces" {
  description = "List of namespaces managed by the platform baseline module."
  value       = [for n in kubernetes_namespace_v1.managed : n.metadata[0].name]
}
