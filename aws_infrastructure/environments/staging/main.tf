terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "eu-north-1"
}

module "staging_infrastructure" {
  source = "../../modules/microservices_env"

  # Pass the environment identifier
  environment = "staging"

  # Pass your secret variables (can be mapped via secret TF_VAR_ environment variables in GitLab)
  rabbitmq_user         = "staging_mq_user"
  rabbitmq_password     = var.rabbitmq_password
  db_password_inventory = var.db_password_inventory
  db_password_billing   = var.db_password_billing
}

# Declarations for variables passed into the module from tfvars/GitLab
variable "rabbitmq_password" { type = string; sensitive = true }
variable "db_password_inventory" { type = string; sensitive = true }
variable "db_password_billing" { type = string; sensitive = true }