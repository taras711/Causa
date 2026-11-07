# Volitelné: Terraform pro zákaznické servery
terraform {
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 3.0"
    }
  }
}

provider "docker" {}

# Placeholder – konkrétní recursos se doplní při zákaznickém nasazení
resource "docker_container" "causa_backend" {
  name  = "causa-backend"
  image = "causa/backend:latest"
}