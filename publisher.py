import json
import urllib.parse
import boto3
import uuid

# Create SQS client
sqs = boto3.client('sqs')

queue_url = os.environ['SQS_QUEUE']

def lambda_handler(event, context):
    # Get the object from the event
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    other_key = uuid.uuid4()

    log = {
        "id": str(other_key),
        "key": key,
        "bucket": bucket, 
    }

    try:
        # Send message to SQS queue
        response = sqs.send_message(
            QueueUrl=queue_url,
            DelaySeconds=10,
            MessageBody=(json.dumps(log))
        )
        
        return log
    except Exception as e:
        print(e)
        print('Error getting object {} from bucket {}. Make sure they exist and your bucket is in the same region as this function.'.format(key, bucket))
        raise e
