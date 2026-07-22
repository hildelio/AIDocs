variable "table_name" {
  description = "Name of the DynamoDB table."
  type        = string
}

variable "hash_key" {
  description = "Name of the attribute to use as the partition key (hash key)."
  type        = string
}

variable "hash_key_type" {
  description = "Type of the hash key attribute: S (String), N (Number), or B (Binary)."
  type        = string
  default     = "S"

  validation {
    condition     = contains(["S", "N", "B"], var.hash_key_type)
    error_message = "hash_key_type must be one of: S, N, B."
  }
}

variable "tags" {
  description = "Mandatory platform tags: project, environment, owner, cost_center, managed_by."
  type        = map(string)
}
