resource "aws_iam_policy" "dynamodb_crud" {
  name        = "${var.tags["project"]}-${var.tags["environment"]}-lambda-dynamodb-crud"
  description = "CRUD access to DynamoDB table for Lambda execution role. Resource restricted to exact table ARN — no wildcards."

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "dynamodb:GetItem",
          "dynamodb:PutItem",
          "dynamodb:UpdateItem",
          "dynamodb:DeleteItem",
          "dynamodb:Query",
          "dynamodb:Scan",
        ]
        Resource = [var.table_arn]
      }
    ]
  })

  tags = var.tags
}

resource "aws_iam_role_policy_attachment" "dynamodb_crud" {
  role       = var.role_name
  policy_arn = aws_iam_policy.dynamodb_crud.arn
}
