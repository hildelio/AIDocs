variable "project" {
  description = "Project identifier used for naming resources."
  type        = string
  default     = "startup-xyz"
}

variable "environment" {
  description = "Environment name for the deployment."
  type        = string
  default     = "dev"
}

variable "owner" {
  description = "Team or owner responsible for the resources."
  type        = string
  default     = "platform-team"
}

variable "cost_center" {
  description = "Cost center tag for the resources."
  type        = string
  default     = "engineering"
}
