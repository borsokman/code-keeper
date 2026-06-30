resource "aws_ecs_task_definition" "api_gateway" {
  family                   = "api-gateway-task-${var.environment}"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "256"
  memory                   = "512"
  execution_role_arn       = aws_iam_role.ecs_execution_role.arn

  runtime_platform {
    operating_system_family = "LINUX"
    cpu_architecture        = "ARM64"
  }

  container_definitions = jsonencode([
    {
      name         = "api-gateway-app"
      image        = "327425719370.dkr.ecr.eu-north-1.amazonaws.com/api-gateway-app-${var.environment}:v1"
      essential    = true
      portMappings = [{ containerPort = 3000, protocol = "tcp" }]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = "/ecs/microservices/${var.environment}/api-gateway-app"
          "awslogs-region"        = "eu-north-1"
          "awslogs-stream-prefix" = "ecs"
        }
      }
      environment = [
        { name = "INVENTORY_URL", value = "http://inventory-app.microservices-${var.environment}.local:8080" },
        { name = "RABBITMQ_HOST", value = split(":", replace(aws_mq_broker.rabbitmq_broker.instances.0.endpoints.0, "amqps://", ""))[0] },
        { name = "RABBITMQ_PORT", value = "5671" },
        { name = "RABBITMQ_USER", value = var.rabbitmq_user }
      ]
      secrets = [
        { name = "RABBITMQ_PASSWORD", valueFrom = aws_ssm_parameter.rabbitmq_password.arn }
      ]
    }
  ])
}

resource "aws_ecs_task_definition" "inventory_app" {
  family                   = "inventory-app-task-${var.environment}"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "256"
  memory                   = "512"
  execution_role_arn       = aws_iam_role.ecs_execution_role.arn

  runtime_platform {
    operating_system_family = "LINUX"
    cpu_architecture        = "ARM64"
  }

  container_definitions = jsonencode([
    {
      name         = "inventory-app"
      image        = "327425719370.dkr.ecr.eu-north-1.amazonaws.com/inventory-app-${var.environment}:v1"
      essential    = true
      portMappings = [{ containerPort = 8080, protocol = "tcp" }]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = "/ecs/microservices/${var.environment}/inventory-app"
          "awslogs-region"        = "eu-north-1"
          "awslogs-stream-prefix" = "ecs"
        }
      }
      environment = [
        { name = "DB_HOST", value = aws_db_instance.inventory_db.address },
        { name = "DB_PORT", value = "5432" },
        { name = "DB_NAME", value = aws_db_instance.inventory_db.db_name },
        { name = "DB_USER", value = aws_db_instance.inventory_db.username }
      ]
      secrets = [
        { name = "DB_PASSWORD", valueFrom = aws_ssm_parameter.inventory_db_password.arn }
      ]
    }
  ])
}

resource "aws_ecs_task_definition" "billing_app" {
  family                   = "billing-app-task-${var.environment}"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "256"
  memory                   = "512"
  execution_role_arn       = aws_iam_role.ecs_execution_role.arn

  runtime_platform {
    operating_system_family = "LINUX"
    cpu_architecture        = "ARM64"
  }

  container_definitions = jsonencode([
    {
      name         = "billing-app"
      image        = "327425719370.dkr.ecr.eu-north-1.amazonaws.com/billing-app-${var.environment}:v1"
      essential    = true
      portMappings = [{ containerPort = 8080, protocol = "tcp" }]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = "/ecs/microservices/${var.environment}/billing-app"
          "awslogs-region"        = "eu-north-1"
          "awslogs-stream-prefix" = "ecs"
        }
      }
      environment = [
        { name = "PYTHONUNBUFFERED", value = "1" },
        { name = "DB_HOST", value = aws_db_instance.billing_db.address },
        { name = "DB_PORT", value = "5432" },
        { name = "DB_NAME", value = aws_db_instance.billing_db.db_name },
        { name = "DB_USER", value = aws_db_instance.billing_db.username },
        { name = "RABBITMQ_HOST", value = split(":", replace(aws_mq_broker.rabbitmq_broker.instances.0.endpoints.0, "amqps://", ""))[0] },
        { name = "RABBITMQ_PORT", value = "5671" },
        { name = "RABBITMQ_USER", value = var.rabbitmq_user }
      ]
      secrets = [
        { name = "DB_PASSWORD", valueFrom = aws_ssm_parameter.billing_db_password.arn },
        { name = "RABBITMQ_PASSWORD", valueFrom = aws_ssm_parameter.rabbitmq_password.arn }
      ]
    }
  ])
}
