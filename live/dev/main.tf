locals {
  tags = {
    project     = var.project
    environment = var.environment
    owner       = var.owner
    cost_center = var.cost_center
    managed_by  = "terraform"
  }
}

module "iam" {
  source = "../../modules/iam"

  project     = var.project
  environment = var.environment
  owner       = var.owner
  cost_center = var.cost_center
}

module "s3" {
  source = "../../modules/s3"

  bucket_name = "app-data"
  tags        = local.tags
}
