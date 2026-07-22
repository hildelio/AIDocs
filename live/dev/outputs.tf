output "api_endpoint" {
  description = "Public invoke URL of the API Gateway HTTP API."
  value       = module.api_gateway.api_endpoint
}

output "dynamodb_table_name" {
  description = "Name of the DynamoDB table."
  value       = module.dynamodb.table_name
}
