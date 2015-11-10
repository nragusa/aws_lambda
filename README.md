# aws_lambda
A series of useful lambda functions in python

### change_ec2_state ###
This is an example AWS lambda function that can either shutdown
or startup instances in any region given a particular tag name / value
pair. For example, to power off all instances with the following tag:

tag:shutdown = true

Add this lambda function along with the following configuration:

```
STATE = 'stop'
STATE_MAP = {'stop' : {'tag': 'shutdown', 'value': 'true'}}```

This function can then be added as a scheduled event and executed
on a [schedule](http://docs.aws.amazon.com/lambda/latest/dg/getting-started-scheduled-events.html) of your choosing.

In order for this function to work, create a policy similar to
the following, attach it to a role, and associate that role
to this lambda function:
```
{
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
}```

Additionally, this function may take some time to run, so be sure to
set a timeout appropriately.
