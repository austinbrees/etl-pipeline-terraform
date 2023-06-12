provider "google" {
  project = var.project_id
  region  = var.region
  zone    = var.zone
  credentials = file("/Users/austinbrees/Documents/personal-projects/etl-pipeline-terraform/data_pipeline/terraform/credentials.json")
}

module "cloud-functions" {
  source = "/Users/austinbrees/Documents/personal-projects/etl-pipeline-terraform/data_pipeline/terraform/cloud-functions"
  service_account_email = var.service_account_email
}

module "cloud-run" {
  source              = "/Users/austinbrees/Documents/personal-projects/etl-pipeline-terraform/data_pipeline/terraform/cloud-run"
  location            = var.region
  image_url           = var.image
  project_id          = var.project_id
  service_name        = var.service_name
  service_account_email = var.service_account_email
  available_memory_mb = 256 # Replace 256 with the amount of memory you want to allocate
}
