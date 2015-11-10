# aws_lambda
A series of useful lambda functions in python

### poweroff_instances ###
This is an example AWS Lambda script that will shut down any
insntances that either do NOT have the `tag:shutdown`, or with
the `tag:shutdown != false`.

This is meant to be an aggressive script to shutdown instances,
making you explicitly flag an instance to remain powered on.

NOTE: If you tag an instance with `tag:shutdown = falsee`,
the instance will still be turned off. Check your tags!

In order for this function to work, create a policy similar to
the following, attach it to a role, and associate that role
to this lambda function:
`{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Resource": "arn:aws:logs:*:*:*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "ec2:DescribeInstanceAttribute",
                "ec2:DescribeInstanceStatus",
                "ec2:DescribeInstances",
                "ec2:DescribeRegions",
                "ec2:DescribeTags",
                "ec2:StartInstances",
                "ec2:StopInstances"
            ],
            "Resource": [
                "*"
            ]
        }
    ]
}`

Additionally, this function may take some time to run, so be sure to
set a timeout appropriately.
