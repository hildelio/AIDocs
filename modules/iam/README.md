# IAM Module

## Description

This module creates a minimal Lambda execution role with a trust policy for the `lambda.amazonaws.com` service principal. It is intentionally scoped to the least-privilege role creation requested for the project.

## Usage

```hcl
module "iam" {
  source = "../../modules/iam"

  project     = var.project
  environment = var.environment
  owner       = var.owner
  cost_center = var.cost_center
}
```

## Inputs

| Name | Description | Type | Default |
| --- | --- | --- | --- |
| `project` | Project identifier used for naming resources. | `string` | n/a |
| `environment` | Environment name for the deployment. | `string` | n/a |
| `owner` | Team or owner responsible for the resources. | `string` | n/a |
| `cost_center` | Cost center tag for the resources. | `string` | n/a |

## Outputs

| Name | Description |
| --- | --- |
| `lambda_execution_role_arn` | ARN of the Lambda execution role. |
| `lambda_execution_role_name` | Name of the Lambda execution role. |
