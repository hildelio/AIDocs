variable "project" {
  description = "Project name"
  type        = string
}

variable "environment" {
  description = "Environment name"
  type        = string
}

variable "tags" {
  description = "Tags to apply"
  type        = map(string)
}

variable "s3_bucket_id" {
  description = "ID of the S3 bucket to trigger the lambda"
  type        = string
}

variable "s3_bucket_arn" {
  description = "ARN of the S3 bucket to trigger the lambda"
  type        = string
}

variable "dynamodb_table_arn" {
  description = "ARN of the DynamoDB table"
  type        = string
}

variable "artifact_path" {
  description = "Path to the zipped application artifact"
  type        = string
}
