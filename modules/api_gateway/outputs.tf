output "api_endpoint" {
  description = "Public invoke URL of the API Gateway HTTP API."
  value       = aws_apigatewayv2_stage.default.invoke_url
}

output "api_id" {
  description = "ID of the API Gateway HTTP API."
  value       = aws_apigatewayv2_api.this.id
}
