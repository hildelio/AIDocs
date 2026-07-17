variable "bucket_name" {
  description = "Name of the S3 bucket used for Terraform remote state."
  type        = string
}

variable "dynamodb_table_name" {
  description = "Name of the DynamoDB table used for Terraform state locking."
  type        = string
}

variable "aws_region" {
  description = "AWS region where the bootstrap resources will be created."
  type        = string
  default     = "us-east-1"
}

variable "tags" {
  description = "Required tags to apply to bootstrap resources."
  type        = map(string)
  default     = {}
}
