terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    tls = {
      source  = "hashicorp/tls"
      version = "~> 4.0"
    }
  }
}

provider "aws" {
  region = "eu-north-1"
}

terraform {
  backend "s3" {
    bucket         = "your-unique-terraform-state-bucket" # Must be created in AWS manually first
    key            = "state/terraform.tfstate"
    region         = "eu-north-1"
    encrypt        = true
  }
}