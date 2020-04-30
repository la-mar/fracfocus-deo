"""
Example docker deployment to AWS ECS cluster.

The script does the following:

    1. Loads environment variables from .env file in the project root

    For each service in SERVICES
    2. Generates a populated ECS task definition
        - You can configure your task definitions in the get_task_definition() method.
    3. Optionally authenticate Docker to ECR
    4. Optionally build any configured containers
    5. Optionally push any configured containers to ECR
    6. Register the new task definition in ECR
    7. Retrieve the latest task definition revision number
    8. Update the running service with the new task definition and force a new deployment
"""

# pylint: disable=dangerous-default-value,too-many-arguments,missing-function-docstring

import os
from typing import List, Dict

import boto3
import tomlkit

# from dotenv import dotenv_values


def get_project_meta() -> dict:
    pyproj_path = "./pyproject.toml"
    if os.path.exists(pyproj_path):
        with open(pyproj_path, "r") as pyproject:
            file_contents = pyproject.read()
        return tomlkit.parse(file_contents)["tool"]["poetry"]
    else:
        return {}


pkg_meta = get_project_meta()
project = pkg_meta.get("name")
version = pkg_meta.get("version")

ENV = os.getenv("ENV", "prod")
AWS_ACCOUNT_ID = os.getenv(
    "AWS_ACCOUNT_ID", boto3.client("sts").get_caller_identity().get("Account")
)
IMAGE_TAG: str = os.getenv("IMAGE_TAG")  # type: ignore
IMAGE_NAME: str = f"{os.getenv('IMAGE_NAME')}{':' if IMAGE_TAG else ''}{IMAGE_TAG or ''}"

CLUSTER_NAME = os.getenv("ECS_CLUSTER")  # type: ignore
CLUSTER_ARN = f"arn:aws:ecs:us-east-1:{AWS_ACCOUNT_ID}:cluster/{CLUSTER_NAME}"
TASK_IAM_ROLE = f"arn:aws:iam::{AWS_ACCOUNT_ID}:role/{project}-task-role"

if not any([ENV, AWS_ACCOUNT_ID, IMAGE_NAME, CLUSTER_NAME]):
    raise ValueError("One or more environment variables are missing")


SERVICES = [
    {
        "task_name": "fracfocus-web",
        "cluster_name": "ecs-web-cluster",
        "task_type": "service",
    },
    {
        "task_name": "fracfocus-collector",
        "cluster_name": "ecs-collector-cluster",
        "task_type": "scheduled",
    },
]

TAGS = [
    {"key": "domain", "value": "engineering"},
    {"key": "service_name", "value": project},
    {"key": "environment", "value": ENV},
    {"key": "terraform", "value": "true"},
]

TASKS: Dict[str, Dict] = {
    "fracfocus-collector": {
        "service": "fracfocus-bimonthly",
        "command": "fracfocus run collector",
        "rule": "schedule-fracfocus-bi-monthly",
    },
}


BUILD = False
PUSH = False

print("\n\n" + "-" * 30)
print(f"ENV: {ENV}")
print(f"AWS_ACCOUNT_ID: {AWS_ACCOUNT_ID}")
print(f"CLUSTER_NAME: {CLUSTER_NAME}")
print(f"SERVICES: {SERVICES}")
print("-" * 30 + "\n\n")


def get_task_definition(
    name: str,
    task_name: str,
    tags: list = [],
    task_iam_role_arn: str = "ecsTaskExecutionRole",
):
    image = IMAGE_NAME
    defs = {
        "fracfocus-web": {
            "containerDefinitions": [
                {
                    "name": "fracfocus-web",
                    "command": ["fracfocus", "run", "web"],
                    "memoryReservation": 128,
                    "cpu": 128,
                    "image": image,
                    "essential": True,
                    "portMappings": [
                        {"hostPort": 80, "containerPort": 80, "protocol": "tcp"}
                    ],
                },
            ],
            "executionRoleArn": "ecsTaskExecutionRole",
            "family": task_name,
            "networkMode": "awsvpc",
            "taskRoleArn": task_iam_role_arn,
            "tags": tags,
        },
        "fracfocus-collector": {
            "containerDefinitions": [
                {
                    "name": "fracfocus-collector",
                    "command": ["fracfocus", "run", "collector"],
                    "memoryReservation": 512,
                    "cpu": 128,
                    "image": image,
                    "essential": True,
                },
            ],
            "executionRoleArn": "ecsTaskExecutionRole",
            "family": task_name,
            "networkMode": "bridge",
            "taskRoleArn": task_iam_role_arn,
            "tags": tags,
            "cpu": "512",
        },
    }

    return defs[name]


class AWSClient:
    access_key_id = None
    secret_access_key = None
    session_token = None
    account_id = None
    region = None
    _ecs = None

    def __init__(self):
        self.credentials()

    @property
    def has_credentials(self):
        return all(
            [
                self.access_key_id is not None,
                self.secret_access_key is not None,
                self.region is not None,
                self.account_id is not None,
            ]
        )

    @property
    def ecr_url(self):
        if not self.has_credentials:
            self.credentials()
        return f"{self.account_id}.dkr.ecr.{self.region}.amazonaws.com"

    def credentials(self):
        credentials = {
            "access_key_id": os.getenv("AWS_ACCESS_KEY_ID"),
            "secret_access_key": os.getenv("AWS_SECRET_ACCESS_KEY"),
            "region": os.getenv("AWS_REGION", "us-east-1"),
            "account_id": os.getenv("AWS_ACCOUNT_ID"),
            "session_token": os.getenv("AWS_SESSION_TOKEN"),
            "security_token": os.getenv("AWS_SECURITY_TOKEN"),
        }
        # pylint: disable=expression-not-assigned
        [setattr(self, k, v) for k, v in credentials.items()]  # type: ignore

        return credentials

    def get_client(self, service_name: str):

        if not self.has_credentials:
            self.credentials()

        return boto3.client(
            service_name,
            aws_access_key_id=self.access_key_id,
            aws_secret_access_key=self.secret_access_key,
            region_name=self.region,
            aws_session_token=self.session_token,
        )

    @property
    def ecs(self):
        return self._ecs or self.get_client("ecs")

    def get_latest_revision(self, task_name: str):
        response = self.ecs.describe_task_definition(taskDefinition=task_name)
        return response["taskDefinition"]["revision"]


client = AWSClient()

events = client.get_client("events")
target_id = 0
targets = []

results = []


for deployment in SERVICES:
    task = deployment["task_name"]
    task_type = deployment["task_type"]
    cluster = deployment["cluster_name"]
    s = f"{task:>20}:"
    try:
        prev_rev_num = client.get_latest_revision(task)
    except Exception:
        prev_rev_num = "?"
    cdef = get_task_definition(
        name=task, task_name=task, tags=TAGS, task_iam_role_arn=TASK_IAM_ROLE,
    )

    task_def_arn = client.ecs.register_task_definition(**cdef)["taskDefinition"][
        "taskDefinitionArn"
    ]

    rev_num = client.get_latest_revision(task)
    s += "\t" + f"updated revision: {prev_rev_num} -> {rev_num}"
    results.append((task, task_type, cluster, prev_rev_num, rev_num, task_def_arn))
    print(s)

for task, task_type, cluster, prev_rev_num, rev_num, task_def_arn in results:
    if task_type == "service":
        response = client.ecs.update_service(
            cluster=cluster,
            service=task,
            forceNewDeployment=True,
            taskDefinition=f"{task}:{rev_num}",
        )
        print(f"{task:>20}: updated service on cluster {cluster}")
    elif task_type == "scheduled":
        task_def = TASKS[task]
        service = task_def["service"]
        rule = task_def["rule"]
        task_count = 1
        targets = [
            {
                "Id": str(target_id),
                "Arn": CLUSTER_ARN,
                "RoleArn": f"arn:aws:iam::{AWS_ACCOUNT_ID}:role/ecsEventsRole",
                "EcsParameters": {
                    "TaskDefinitionArn": task_def_arn,
                    "TaskCount": task_count,
                },
            }
        ]
        response = events.put_targets(Rule=rule, Targets=targets)
        print("\t" + f"created event: {cluster}/{service} - {rule}")
        target_id += 1


print("\n\n")


print("\n\n")
