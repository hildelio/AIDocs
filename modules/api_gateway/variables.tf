variable "name" {
  description = "Name of the API Gateway HTTP API."
  type        = string
}

variable "lambda_invoke_arn" {
  description = "Invocation ARN of the Lambda function. Must be sourced from module.lambda.invoke_arn — never hardcoded."
  type        = string
}

variable "lambda_function_name" {
  description = "Name of the Lambda function. Must be sourced from module.lambda.function_name — never hardcoded."
  type        = string
}

variable "tags" {
  description = "Mandatory platform tags: project, environment, owner, cost_center, managed_by."
  type        = map(string)
}
