resource "google_cloud_run_service" "frontend-streamlit-tobipets" {
  name     = var.service_name
  location = var.location

  template {
    spec {
      containers {
        image = var.image_url

      
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }
}
