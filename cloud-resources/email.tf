data "aws_iam_policy_document" "lambda_role" {
  statement {
    effect = "Allow"

    principals {
      type = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }

    actions = ["sts:AssumeRole"]
  }
}

resource "aws_iam_role" "lambda_role" {
  name = "judgment-reader-lambda-report"
  assume_role_policy = data.aws_iam_policy_document.lambda_role.json
}

resource "aws_iam_role_policy_attachment" "lambda_role_basic_attachment" {
  role = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}


data "aws_iam_policy_document" "report_step_role" {
  statement {
    effect = "Allow"

    principals {
      type = "Service"
      identifiers = ["states.amazonaws.com"]
    }

    actions = ["sts:AssumeRole"]
  }
}

resource "aws_iam_role" "report_step_role" {
  name = "judgment-reader-state-report"
  assume_role_policy = data.aws_iam_policy_document.report_step_role.json
}

resource "aws_iam_role_policy_attachment" "report_step_role_lambda" {
  role = aws_iam_role.report_step_role.name 
  policy_arn = "arn:aws:iam::aws:policy/AWSLambda_FullAccess"
}

resource "aws_iam_role_policy_attachment" "report_step_role_ses" {
  role = aws_iam_role.report_step_role.name 
  policy_arn = "arn:aws:iam::aws:policy/AmazonSESFullAccess"
}

resource "aws_iam_role_policy_attachment" "report_step_role_x_ray" {
   role = aws_iam_role.report_step_role.name
  policy_arn = "arn:aws:iam::aws:policy/AWSXrayFullAccess"
}

data "aws_iam_policy_document" "report_scheduler_role" {
  statement {
    effect = "Allow"

    principals {
      type = "Service"
      identifiers = ["scheduler.amazonaws.com"]
    }

    actions = ["sts:AssumeRole"]
  }

}

data "aws_iam_policy_document" "report_scheduler_role_policy" {
  statement {
    effect = "Allow"
    actions = [
      "states:StartExecution"
    ]
    resources = [
      "${aws_sfn_state_machine.report_step_function.arn}"
    ]
  }

    statement {
    effect = "Allow"

    actions = [
      "logs:CreateLogStream",
      "logs:PutLogEvents",
    ]

    resources = ["arn:aws:logs:*:*:*"]
  }
}

resource "aws_iam_role" "report_scheduler_role" {
  name = "judgment-reader-state-scheduler-role"
  assume_role_policy = data.aws_iam_policy_document.report_scheduler_role.json
}

resource "aws_iam_role_policy" "report_scheduler_policy"{
  name = "judgment-reader-report-scheduler-policy"
  role = aws_iam_role.report_scheduler_role.id
  policy = data.aws_iam_policy_document.report_scheduler_role_policy.json
}

resource "aws_ecr_repository" "report_lambda" {
  name = "judgment-reader-report-lambda"
  image_tag_mutability = "MUTABLE"
}

resource "aws_cloudwatch_log_group" "report_lambda" {
  name = "judgment-reader-report-lambda"
}

resource "null_resource" "report_lambda"{
  provisioner "local-exec" {
    command = <<EOT
      aws ecr get-login-password --region eu-west-2 | docker login --username AWS --password-stdin ${local.account_id}.dkr.ecr.eu-west-2.amazonaws.com
      docker pull public.ecr.aws/ecs-sample-image/amazon-ecs-sample:latest
      docker build --platform linux/arm64 --provenance false -t judgment-reader-server .
      docker tag public.ecr.aws/ecs-sample-image/amazon-ecs-sample:latest ${aws_ecr_repository.report_lambda.repository_url}:latest
      docker push ${aws_ecr_repository.report_lambda.repository_url}:latest
    EOT
  }
}

resource "aws_lambda_function" "report" {
  function_name = "judgment-reader-report"
  role = aws_iam_role.lambda_role.arn
  image_uri = "${aws_ecr_repository.report_lambda.repository_url}:latest"
  package_type = "Image"
  architectures = ["arm64"]
  environment {
    variables = {
      DB_NAME = var.db_name
      DB_HOST = aws_db_instance.main.address
      DB_PORT = aws_db_instance.main.port
      DB_USER = var.db_user
      DB_PASSWORD = var.db_password
    }
  }
  depends_on = [
      aws_cloudwatch_log_group.report_lambda,
      aws_iam_role_policy_attachment.lambda_role_basic_attachment,
      aws_ecr_repository.report_lambda,
      null_resource.report_lambda
    ]
}

resource "aws_scheduler_schedule" "report_schedule" {
  name = "judgment-reader-report"

  flexible_time_window {
    mode = "OFF"
  }

  schedule_expression = "cron(0 6 ? * MON-FRI *)"

  target {
    arn = aws_sfn_state_machine.report_step_function.arn
    role_arn = aws_iam_role.report_scheduler_role.arn
  }
}

resource "aws_sesv2_contact_list" "daily_update" {
  contact_list_name = "judgment-reader-daily-update-contact-list"

  topic {
    default_subscription_status = "OPT_IN"
    description = "Daily update of the previous day's cases"
    display_name = "Judgment Reader Daily Update"
    topic_name = "daily-update"
  }
}

resource "aws_ses_template" "daily_update" {
  name = "judgment-reader-daily-update"
  html = <<HTML
        <html>
        <body>
            Hi everyone,
            <br><br>
            Please see below a list of the previous day's judgments. Click on a judgment to be taken to its overview:
            <br><br>
            {{ JudgmentData }}
            <br><br>
            Best wishes,
            <br><br>
            The Judgment Reader Team
            </body>
            <a href='{{ amazonSESUnsubscribeUrl }}'>Click here to unsubscribe</a>
            </html>
        HTML
  subject = "Judgment Reader Daily Update"
}

resource "aws_sfn_state_machine" "report_step_function" {
  name = "judgment-reader-report-fsm"
  role_arn = aws_iam_role.report_step_role.arn
  definition = jsonencode(
    {
      "QueryLanguage": "JSONata",
      "StartAt": "Lambda Invoke",
      "States": {
        "Lambda Invoke": {
          "Type": "Task",
          "Resource": "arn:aws:states:::lambda:invoke",
          "Output": "{% $states.result %}",
          "Arguments": {
            "FunctionName": "${aws_lambda_function.report.arn}",
            "Payload": "{% $states.input %}"
          },
          "Retry": [
            {
              "ErrorEquals": [
                "Lambda.ServiceException",
                "Lambda.AWSLambdaException",
                "Lambda.SdkClientException",
                "Lambda.TooManyRequestsException"
              ],
              "IntervalSeconds": 1,
              "MaxAttempts": 3,
              "BackoffRate": 2,
              "JitterStrategy": "FULL"
            }
          ],
          "Next": "SendEmail",
          "Assign": {
            "Body": "{% $states.result.Payload.Body %}",
            "SubscribedEmails": "{% $states.result.Payload.SubscribedEmails %}"
          }
        },
        "SendEmail": {
          "Type": "Task",
          "Arguments": {
            "ConfigurationSetName": "",
            "Content": {
              "Template": {
                "TemplateArn": "${aws_ses_template.daily_update.arn}",
                "TemplateData": "{% $Body %}"
              }
            }
            "Destination": {
              "BccAddresses": "{% $SubscribedEmails %}"
            },
            "FeedbackForwardingEmailAddress": "${var.my_email}",
            "FromEmailAddress": "${var.my_email}",
            "ListManagementOptions": {
              "ContactListName": "${aws_sesv2_contact_list.daily_update.contact_list_name}",
              "TopicName": "daily-update"
            }
          },
          "Resource": "arn:aws:states:::aws-sdk:sesv2:sendEmail",
          "End": true
        }
      }
    }
  )
  type = "STANDARD"
}
