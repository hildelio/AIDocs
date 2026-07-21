variable "function_name" {
  description = "Name of the Lambda function."
  type        = string
}

variable "runtime" {
  description = "Lambda runtime identifier (e.g., python3.12)."
  type        = string
}

variable "handler" {
  description = "Function entrypoint in the form file.method (e.g., index.handler)."
  type        = string
}

variable "filename" {
  description = "Path to the deployment package (.zip file)."
  type        = string
}

variable "iam_role_arn" {
  description = "ARN of the IAM execution role for the Lambda function. Must be sourced from the IAM module output."
  type        = string
}

variable "tags" {
  description = "Mandatory platform tags: project, environment, owner, cost_center, managed_by."
  type        = map(string)
}
