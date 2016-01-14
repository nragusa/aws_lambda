# aws_lambda
A series of useful lambda functions in python

### change_ec2_state ###
This is an example AWS lambda function that can either shutdown
or startup instances in any region given a particular tag name / value
pair.

### TA_service_limit_alerts ###
This function will call the Trusted Advisor Service Limits check and
post a message to an SNS topic if any service limits are at 80% or
greater. Useful if you wish to schedule this check on a frequent
basis and want to get notified as soon as possible.
