variable "bucket_name" {
  description = "Base name for the S3 bucket."
  type        = string
}

variable "tags" {
  description = "A map of tags to assign to the bucket."
  type        = map(string)
  default     = {}
}
