variable "project_id" {
  description = "The ID of the project in which resources will be managed."
}

variable "region" {
  description = "The region in which resources will be managed."
}

variable "zone" {
  description = "The zone in which resources will be managed."
}

variable "autoship_clean_source_path" {
  description = "Path to the autoship cleaning function source archive."
  default     = "/Users/austinbrees/Documents/personal-projects/data-pipeline/data_pipeline/terraform/autoship-clean_function-source.zip"
}

variable "inventory_control_cleaning_source_path" {
  description = "Path to the inventory control cleaning function source archive."
  default     = "/Users/austinbrees/Documents/personal-projects/data-pipeline/data_pipeline/terraform/inventory_control_cleaning_function-source.zip"
}

variable "transactions_cleaning_source_path" {
  description = "Path to the transactions cleaning function source archive."
  default     = "/Users/austinbrees/Documents/personal-projects/data-pipeline/data_pipeline/terraform/transactions-cleaning_function-source.zip"
}
variable "service_name" {
    description = "The name of the service to deploy."
}

variable "image" {
  description = "The container image to deploy."
}
variable "service_account_email" {
  description = "The email of the service account to use for Cloud Run."
}