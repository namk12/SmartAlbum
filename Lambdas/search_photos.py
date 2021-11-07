import json
import boto3
import requests
import logging

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

def searchElasticIndex(search):
    photos = []
    for s in search:
        host = 'https://search-photo-bfekp4qquelaimy4ky5dwps6na.us-east-2.es.amazonaws.com/photos/_search?q='+s
        res = requests.get(host,auth=('nk2863','NamKap@14310'))
        res = json.loads(res.content.decode('utf-8'))
        for item in res["hits"]["hits"]:
            bucket = item["_source"]["bucket"]
            key = item["_source"]["objectKey"]
            photoURL = "https://{0}.s3.amazonaws.com/{1}".format(bucket,key)
            photos.append(photoURL)
    return photos

def prepareForSearch(res):
    photos = []
    if res["slots"]["a"] != None:
        photos.append(res["slots"]["a"])
    if res["slots"]["b"] != None:
        photos.append(res["slots"]["b"])
    return photos

def sendToLex(message):
    lex = boto3.client('lex-runtime','us-east-1')
    response = lex.post_text(
        botName='PhotoBot',
        botAlias='demo',
        userId='45s45',
        inputText=message)
    print(response)
    return response
    
def lambda_handler(event, context):
    # TODO implement
    logger.debug("inside")
    logger.debug(event)
    photos = []
    message = event["queryStringParameters"]["q"]
    resFromLex = sendToLex(message)
    search = prepareForSearch(resFromLex)
    photos = searchElasticIndex(search)
    
    logger.debug(photos)
    
    res = {"results": photos}
    
    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Headers': '*',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': '*'
        },
        'body': json.dumps(res)
    }