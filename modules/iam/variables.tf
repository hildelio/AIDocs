variable "project" {
  description = "Project identifier used for naming resources."
  type        = string
}

variable "environment" {
  description = "Environment name for the deployment."
  type        = string
}

variable "owner" {
  description = "Team or owner responsible for the resources."
  type        = string
}

variable "cost_center" {
  description = "Cost center tag for the resources."
  type        = string
}
