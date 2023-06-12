resource "google_pubsub_topic" "autoship_topic" {
  name = "autoship_topic"
}

resource "google_pubsub_topic" "inventory_topic" {
  name = "inventory_topic"
}

resource "google_pubsub_topic" "transactions_topic" {
  name = "transactions_topic"
}

resource "google_cloudfunctions2_function" "autoship_clean_function" {
  name        = "autoship-clean-function"
  location    = "us-central1"
  description = "My function description"

  build_config {
    runtime     = "python39"
    entry_point = "autoships_cleaning"
    source {
      storage_source {
        bucket = "cloud-functions-tobipets"
        object = "autoship-clean_function-source.zip"
      }
    }
  }

  service_config {
    max_instance_count = 1
    available_memory   = "256M"
    timeout_seconds    = 60
  }

  event_trigger {
    trigger_region = "us-central1"
    event_type     = "google.cloud.pubsub.topic.v1.messagePublished"
    pubsub_topic   = google_pubsub_topic.autoship_topic.id
    retry_policy   = "RETRY_POLICY_RETRY"
  }
}

resource "google_cloudfunctions2_function" "inventory_control_clean_function" {
  name        = "inventory-control-clean-function"
  location    = "us-central1"
  description = "My function description"

  build_config {
    runtime     = "python39"
    entry_point = "inventory_control_cleaning"
    source {
      storage_source {
        bucket = "cloud-functions-tobipets"
        object = "inventory_control_cleaning_function-source.zip"
      }
    }
  }

  service_config {
    max_instance_count = 1
    available_memory   = "256M"
    timeout_seconds    = 60
  }

  event_trigger {
    trigger_region = "us-central1"
    event_type     = "google.cloud.pubsub.topic.v1.messagePublished"
    pubsub_topic   = google_pubsub_topic.inventory_topic.id
    retry_policy   = "RETRY_POLICY_RETRY"
  }
}

resource "google_cloudfunctions2_function" "transactions_clean_function" {
  name        = "transactions-clean-function"
  location    = "us-central1"
  description = "My function description"

  build_config {
    runtime     = "python39"
    entry_point = "transactions_cleaning"
    source {
      storage_source {
        bucket = "cloud-functions-tobipets"
        object = "transactions-cleaning_function-source.zip"
      }
    }
  }

  service_config {
    max_instance_count = 1
    available_memory   = "256M"
    timeout_seconds    = 60
  }

  event_trigger {
    trigger_region = "us-central1"
    event_type     = "google.cloud.pubsub.topic.v1.messagePublished"
    pubsub_topic   = google_pubsub_topic.transactions_topic.id
    retry_policy   = "RETRY_POLICY_RETRY"
  }
}
