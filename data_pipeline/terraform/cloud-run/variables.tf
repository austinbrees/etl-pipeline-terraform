variable "project_id" {
  description = "The ID of the project in which resources will be managed."
}

variable "location" {
  description = "The region in which resources will be managed."
}

variable "service_name" {
  description = "The name of the service to deploy."
}

variable "image_url" {
  description = "The container image to deploy."
}

variable "available_memory_mb" {
  description = "The amount of memory to allocate to the service."
  type        = number
  default     = 256 # This is optional, remove if you always want to provide this value
}
variable "service_account_email" {
  description = "The email of the service account to use for Cloud Run."
}
