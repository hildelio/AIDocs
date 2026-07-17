output "bootstrap_bucket_name" {
  description = "S3 bucket name configured for Terraform remote state."
  value       = aws_s3_bucket.terraform_state.bucket
}

output "bootstrap_bucket_arn" {
  description = "ARN of the S3 bucket configured for Terraform remote state."
  value       = aws_s3_bucket.terraform_state.arn
}

output "bootstrap_dynamodb_table_name" {
  description = "DynamoDB table name configured for Terraform state locking."
  value       = aws_dynamodb_table.terraform_state_lock.name
}

output "bootstrap_dynamodb_table_arn" {
  description = "ARN of the DynamoDB table configured for Terraform state locking."
  value       = aws_dynamodb_table.terraform_state_lock.arn
}

output "bootstrap_region" {
  description = "AWS region configured for the bootstrap module."
  value       = var.aws_region
}

output "bootstrap_tags" {
  description = "Resolved tags applied to bootstrap resources."
  value       = var.tags
}
