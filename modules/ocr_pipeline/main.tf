resource "aws_iam_role" "ocr_lambda_exec" {
  name = "${var.project}-${var.environment}-ocr-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = "sts:AssumeRole"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })

  tags = var.tags
}

resource "aws_iam_policy" "ocr_lambda_policy" {
  name        = "${var.project}-${var.environment}-ocr-policy"
  description = "Least privilege policy for OCR Lambda"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "textract:DetectDocumentText"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject"
        ]
        Resource = "${var.s3_bucket_arn}/*"
      },
      {
        Effect = "Allow"
        Action = [
          "dynamodb:PutItem",
          "dynamodb:UpdateItem",
          "dynamodb:Scan"
        ]
        Resource = var.dynamodb_table_arn
      },
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:*:*:*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ocr_lambda_policy_attach" {
  role       = aws_iam_role.ocr_lambda_exec.name
  policy_arn = aws_iam_policy.ocr_lambda_policy.arn
}

module "ocr_lambda" {
  source = "../lambda"

  function_name = "${var.project}-${var.environment}-ocr"
  runtime       = "python3.12"
  handler       = "src.handlers.ocr_handler.handler"
  filename      = var.artifact_path
  iam_role_arn  = aws_iam_role.ocr_lambda_exec.arn
  timeout       = 30
  memory_size   = 256

  environment_variables = {
    S3_BUCKET_NAME      = var.s3_bucket_id
    DYNAMODB_TABLE_NAME = split("/", var.dynamodb_table_arn)[1]
  }

  tags = var.tags
}

resource "aws_lambda_permission" "allow_s3" {
  statement_id  = "AllowExecutionFromS3Bucket"
  action        = "lambda:InvokeFunction"
  function_name = module.ocr_lambda.function_name
  principal     = "s3.amazonaws.com"
  source_arn    = var.s3_bucket_arn
}

resource "aws_s3_bucket_notification" "bucket_notification" {
  bucket = var.s3_bucket_id

  lambda_function {
    lambda_function_arn = module.ocr_lambda.function_arn
    events              = ["s3:ObjectCreated:*"]
  }

  depends_on = [aws_lambda_permission.allow_s3]
}
