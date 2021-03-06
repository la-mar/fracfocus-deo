
### Task Definitions ###

data "aws_ecs_task_definition" "web" {
  task_definition = "${var.service_name}-web"
}

resource "aws_security_group" "web" {
  description = "Balancer for ${local.full_service_name}"

  vpc_id = data.terraform_remote_state.vpc.outputs.vpc_id
  name   = "${var.service_name}-web-sg"
  tags   = local.tags

  ingress {
    description = "All TCP Traffic"
    protocol    = "tcp"
    from_port   = var.service_port
    to_port     = var.service_port
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    description = "All Traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}


### ECS Services ###
resource "aws_ecs_service" "web" {
  name            = "${var.service_name}-web"
  cluster         = data.terraform_remote_state.web_cluster.outputs.cluster_arn
  task_definition = data.aws_ecs_task_definition.web.family

  scheduling_strategy = "DAEMON"
  # ordered_placement_strategy {
  #   type  = "spread"
  #   field = "instanceId"
  # }
  # desired_count           = var.ecs_service_desired_count_web
  enable_ecs_managed_tags = true
  propagate_tags          = "TASK_DEFINITION"
  tags                    = local.tags

  # allow external changes without Terraform plan difference
  lifecycle {
    create_before_destroy = true
    ignore_changes = [
      desired_count,
      task_definition,
    ]
  }

  network_configuration {
    subnets          = data.terraform_remote_state.vpc.outputs.private_subnets
    security_groups  = [aws_security_group.web.id]
    assign_public_ip = false
  }

  service_registries {
    registry_arn   = aws_service_discovery_service.web.arn
    container_name = "${var.service_name}-web"

  }
}

# TODO:Add cpu util auto scaler

# Define Task Role
resource "aws_iam_role" "task_role" {
  name                  = "${var.service_name}-task-role"
  assume_role_policy    = data.aws_iam_policy_document.task_sts_policy.json
  force_detach_policies = true
  tags                  = local.tags
}

data "aws_iam_policy_document" "task_sts_policy" {
  statement {
    sid    = ""
    effect = "Allow"
    actions = [
      "sts:AssumeRole",
    ]
    principals {
      type        = "Service"
      identifiers = ["ecs-tasks.amazonaws.com"]
    }
  }
}

resource "aws_iam_role_policy_attachment" "attach_ecs_service_policy_to_task_role" {
  role       = aws_iam_role.task_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonEC2ContainerServiceforEC2Role"
}

data "aws_iam_policy_document" "task_policy" {

  statement {
    sid = "1" # task_access_secrets
    actions = [
      "ssm:GetParameter*",
    ]
    resources = [
      "arn:aws:ssm:*:*:parameter/${var.service_name}/*",
      "arn:aws:ssm:*:*:parameter/${var.service_name}-collector/*",
      "arn:aws:ssm:*:*:parameter/datadog/*"
    ]
  }

  statement {
    sid = "2" # task_access_kms
    actions = [
      "kms:ListKeys",
      "kms:ListAliases",
      "kms:Describe*",
      "kms:Decrypt"
    ]
    resources = [
      data.terraform_remote_state.kms.outputs.ssm_key_arn # dont use alias arn
    ]
  }
}

resource "aws_iam_policy" "task_policy" {
  name        = "${var.service_name}-task-policy"
  path        = "/"
  description = "${var.service_name} task policy"

  policy = data.aws_iam_policy_document.task_policy.json
}

resource "aws_iam_role_policy_attachment" "attach_task_policy_to_task_role" {
  role       = aws_iam_role.task_role.name
  policy_arn = aws_iam_policy.task_policy.arn
}
