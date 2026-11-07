# Volitelné: Terraform proměnné
variable "tenant_id" {
  description = "ID tenanta pro izolaci klienta"
  type        = string
  default     = "default"
}

variable "db_password" {
  description = "Heslo k databázi"
  type        = string
  sensitive   = true
}