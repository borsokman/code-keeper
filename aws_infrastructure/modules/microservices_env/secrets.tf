resource "aws_ssm_parameter" "inventory_db_password" {
  name  = "/microservices/inventory-db/password"
  type  = "SecureString"
  value = var.db_password_inventory
}

resource "aws_ssm_parameter" "billing_db_password" {
  name  = "/microservices/billing-db/password"
  type  = "SecureString"
  value = var.db_password_billing
}

resource "aws_ssm_parameter" "rabbitmq_password" {
  name  = "/microservices/rabbitmq/password"
  type  = "SecureString"
  value = var.rabbitmq_password
}

resource "aws_iam_role_policy" "ecs_secrets_policy" {
  name = "ecs-secrets-policy"
  role = aws_iam_role.ecs_execution_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ssm:GetParameters",
          "kms:Decrypt"
        ]
        Resource = [
          aws_ssm_parameter.inventory_db_password.arn,
          aws_ssm_parameter.billing_db_password.arn,
          aws_ssm_parameter.rabbitmq_password.arn
        ]
      }
    ]
  })
}