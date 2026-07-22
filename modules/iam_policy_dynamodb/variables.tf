variable "role_name" {
  description = "Name of the IAM role to attach the policy to. Must be sourced from module.iam.lambda_execution_role_name."
  type        = string
}

variable "table_arn" {
  description = "ARN of the DynamoDB table to grant CRUD access to. Must be sourced from module.dynamodb.table_arn."
  type        = string
}

variable "tags" {
  description = "Mandatory platform tags: project, environment, owner, cost_center, managed_by."
  type        = map(string)
}
