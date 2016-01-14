### Overview ###

This function will call the Trusted Advisor Service Limits check and
post a message to an SNS topic if any service limits are at 80% or
greater. Useful if you wish to schedule this check on a frequent
basis and want to get notified as soon as possible.

To avoid duplicate notifications, specify an S3 bucket and key to
cache the current results. Each time the function is executed, it
will compare the current results with the cache and only send a
message if the current results differ from the cache.


### Config ###
At the top of the function, specify the following:

```
# S3 config for caching
S3_REGION = '<S3 region>'      # e.g. us-east-1
S3_BUCKET = '<S3 bucket name>' # e.g. mybucket
S3_KEY = '<S3 key name>'       # e.g. latest

# Trusted Advisor
CHECK_ID = 'eW7HH0l7J9' # Probably safe to leave as is

# SNS for notifications
TOPIC_ARN = '<your SNS topic ARN>' # e.g. arn:aws:sns:us-east-1:000000000000:config-topic

# Set to true for increased logging
DEBUG = True
```

### IAM ###
In order for this function to work properly, an IAM role should be created
to allow proper access to Trusted Advisor, S3, and SNS. Use the following
as an example policy you may wish to attach to this role, being sure to
specify the appropriate **S3 bucket** and **SNS topic**:
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
            "Sid": "Stmt1451529341202",
            "Action": [
                "sns:Publish"
            ],
            "Effect": "Allow",
            "Resource": "arn:aws:sns:us-east-1:000000000000:config-topic"
        },
        {
            "Sid": "Stmt1451621733281",
            "Action": [
                "s3:Get*",
                "s3:List*",
                "s3:Put*"
            ],
            "Effect": "Allow",
            "Resource": "arn:aws:s3:::mybucket/*"
        }
    ]
}
```

### Lambda Schedule ###
To execute this function on a regular basis, in the **Event Sources** tab
of your console click *Add event source* and specify the following:
* Event source type: Scheduled Event
* Name: a-useful-name
* Description: Runs every X hours
* Schedule expression: rate(4 hours)

This will set a schedule to execute your function every 4 hours. See the
[lambda scheduled event documentation](http://docs.aws.amazon.com/lambda/latest/dg/with-scheduled-events.html)
for more details.
