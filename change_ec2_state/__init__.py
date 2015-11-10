"""
This script will stop or start instances in any region
with a specified tag. For example, to start instances
with the tag:startup = true, set the following:

    STATE = 'start'
    STATE_MAP = {'start': {'tag': 'startup', 'value': 'true'}}

To shutdown instances with tag:shutdown = true:

    STATE = 'stop'
    STATE_MAP = {'stop' : {'tag': 'shutdown', 'value': 'true'}}
"""
from boto3 import resource, client
from botocore.exceptions import ClientError
import logging

########
# Config
########
logger = logging.getLogger()
logger.setLevel(logging.INFO)

STATE = 'start'
STATE_MAP = {'start' : {'tag': 'startup', 'value': 'true'}}

########

def _getRegions():
    logger.info('Getting list of regions')
    ec2 = client('ec2')
    regions = []
    try:
        for region in ec2.describe_regions().get('Regions', []):
            regions.append(region)
        logger.debug('Regions: %s' % regions)
        return regions
    except ClientError as e:
        logger.error('Problem retreiving regions: %s' % str(e))
        raise

def lambda_handler(event, context):
    """Get a list of active regions"""
    logger.info('Starting lambda_handler()')
    logger.debug('event: %s\ncontent: %s' % (event, context))
    all_instances = {}
    regions = _getRegions()
    for region in regions:
        if 'RegionName' not in region:
            raise Exception('Unknown region returned')
        ec2 = resource('ec2', region_name=region['RegionName'])

        """Retrieve instances in this region """
        logger.info('Retrieving instances from %s' % region['RegionName'])
        if STATE == 'stop':
            instance_filter = ['running']
        elif STATE == 'start':
            instance_filter = ['stopped']
        else:
            raise Exception('Unknown instance state specified')
        instances = ec2.instances.filter(
            Filters=[{'Name': 'instance-state-name', 'Values': instance_filter}])
        instances_to_change = []

        """Look at the tags of the returned instances and determine
        whether or not the state should be changed"""
        for instance in instances:
            logger.info('Checking tags on instance %s' % instance.id)
            for tag in instance.tags:
                if STATE in STATE_MAP:
                    key = STATE_MAP[STATE]['tag']
                    value = STATE_MAP[STATE]['value']
                else:
                    raise Exception('Can not determine what tags to verify')
                if tag['Key'] == key and tag['Value'] == value:
                    instances_to_change.append(instance.id)
                    logger.info('Instance %s will change state to %s'
                                % (instance.id, STATE))

        if len(instances_to_change) > 0:
            all_instances[region['RegionName']] = instances_to_change
            logger.info('Changing state on instances: %s' % (instances_to_change))
            try:
                if STATE == 'start':
                    response = ec2.instances.filter(InstanceIds=instances_to_change).start()
                elif STATE == 'stop':
                    response = ec2.instances.filter(InstanceIds=instances_to_change).stop()
                else:
                    raise Exception('Unknown state specified')
            except:
                raise Exception('Problem changing instance state')
            else:
                logger.debug('Response from command: %s' % response)
                if len(response) == 1:
                    if ('ResponseMetadata' in response[0]):
                        """Check the return code"""
                        if response[0]['ResponseMetadata']['HTTPStatusCode'] != 200:
                            logger.warning('Unexpected status code returned: %d'
                            % response[0]['ResponseMetadata']['HTTPStatusCode'])
                        else:
                            logger.info('Successfully changed %s state in region %s'
                                         % (instances_to_change, region['RegionName']))
                    else:
                        logger.warn('Missing keys from response')
                else:
                    logger.warn('Unknown length of response')
            finally:
                logger.info('State change in region complete')
        else:
            logger.info('No instances to change')
    return all_instances
