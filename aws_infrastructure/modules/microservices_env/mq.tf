resource "aws_mq_broker" "rabbitmq_broker" {
  broker_name                = "rabbitmq"
  engine_type                = "RabbitMQ"
  engine_version             = "3.13" # Or your preferred stable version
  host_instance_type         = "mq.m7g.medium"
  auto_minor_version_upgrade = true
  security_groups            = [aws_security_group.internal_sg.id]
  subnet_ids                 = [aws_subnet.private_1.id] # Sits securely in your private subnet

  user {
    username = var.rabbitmq_user
    password = var.rabbitmq_password
  }
}