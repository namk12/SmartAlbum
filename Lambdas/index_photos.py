import json
import logging
import boto3
import requests
from opensearchpy import OpenSearch, RequestsHttpConnection

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)



def detect_labels(photo, bucket):

    rekog = boto3.client('rekognition','us-east-2')
    s3 = boto3.client('s3','us-east-2')

    response = rekog.detect_labels(Image={'S3Object':{'Bucket':bucket,'Name':photo}},MaxLabels=10,MinConfidence=90)
    
    headerData = s3.head_object(Bucket=bucket,Key=photo);
    userLabels = headerData['ResponseMetadata']['HTTPHeaders']['x-amz-meta-customlabels'];
    user_labels = [x.strip() for x in userLabels.split(',')]
    
    A1 = user_labels
    for label in response['Labels']:
        print(label['Name'])
        A1.append(label['Name'])
    
    logger.debug(A1)
    
    return A1
    
def storeInES(A1,event):
    #host = 'vpc-photos-n7ltjenzsp4c4uigejymrugpkq.us-east-2.es.amazonaws.com'  # For example, my-test-domain.us-east-1.es.amazonaws.com
    host = 'search-photo-bfekp4qquelaimy4ky5dwps6na.us-east-2.es.amazonaws.com'
    region = 'us-east-2'  # e.g. us-west-1
    service = 'es'
    
    search = OpenSearch(
        hosts=[{'host': host, 'port': 443}],
        http_auth=('nk2863','NamKap@14310'),
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection
    )
    
    res = {
        "objectKey":event['Records'][0]['s3']['object']['key'],
        "bucket":event['Records'][0]['s3']['bucket']['name'],
        "createdTimestamp":event['Records'][0]['eventTime'],
        "labels":A1
    }
    
    #print(res)
    search.index(index="photos", doc_type="photoIndex", id=event['Records'][0]['s3']['object']['key'], body=json.dumps(res), refresh=True)
    logger.debug('ES finished')
    
def lambda_handler(event, context):
    # TODO implement
    
    logger.debug(event)
    
    photo = event['Records'][0]['s3']['object']['key']
    bucket = event['Records'][0]['s3']['bucket']['name']
    
    #photo = "yyup.jpg"
    #bucket = "photobucket-b2"
    
    A1 = detect_labels(photo, bucket)
    
    storeInES(A1,event)
    
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }

