import boto3

s3 = boto3.client('s3')

# This is an origin request function
def lambda_handler(event, context):

    request = event['Records'][0]['cf']['request']
    headers = request['headers']

    # Only do the processing for manifest files
    if request['uri'].find('.m3u8') == -1:
        return request

    transformed = s3.get_object(
        Bucket='arn:aws:s3-object-lambda:ap-east-1:693858346231:accesspoint/elemental-object-lambda-ap',
        Key=request['uri'].lstrip('/'))

    manifestContent = transformed['Body'].read().decode('utf-8')

    # Only do the processing for master manifest files
    if manifestContent.find('#EXT-X-STREAM-INF') == -1:
        return request

    # Generate HTTP OK response using 200 status code with HTML body.
    response = {
        'status': '200',
        'statusDescription': 'OK',
        'headers': {
            'cache-control': [
                {
                    'key': 'Cache-Control',
                    'value': 'max-age=2'
                }
            ],
            "content-type": [
                {
                    'key': 'Content-Type',
                    'value': 'application/x-mpegURL'
                }
            ]
        },
        'body': manifestContent
    }
    return response
