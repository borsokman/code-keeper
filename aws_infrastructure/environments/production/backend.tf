terraform {
  backend "s3" {
    bucket  = "code-keeper-microservices-project-borsok"
    key     = "environments/production/terraform.tfstate"
    region  = "eu-north-1"
    encrypt = true
  }
}