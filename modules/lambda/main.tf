resource "aws_lambda_function" "this" {
  function_name = var.function_name
  role          = var.iam_role_arn
  runtime       = var.runtime
  handler       = var.handler
  filename      = var.filename

  tags = var.tags
}
