import putTarget

event={
 'RequestType': 'Create',
 'ServiceToken': 'arn-your-function-resource',
 'ResponseURL': 'https://cloudformation-custom-resource-response-useast1.s3.amazonaws.com/arn%3Aaws%3Acloudformation%3Aus-east-1%3A994357011367%3Astack/user-sftp-teste/1d5fd5d0-d4e5-11e9-950a-1202dd259b0c%7CS3Folder%7C326eb322-b0b0-4858-9b46-84b7295f9769?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date=20190911T224052Z&X-Amz-SignedHeaders=host&X-Amz-Expires=7200&X-Amz-Credential=AKIA6L7Q4OWTTYC3DXNI%2F20190911%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Signature=e50ed842bb0febd7beb13ab24103a2be03a010a39438aefe9325058523daea11',
 'StackId': 'arn:aws:cloudformation:us-east-1:4984894561561516:stack/user-teste/1d5fd5d0-d4e5-11e9-950a-1202dd259b0c',
 'RequestId': '326eb322-b0b0-4858-9b46-84b7295f9769',
 'LogicalResourceId': 'S3Folder',
 'ResourceType': 'AWS::CloudFormation::CustomResource',
 'ResourceProperties': {
    'Rule': 'name-your-rule',
    'ServiceToken': 'arn-your-function-resource',
    'Arn': 'arn-your-job-queue',
    'Id': 'ID',
    'RoleArn': 'arn-your-role',
    "InputTransformer": {
      "InputPathsMap": {
        "S3KeyValue": "$.detail.requestParameters.key"
      },
      "InputTemplate": "{\"Parameters\" : {\"S3key\": <S3KeyValue>}}"
    },    
    'BatchParameters': {
      'JobDefinition': 'name-this-jobDefinition',
      'JobName': 'name-this-job'
    }
 }
}

putTarget.lambda_handler(event, '')