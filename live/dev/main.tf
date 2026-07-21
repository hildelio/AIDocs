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

module "lambda" {
  source = "../../modules/lambda"

  function_name = "${var.project}-${var.environment}-hello"
  runtime       = "python3.12"
  handler       = "index.handler"
  filename      = "${path.module}/artifacts/hello.zip"
  iam_role_arn  = module.iam.lambda_execution_role_arn
  tags          = local.tags
}

module "api_gateway" {
  source = "../../modules/api_gateway"

  name                 = "${var.project}-${var.environment}-api"
  lambda_invoke_arn    = module.lambda.invoke_arn
  lambda_function_name = module.lambda.function_name
  tags                 = local.tags
}
