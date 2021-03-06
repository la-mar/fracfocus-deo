# General
variable "domain" {
  description = "Design domain of this service."
  default     = "technology"
}

variable "environment" {
  description = "Environment Name"
}

variable "service_name" {
  description = "Name of the service"
}

variable "service_port" {
  description = "Web service port"
}

variable "collector_schedule_expression" {
  description = "Cron expression for collector scheduled task"
}

variable "ecs_service_desired_count_web" {
  description = "Desired number of web containers"
  default     = 1

}

