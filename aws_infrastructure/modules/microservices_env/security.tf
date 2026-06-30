# 1. ALB Security Group (Internet -> ALB)
resource "aws_security_group" "alb_sg" {
  name        = "alb-security-group-${var.environment}"
  description = "Allow HTTP traffic from the internet"
  vpc_id      = aws_vpc.main_vpc.id

  ingress {
    description = "HTTP from Internet"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# 2. API Gateway Security Group (ALB -> API Gateway)
resource "aws_security_group" "api_gateway_sg" {
  name        = "api-gateway-sg-${var.environment}"
  description = "Allow traffic from ALB to API Gateway"
  vpc_id      = aws_vpc.main_vpc.id

  ingress {
    description     = "Traffic from ALB"
    from_port       = 3000
    to_port         = 3000
    protocol        = "tcp"
    security_groups = [aws_security_group.alb_sg.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# 3. Internal Services Security Group (API Gateway -> Apps -> AmazonMQ)
resource "aws_security_group" "internal_sg" {
  name        = "internal-services-sg-${var.environment}"
  description = "Allow internal traffic for apps and MQ broker"
  vpc_id      = aws_vpc.main_vpc.id

  # Allow API Gateway to talk to backend apps (Inventory/Billing) on 8080
  ingress {
    description     = "Traffic from API Gateway to Apps"
    from_port       = 8080
    to_port         = 8080
    protocol        = "tcp"
    security_groups = [aws_security_group.api_gateway_sg.id]
  }

  # Allow RabbitMQ TLS traffic (5671) from API Gateway AND internal apps
  ingress {
    description     = "RabbitMQ TLS from API Gateway"
    from_port       = 5671
    to_port         = 5671
    protocol        = "tcp"
    security_groups = [aws_security_group.api_gateway_sg.id]
  }

  ingress {
    description = "RabbitMQ TLS from Internal Apps"
    from_port   = 5671
    to_port     = 5671
    protocol    = "tcp"
    self        = true # Allows Billing App in this same SG to talk to MQ
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# 4. Database Security Group (Apps -> RDS)
resource "aws_security_group" "db_sg" {
  name        = "rds-database-sg-${var.environment}"
  description = "Allow PostgreSQL traffic from internal applications only"
  vpc_id      = aws_vpc.main_vpc.id

  ingress {
    description     = "PostgreSQL from internal microservices"
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.internal_sg.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}