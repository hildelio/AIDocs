variable "role_name" {
  description = "Name of the IAM role to attach the policy to."
  type        = string
}

variable "bucket_arn" {
  description = "ARN of the S3 bucket to allow PutObject."
  type        = string
}

variable "tags" {
  description = "Tags for the policy."
  type        = map(string)
}
