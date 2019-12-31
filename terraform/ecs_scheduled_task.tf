
# Define Scheduled Task Role (essentially inherits from regular task role)
resource "aws_iam_role" "scheduled_task_role" {
  name                  = "${var.service_name}-scheduled-task-role"
  assume_role_policy    = data.aws_iam_policy_document.task_sts_policy.json
  force_detach_policies = true
  tags                  = local.tags
}

resource "aws_iam_role_policy_attachment" "attach_ecs_service_policy_to_scheduled_task_role" {
  role       = aws_iam_role.scheduled_task_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonEC2ContainerServiceforEC2Role"
}

resource "aws_iam_role_policy_attachment" "attach_ecs_events_policy_to_scheduled_task_role" {
  role       = aws_iam_role.scheduled_task_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonEC2ContainerServiceEventsRole"
}

resource "aws_iam_role_policy_attachment" "attach_task_policy_to_scheduled_task_role" {
  role       = aws_iam_role.scheduled_task_role.name
  policy_arn = aws_iam_policy.task_policy.arn
}

data "aws_ecs_task_definition" "collector" {
  task_definition = "${var.service_name}-collector"
}


## Cloudwatch event

resource "aws_cloudwatch_event_rule" "scheduled_task" {
  name                = "${var.service_name}_collector_scheduled_task"
  description         = "Run ${var.service_name} collector task at a scheduled time (${var.collector_schedule_expression})"
  schedule_expression = var.collector_schedule_expression
}

resource "aws_cloudwatch_event_target" "scheduled_task" {
  target_id = "${var.service_name}-collector-scheduled-task-bi-monthly"
  rule      = aws_cloudwatch_event_rule.scheduled_task.name
  arn       = data.terraform_remote_state.collector_cluster.outputs.cluster_arn
  role_arn  = aws_iam_role.scheduled_task_role.arn

  ecs_target {
    task_count          = 1
    task_definition_arn = "arn:aws:ecs:us-east-1:${data.aws_caller_identity.current.account_id}:task-definition/${var.service_name}-collector"
  }
}
