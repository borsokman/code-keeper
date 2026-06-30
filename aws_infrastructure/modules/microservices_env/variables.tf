variable "rabbitmq_user" {
  type        = string
  description = "Username for Amazon MQ RabbitMQ"
}

variable "rabbitmq_password" {
  type        = string
  description = "Password for Amazon MQ RabbitMQ"
  sensitive   = true
}

variable "db_password_inventory" {
  type        = string
  description = "Password for the Inventory RDS PostgreSQL database"
  sensitive   = true
}

variable "db_password_billing" {
  type        = string
  description = "Password for the Billing RDS PostgreSQL database"
  sensitive   = true
}

variable "environment" {
  type        = string
  description = "The deployment environment (staging or production)"
}