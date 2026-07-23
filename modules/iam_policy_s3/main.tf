resource "aws_iam_policy" "s3_put" {
  name        = "${var.role_name}-s3-put"
  description = "Allows PutObject on the S3 bucket"
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:PutObject"
        ]
        Resource = "${var.bucket_arn}/*"
      }
    ]
  })

  tags = var.tags
}

resource "aws_iam_role_policy_attachment" "s3_put_attach" {
  role       = var.role_name
  policy_arn = aws_iam_policy.s3_put.arn
}
