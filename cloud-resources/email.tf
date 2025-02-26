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

data "aws_iam_policy_document" "lambda_custom" {
  statement {
    effect = "Allow"

    actions = [
      "kms:Decrypt",
      "s3:*"
    ]

    resources = ["*"]
  }
}

resource "aws_iam_role" "lambda_role" {
  name = "judgment-reader-lambda-report"
  assume_role_policy = data.aws_iam_policy_document.lambda_role.json
}

resource "aws_iam_role_policy" "lambda_cutom" {
  role = aws_iam_role.lambda_role.name
  name = "judgment-reader-report-lambda"
  policy = data.aws_iam_policy_document.lambda_custom.json

}

resource "aws_iam_role_policy_attachment" "lambda_role_basic_attachment" {
  role = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy_attachment" "lambda_role_eni" {
  role = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2FullAccess"
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

  statement {
    effect = "Allow"

    actions = [
      "kms:Decrypt",
      "s3:*",
      "ses:GetContact",
      "ses:GetContactList"
    ]

    resources = ["*"]
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
  force_delete = true
}

resource "aws_cloudwatch_log_group" "report_lambda" {
  name = "judgment-reader-report-lambda"
}

resource "null_resource" "report_lambda"{
  provisioner "local-exec" {
    command = <<EOT
      aws ecr get-login-password --region eu-west-2 | docker login --username AWS --password-stdin ${local.account_id}.dkr.ecr.eu-west-2.amazonaws.com
      docker pull hello-world
      docker tag hello-world ${aws_ecr_repository.report_lambda.repository_url}:latest
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
  timeout = 30
  environment {
    variables = {
      DB_NAME = var.db_name
      DB_HOST = aws_db_instance.main.address
      DB_PORT = aws_db_instance.main.port
      DB_USER = var.db_user
      DB_PASSWORD = var.db_password
      ACCESS_KEY = var.access_key
      SECRET_KEY = var.secret_key
      CONTACT_LIST_NAME = aws_sesv2_contact_list.daily_update.id
    }
  }
  vpc_config {
    subnet_ids = [
      aws_subnet.public_a.id,
      aws_subnet.public_b.id
    ]
    security_group_ids = [aws_security_group.master.id]
  }
  depends_on = [
      aws_cloudwatch_log_group.report_lambda,
      aws_iam_role_policy_attachment.lambda_role_basic_attachment,
      aws_ecr_repository.report_lambda,
      null_resource.report_lambda
    ]
}

resource "aws_ecr_repository" "contact_lambda" {
  name = "judgment-reader-contact-lambda"
  image_tag_mutability = "MUTABLE"
  force_delete = true
}

resource "aws_cloudwatch_log_group" "contact_lambda" {
  name = "judgment-reader-contact-lambda"
}

resource "null_resource" "contact_lambda"{
  provisioner "local-exec" {
    command = <<EOT
      aws ecr get-login-password --region eu-west-2 | docker login --username AWS --password-stdin ${local.account_id}.dkr.ecr.eu-west-2.amazonaws.com
      docker pull hello-world
      docker tag hello-world ${aws_ecr_repository.contact_lambda.repository_url}:latest
      docker push ${aws_ecr_repository.contact_lambda.repository_url}:latest
    EOT
  }
}

resource "aws_lambda_function" "contact" {
  function_name = "judgment-reader-contact"
  role = aws_iam_role.lambda_role.arn
  image_uri = "${aws_ecr_repository.contact_lambda.repository_url}:latest"
  package_type = "Image"
  architectures = ["arm64"]
  timeout = 30
  environment {
    variables = {
      DB_NAME = var.db_name
      DB_HOST = aws_db_instance.main.address
      DB_PORT = aws_db_instance.main.port
      DB_USER = var.db_user
      DB_PASSWORD = var.db_password
      ACCESS_KEY = var.access_key
      SECRET_KEY = var.secret_key
      CONTACT_LIST_NAME = aws_sesv2_contact_list.daily_update.id
    }
  }
  depends_on = [
      aws_cloudwatch_log_group.report_lambda,
      aws_iam_role_policy_attachment.lambda_role_basic_attachment,
      aws_ecr_repository.contact_lambda,
      null_resource.contact_lambda
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
            <a href='{{ amazonSESUnsubscribeUrl }}'>Click here to unsubscribe</a>
          <body>
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
      "StartAt": "Contact Lambda",
      "States": {
        "Contact Lambda": {
          "Type": "Task",
          "Resource": "arn:aws:states:::lambda:invoke",
          "Output": "{% $states.result.Payload %}",
          "Arguments": {
            "FunctionName": "arn:aws:lambda:eu-west-2:129033205317:function:judgment-reader-contact:$LATEST"
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
          "Assign": {
            "SubscribedEmails": "{% $states.result.Payload.SubscribedEmails %}"
          },
          "Next": "Choice"
        },
        "Choice": {
          "Type": "Choice",
          "Choices": [
            {
              "Next": "Report Lambda",
              "Condition": "{% $boolean($SubscribedEmails) %}"
            }
          ],
          "Default": "Fail"
        },
        "Report Lambda": {
          "Arguments": {
            "FunctionName": "arn:aws:lambda:eu-west-2:129033205317:function:judgment-reader-report:$LATEST"
          },
          "Assign": {
            "JudgmentData": "{% $states.result.Payload.JudgmentData %}"
          },
          "Output": "{% $states.result %}",
          "Resource": "arn:aws:states:::lambda:invoke",
          "Retry": [
            {
              "BackoffRate": 2,
              "ErrorEquals": [
                "Lambda.ServiceException",
                "Lambda.AWSLambdaException",
                "Lambda.SdkClientException",
                "Lambda.TooManyRequestsException"
              ],
              "IntervalSeconds": 1,
              "JitterStrategy": "FULL",
              "MaxAttempts": 3
            }
          ],
          "Type": "Task",
          "Next": "Choice (1)"
        },
        "Choice (1)": {
          "Type": "Choice",
          "Choices": [
            {
              "Next": "SendEmail",
              "Condition": "{% $boolean($JudgmentData) %}"
            }
          ],
          "Default": "Fail (1)"
        },
        "SendEmail": {
          "Arguments": {
            "ConfigurationSetName": "",
            "Content": {
              "Template": {
                "TemplateArn": "${aws_ses_template.daily_update.arn}",
                "TemplateData": {
                  "JudgmentData": "{% $JudgmentData %}"
                }
              }
            },
            "Destination": {
              "BccAddresses": "{% $SubscribedEmails %}"
            },
            "FeedbackForwardingEmailAddress": "${var.my_email}",
            "FromEmailAddress": "${var.my_email}",
            "ListManagementOptions": {
              "ContactListName": "judgment-reader-daily-update-contact-list",
              "TopicName": "daily-update"
            }
          },
          "Resource": "arn:aws:states:::aws-sdk:sesv2:sendEmail",
          "Type": "Task",
          "Next": "Success"
        },
        "Success": {
          "Type": "Succeed"
        },
        "Fail (1)": {
          "Type": "Fail"
        },
        "Fail": {
          "Type": "Fail"
        }
      }
    }
  )
  type = "STANDARD"
}
