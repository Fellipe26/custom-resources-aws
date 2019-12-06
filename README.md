# custom-resources-aws
Custom resources aws

**How to use this custom resource**

***Create folder s3***

```
AWSTemplateFormatVersion: '2010-09-09'
Description: CF automation template Create Folder for Bucket

Parameters:
  AccessControl:
    Type: String  
  BucketName:
    Type: String 
  BlockPublicAcls: 
    Type: String
  BlockPublicPolicy: 
    Type: String
  IgnorePublicAcls: 
    Type: String
  RestrictPublicBuckets: 
    Type: String
  Product:
    Type: String
  Environment:
    Type: String

Resopurces:
  BucketS3:
    Type: AWS::S3::Bucket
    Properties: 
      AccessControl: !Ref AccessControl
      BucketName: !Ref BucketName
      PublicAccessBlockConfiguration: 
        BlockPublicAcls: !Ref BlockPublicAcls
        BlockPublicPolicy: !Ref BlockPublicPolicy
        IgnorePublicAcls: !Ref IgnorePublicAcls
        RestrictPublicBuckets: !Ref RestrictPublicBuckets
      Tags:
        - 
          Key: "Product"
          Value: !Ref Product
        - 
          Key: "Environment"
          Value: !Ref Environment

  S3FolderGenerator:
    Type: AWS::CloudFormation::CustomResource
    DependsOn:
      - BucketS3
    Properties:
      ServiceToken: !ImportValue S3InfoResource
      Bucket: !GetAtt BucketGenerator.Outputs.BucketName
      Key: 
        - one
        - two
        - three
        - four
        - ...

Outputs:
  BucketName:
    Value: !Ref 'BucketS3'
    Description: Name of the AWS S3 bucket
    Export:
      Name: 
        'Fn::Sub': '${AWS::StackName}-BucketName'
  BucketArn:
    Value: !GetAtt 'BucketS3.Arn'
    Description: Arn of the AWS S3 bucket
    Export:
      Name: 
        'Fn::Sub': '${AWS::StackName}-BucketArn'
  BucketDomainName:
    Value: !GetAtt 'BucketS3.DomainName'
    Description: DomainName of the AWS S3 bucket
    Export:
      Name:
        'Fn::Sub': '${AWS::StackName}-BucketDomainName'
```



***Create put-target for aws batch***

```
AWSTemplateFormatVersion: '2010-09-09'
Description: CF automation template put-target fow aws batch

Parameters:
  CloudWatchLogsRetentionInDays:
    Description: 'The number of days log events are kept in CloudWatch Logs'
    Type: Number
    Default: 3653
    AllowedValues: [1, 3, 5, 7, 14, 30, 60, 90, 120, 150, 180, 365, 400, 545, 731, 1827, 3653]
  ImageVersion:
    Type: String
  Environment:
    Type: String
  BucketTrailLogName:
    Type: String
  PierConnectionTimeout:
    Type: String
  PierReadTimeout:
    Type: String
  BucketOne:
    Type: String
  BucketTwo:
    Type: String
  JobQueueName:
    Type: String

Conditions:
  isItProd:
    !Or
    - !Equals [ !Ref Environment, prd ]
    - !Equals [ !Ref Environment, prdbr ]

  isNotPrdBr:
    !Not [ !Equals [ !Ref Environment, prdbr ] ]

Mappings:
  batch:
    version:
      value: 0.291.0
  jobQueue:
    version:
      value: 0.291.0
  S3Bucket:
    version:
      value: 0.333.0

Resources:
  Computeenvironment:
    Type: AWS::CloudFormation::Stack
    Properties:
      Parameters:
        KeyName: !Ref KeyName
        MaxvCpus: 4
        MinvCpus: 0
        DesiredvCpus: 0
        InstanceTypes: c5.large
        VpcId:
          Fn::ImportValue:
            !If
            - isNotPrdBr
            - vpc-vpc
            - vpc
        ImageId: !If [ isItProd, ami-09987452123fadc5b, ami-007571470797b8ffa ]
        Subnets:
          !Join
          - ','
          - - !ImportValue vpc-subnetPrvC
            - !If
              - isItProd
              - !ImportValue vpc-subnetPrvA
              - !ImportValue vpc-subnetPrvB
      TemplateURL:
        !Sub
        - "https://s3.amazonaws.com/local-your-template/aws_batch_compute_environment-${version}.yml"
        - { version: !FindInMap [ batch, version, value ] }

  JobDefinition:
    Type: AWS::Batch::JobDefinition
    Properties:
      Type: container
      JobDefinitionName: HellowHordTesteTargetJobDefinition
      ContainerProperties:
        Memory: !Ref Memory
        Privileged: true
        JobRoleArn: !GetAtt Computeenvironment.Outputs.RoleJobDefinition
        ReadonlyRootFilesystem: true
        Vcpus: !Ref Vcpus
        Image: !Sub 45648465456465.dkr.ecr.us-east-1.amazonaws.com/hellowHord-teste-target:${ImageVersion}
        Command:
          - sh
          - execute.sh
          - 'Ref::S3Bucket'
          - 'Ref::S3Key'
        Environment:
          - Name: one
            Value: !Ref one
          - Name: two
            Value: !Ref two
          - Name: three
            Value: !Ref three
          - Name: four
            Value: !Ref four

  JobQueue:
    Type: AWS::CloudFormation::Stack
    DependsOn:
      - Computeenvironment
    Properties:
      Parameters:
        ComputeEnvironment: !GetAtt Computeenvironment.Outputs.ComputeEnvironmentArn
        JobQueueName: !Ref JobQueueName
        Priority: 100
      TemplateURL:
        !Sub
        - "https://s3.amazonaws.com/local-your-template/aws_batch_job_queue-${version}.yml"
        - { version: !FindInMap [ jobQueue, version, value ] }

  EventBatchTesteTarget:
    Type: AWS::Events::Rule
    DependsOn: 
      - JobQueue
      - S3BucketOne
      - S3BucketTwo
    Properties:
      Description: Event para disparar o -teste-nexoos
      Name: hellowHord-teste-target
      EventPattern:
        source:
          - aws.s3
        detail-type:
          - AWS API Call via CloudTrail
        detail:
          eventSource:
            - s3.amazonaws.com
          eventName:
            - PutObject
          requestParameters:
            bucketName:
              - !Ref BucketOne
              - !Ref BucketTwo
      State: ENABLED

  Target:
    Type: AWS::CloudFormation::CustomResource
    DependsOn:
      - EventBatchTesteTarget
    Properties:
      ServiceToken: !ImportValue targetEventInfoResource
      Rule: hellowHord-teste-target
      Arn: !Join ["/", [!Sub "arn:aws:batch:${AWS::Region}:${AWS::AccountId}:job-queue", "HellowHordTesteTarget"]]
      Id: Id1234
      RoleArn: !Join ["/", [!Sub "arn:aws:iam::${AWS::AccountId}:role" , "service-role" , "AWS_Events_Invoke_Batch_Job_Queue_2083888063"]]
      InputTransformer:
        InputPathsMap:
          S3KeyValue: $.detail.requestParameters.key
          S3BucketValue: $.detail.requestParameters.bucketName
        InputTemplate:
          Parameters:
            S3Bucket: <S3BucketValue>
            S3Key: <S3KeyValue>
      BatchParameters:
        JobDefinition: HellowHordTesteTargetJobDefinition
        JobName: hellowHord-teste-target

  S3BucketOne:
    Type: AWS::CloudFormation::Stack
    Properties:
      Parameters:
        AccessControl: Private
        BucketName: !Ref BucketOne
        BlockPublicAcls: true
        BlockPublicPolicy: true
        IgnorePublicAcls: true
        RestrictPublicBuckets: true
      TemplateURL:
        !Sub 
          - "https://s3.amazonaws.com/local-your-template/s3-${version}.yml"
          - { version: !FindInMap [ S3Bucket, version, value ] }

  S3BucketTwo:
    Type: AWS::CloudFormation::Stack
    Properties:
      Parameters:
        AccessControl: Private
        BucketName: !Ref BucketTwo
        BlockPublicAcls: true
        BlockPublicPolicy: true
        IgnorePublicAcls: true
        RestrictPublicBuckets: true
      TemplateURL:
        !Sub 
          - "https://s3.amazonaws.com/local-your-template/s3-${version}.yml"
          - { version: !FindInMap [ S3Bucket, version, value ] }
          
  S3FolderNexoos:
    Type: AWS::CloudFormation::CustomResource
    DependsOn:
      - S3BucketOne
    Properties:
      ServiceToken: !ImportValue S3InfoResource
      Bucket: !Ref BucketOne
      Key: 
        - input
        - output
        - result
        - error          

  S3FolderGetNet:
    Type: AWS::CloudFormation::CustomResource
    DependsOn:
      - S3BucketTwo
    Properties:
      ServiceToken: !ImportValue S3InfoResource
      Bucket: !Ref BucketTwo
      Key: 
        - input
        - output
        - result
        - error

  S3BucketTrailLog:
    Type: AWS::CloudFormation::Stack
    Properties:
      Parameters:
        AccessControl: Private
        BucketName: !Ref BucketTrailLogName
        BlockPublicAcls: true
        BlockPublicPolicy: true
        IgnorePublicAcls: true
        RestrictPublicBuckets: true
      TemplateURL:
        !Sub 
          - "https://s3.amazonaws.com/local-your-template/s3-${version}.yml"
          - { version: !FindInMap [ S3Bucket, version, value ] }

  AWSCloudTrailBucketPolicy:
    DependsOn: 
      - S3BucketTrailLog
    Type: AWS::S3::BucketPolicy
    Properties:
      Bucket: !Ref BucketTrailLogName
      PolicyDocument:
        Version: 2012-10-17
        Statement:
          - Sid: "AWSCloudTrailAclCheck"
            Effect: Allow
            Principal:
              Service: 'cloudtrail.amazonaws.com'
            Action: 's3:GetBucketAcl'
            Resource: !Sub 'arn:aws:s3:::${BucketTrailLogName}'
          - Sid: "AWSCloudTrailWrite"
            Effect: Allow
            Principal:
              Service: 'cloudtrail.amazonaws.com'
            Action: 's3:PutObject'
            Resource: !Sub 'arn:aws:s3:::${BucketTrailLogName}/AWSLogs/${AWS::AccountId}/*'

  TrailTeste:
    DependsOn:
      - S3BucketOne
      - S3BucketTwo
      - AWSCloudTrailBucketPolicy
      - TrailLogGroupRole
    Type: AWS::CloudTrail::Trail
    Properties:
      TrailName: HellowHordTesteTarget
      EnableLogFileValidation: false
      EventSelectors:
        - DataResources:
            - Type: 'AWS::S3::Object'
              Values: 
                - !Sub 'arn:aws:s3:::${BucketOne}/input'
                - !Sub 'arn:aws:s3:::${BucketTwo}/input'
          IncludeManagementEvents: true
          ReadWriteType: WriteOnly
      IncludeGlobalServiceEvents: false
      IsLogging: true
      IsMultiRegionTrail: false
      S3BucketName: !Ref BucketTrailLogName
      CloudWatchLogsLogGroupArn: !GetAtt TrailLogGroup.Arn
      CloudWatchLogsRoleArn: !GetAtt TrailLogGroupRole.Arn

  TrailLogGroup:
    Type: 'AWS::Logs::LogGroup'
    Properties:
      RetentionInDays: !Ref CloudWatchLogsRetentionInDays

  TrailLogGroupRole:
    DependsOn: 
      - TrailLogGroup
    Type: 'AWS::IAM::Role'
    Properties:
      AssumeRolePolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Sid: AssumeRole1
            Effect: Allow
            Principal:
              Service: 'cloudtrail.amazonaws.com'
            Action: 'sts:AssumeRole'
      Policies:
        - PolicyName: 'cloudtrail-policy'
          PolicyDocument:
            Version: '2012-10-17'
            Statement:
              - Effect: Allow
                Action:
                  - 'logs:CreateLogStream'
                  - 'logs:PutLogEvents'
                Resource: !GetAtt 'TrailLogGroup.Arn'
```