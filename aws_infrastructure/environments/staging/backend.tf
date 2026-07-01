terraform {
  backend "s3" {
    bucket  = "code-keeper-microservices-project-borsok"
    key     = "environments/staging/terraform.tfstate"
    region  = "eu-north-1"
    encrypt = true
  }
}