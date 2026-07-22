output "policy_arn" {
  description = "ARN of the IAM policy granting DynamoDB CRUD access."
  value       = aws_iam_policy.dynamodb_crud.arn
}
