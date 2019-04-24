import json
import os
import logging
import time

import requests
from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.core import patch_all
import boto3

patch_all()

# Add after all imports
import epsagon

epsagon.init(
    token='',
    app_name='Epsagon SAM Example',
    metadata_only=False,
)


logger = logging.getLogger()
logger.setLevel(logging.INFO)

@epsagon.lambda_wrapper
def lambda_handler(event, context):
    """Sample pure Lambda function

    Parameters
    ----------
    event: dict, required
        API Gateway Lambda Proxy Input Format

        {
            "resource": "Resource path",
            "path": "Path parameter",
            "httpMethod": "Incoming request's method name"
            "headers": {Incoming request headers}
            "queryStringParameters": {query string parameters }
            "pathParameters":  {path parameters}
            "stageVariables": {Applicable stage variables}
            "requestContext": {Request context, including authorizer-returned key-value pairs}
            "body": "A JSON string of the request payload."
            "isBase64Encoded": "A boolean flag to indicate if the applicable request payload is Base64-encode"
        }

        https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html#api-gateway-simple-proxy-for-lambda-input-format

    context: object, required
        Lambda Context runtime methods and attributes

    Attributes
    ----------

    context.aws_request_id: str
         Lambda request ID
    context.client_context: object
         Additional context when invoked through AWS Mobile SDK
    context.function_name: str
         Lambda function name
    context.function_version: str
         Function version identifier
    context.get_remaining_time_in_millis: function
         Time in milliseconds before function times out
    context.identity:
         Cognito identity provider context when invoked through AWS Mobile SDK
    context.invoked_function_arn: str
         Function ARN
    context.log_group_name: str
         Cloudwatch Log group name
    context.log_stream_name: str
         Cloudwatch Log stream name
    context.memory_limit_in_mb: int
        Function memory

        https://docs.aws.amazon.com/lambda/latest/dg/python-context-object.html

    Returns
    ------
    API Gateway Lambda Proxy Output Format: dict
        'statusCode' and 'body' are required

        {
            "isBase64Encoded": true | false,
            "statusCode": httpStatusCode,
            "headers": {"headerName": "headerValue", ...},
            "body": "..."
        }

        # api-gateway-simple-proxy-for-lambda-output-format
        https: // docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html
    """

    try:
        xray_recorder.begin_subsegment('HelloSubsegment')
        xray_recorder.put_annotation('SubHelloAnnotation', 'SubHello')
        xray_recorder.put_metadata('SubHelloMeta', 'SubMeta', 'SubSegmentMetaNamespace')
        # Put something into dynamodb

        time.sleep(1)
        xray_recorder.end_subsegment()

        logger.info('got event{}'.format(event))
        logger.info(os.environ)
        ip = requests.get("http://checkip.amazonaws.com/")
        logger.info('requesting goodby')
        resp = requests.get("https://myrr2f778a.execute-api.us-east-1.amazonaws.com/Stage/goodby")
        logger.info('got response{}'.format(resp))
    except requests.RequestException as e:
        # Send some context about this error to Lambda Logs
        print(e)

        raise e

    return {
        "statusCode": 200,
        "body": json.dumps(
            {"message": "hello world", "location": ip.text.replace("\n", "")}
        ),
    }


@epsagon.lambda_wrapper
def lambda_handler2(event, context):
    try:
        logger.info('in good by handler with event{}'.format(event))
        logger.info(os.environ)
        sqs = boto3.client('sqs')
        response = sqs.send_message_batch(Entries=[
            {
                'Id': '1',
                'MessageBody': 'world'
            },
            {
                'Id': '2',
                'MessageBody': 'boto3',
                'MessageAttributes': {
                    'Author': {
                        'StringValue': 'Daniel',
                        'DataType': 'String'
                    }
                }
            }
        ], QueueUrl=os.environ['qname'])
        logger.info(response)
    except requests.RequestException as e:
        # Send some context about this error to Lambda Logs
        print(e)

        raise e

    return {
        "statusCode": 200,
        "body": json.dumps(
            {"message": "goodby world"}
        ),
    }


@epsagon.lambda_wrapper
def lambda_handler3(event, context):
    try:
        client = boto3.client('sns')
        logger.info('in sqs handler with event{}'.format(event))
        logger.info(os.environ)
        client.publish(TopicArn=os.environ['topic'], Message='SNSISENT!!!!')
    except requests.RequestException as e:
        # Send some context about this error to Lambda Logs
        print(e)

        raise e

    return None


@epsagon.lambda_wrapper
def lambda_handler4(event, context):
    try:
        logger.info('in sns handler with event{}'.format(event))
        logger.info(os.environ)
    except requests.RequestException as e:
        # Send some context about this error to Lambda Logs
        print(e)

        raise e

    return None
