"""
This lambda function is intended to be run on a defined schedule
and will check for any service limits are that at 80% or greater
as reported by Trusted Advisor. The function will then post a message
to an SNS topic with the results. Data may also be stored in S3
so as to avoid posting to the SNS topic with the same data on
each execution.
"""
from __future__ import print_function
from datetime import datetime
import boto3
import json
import logging

##########
# CONFIG
##########
S3_REGION = 'us-east-1'
S3_BUCKET = 'mybucket'
S3_KEY = 'latest'

# Trusted Advisor
CHECK_ID = 'eW7HH0l7J9' # Probably safe to leave alone

# SNS
TOPIC_ARN = 'arn:aws:sns:us-east-1:000000000000:service-limit-topic'

# Set to true for increased logging
DEBUG = False
##########

logger = logging.getLogger()
if DEBUG is True:
    logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.INFO)

def updateCurrentValues(data):
    logger.info('Updating cache in S3')
    s3_client = boto3.client('s3', S3_REGION)
    local_file = '/tmp/%s' % S3_KEY
    with open(local_file, 'w') as f:
        json.dump(data, f, sort_keys=True, indent=4)
    try:
        s3_client.upload_file(local_file, S3_BUCKET, S3_KEY)
    except Exception as e:
        logger.error('Problem updating cache in S3: {}'.format(str(e)))
        raise

def getCachedLimits():
    logger.info('Getting current limits at or above 80%% from cache')
    s3_client = boto3.client('s3',S3_REGION)
    try:
        local_file = '/tmp/%s' % S3_KEY
        s3_client.download_file(S3_BUCKET, S3_KEY, local_file)
        with open(local_file, 'r') as f:
            cache = json.load(f)
        return cache
    except:
        logger.warning('Problem getting cache. Assuming none...')
        return {'flagged': ''}

def formatMessage(data):
    """Extracts the metadata from the TA support API and formats it
    in a more human readable way for easy digesting in an email"""
    message = "The following service limits have reached 80% or greater:\n\n"
    for check in data['flagged']:
        metadata = check.get('metadata',[])
        if len(metadata) > 0:
            try:
                service = ('Service: {}\nLimit Name: {}\n'
                           'Limit Amount: {}\n Current Usage: {}\n'
                           'Region: {}\n\n'.format(metadata[1],metadata[2],
                                                   metadata[3],metadata[4],
                                                   metadata[0]))
                message += service
            except IndexError:
                message += '\n'
    return message


def sendUpdate(data):
    client = boto3.client('sns')
    try:
        response = client.publish(
                TopicArn=TOPIC_ARN,
                Message=formatMessage(data),
                Subject='AWS Service Limits >= 80%'
        )
        logger.info('Published message {} to SNS topic'.format(response.get('MessageId','')))
    except Exception as e:
        logger.error('Problem sending message to SNS: {}'.format(str(e)))
        raise

def lambda_handler(event, context):
    support_client = boto3.client('support')
    try:
        """Refresh checks then get the data"""
        response = support_client.refresh_trusted_advisor_check(checkId=CHECK_ID)
        logger.info('Status of check refresh: {}'.format(response))
        response = support_client.describe_trusted_advisor_check_result(checkId=CHECK_ID,
                                                                language='en')
        checks = response.get('result').get('flaggedResources',[])
    except Exception as e:
        logger.error('Problem getting trusted advisor checks: {}'.format(str(e)))
        return {'status': 'failed'}
    cached_limits = getCachedLimits()
    """Turn the current limits into a JSON object for comparison"""
    current_limits = dict(
        updated = datetime.now().isoformat(' '),
        flagged = [check for check in checks if check.get('status') == 'warning']
    )
    if cached_limits['flagged'] != current_limits['flagged']:
        logger.info('Current limit check does not match cached version. Sending update.')
        logger.debug('Cached: {}\nCurrent: {}'.format(cached_limits, current_limits))
        sendUpdate(current_limits)
        updateCurrentValues(current_limits)
        return {'status': 'success', 'update': True}
    else:
        logger.info('Cached and current limits are the same.')
        return {'status': 'success', 'update': False}
