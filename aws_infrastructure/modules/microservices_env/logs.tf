resource "aws_cloudwatch_log_group" "microservices_logs" {
  for_each = toset([
    "api-gateway-app",
    "inventory-app",
    "billing-app",
  ])

  name              = "/ecs/microservices/${var.environment}/${each.key}"
  retention_in_days = 7
}