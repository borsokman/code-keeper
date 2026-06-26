resource "aws_ecr_repository" "api_gateway" {
  name                 = "api-gateway-app"
  image_tag_mutability = "MUTABLE"
  force_delete         = true
  image_scanning_configuration { scan_on_push = true }
}

resource "aws_ecr_repository" "inventory_app" {
  name                 = "inventory-app"
  image_tag_mutability = "MUTABLE"
  force_delete         = true
  image_scanning_configuration { scan_on_push = true }
}

resource "aws_ecr_repository" "billing_app" {
  name                 = "billing-app"
  image_tag_mutability = "MUTABLE"
  force_delete         = true
  image_scanning_configuration { scan_on_push = true }
}

# These blocks dynamically fetch your Account ID and Region
data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

output "ecr_registry_url" {
  value = "${data.aws_caller_identity.current.account_id}.dkr.ecr.${data.aws_region.current.name}.amazonaws.com"
}
