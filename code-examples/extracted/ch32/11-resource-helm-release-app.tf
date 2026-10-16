resource "helm_release" "app" {
  name       = "backend"
  repository = "..."
  chart      = "backend"
}
