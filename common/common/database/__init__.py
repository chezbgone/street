import boto3

from config import CONFIG

_boto_config = {}
_boto_config['region_name'] = 'us-east-1'

if not CONFIG['production_mode']:
    _boto_config['aws_access_key_id'] = 'anything'
    _boto_config['aws_secret_access_key'] = 'anything'
    _boto_config['endpoint_url'] = 'http://db:8000'

def dynamoDB():
    return boto3.resource('dynamodb', **_boto_config)
