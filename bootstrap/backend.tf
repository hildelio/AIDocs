terraform {
  backend "s3" {
    bucket         = "startup-xyz-terraform-state"
    key            = "terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "startup-xyz-terraform-locks"
    encrypt        = true
  }
}
