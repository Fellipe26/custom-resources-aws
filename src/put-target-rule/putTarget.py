import json
import requests
import boto3
import uuid

#session = boto3.Session(profile_name='dev')
#s3_client = session.client('events')

s3_client = boto3.client('events')
global response_aws_client

def lambda_handler(event, context):

    """ lambda responsavel por adicionar o target ao event rule."""

    try:
        print('Event : %s' % str(event))
        print('Context : %s' % str(context))
        
        response = {
            'StackId': event['StackId'],
            'RequestId': event['RequestId'],
            'LogicalResourceId': event['LogicalResourceId'],
            'Status': 'SUCCESS',
            'Data': {}
        }

        print (response)
        
        if 'PhysicalResourceId' in event:
            response['PhysicalResourceId'] = event['PhysicalResourceId']
        else:
            response['PhysicalResourceId'] = str(uuid.uuid4())

        data = event['ResourceProperties']

        print (data)

        if event.get('RequestType') == 'Create':
            print('create')
            response_aws_client = add_target(data=data)

        elif event.get('RequestType') == 'Update':
            print('Update')
            response_aws_client = update_target(data=data)

        elif event.get('RequestType') == 'Delete':
            print('Delete')
            delete_target(data=data)

        else:
            print('Failed')
            response['Status'] = 'FAILED'

        if 'PhysicalResourceId' in event:
            response['PhysicalResourceId'] = event['PhysicalResourceId']
        else:
            response['PhysicalResourceId'] = str(uuid.uuid4())

        return send_response(event, response)

    except Exception as err:
        exception_type = err.__class__.__name__
        exception_message = str(err)

        api_exception_obj = {
            "isError": True,
            "type": exception_type,
            "message": exception_message
        }

        print (event)

        response = {
            'StackId': event['StackId'],
            'RequestId': event['RequestId'],
            'LogicalResourceId': event['LogicalResourceId'],
            'Status': 'FAILED',
            'Reason': exception_message
        }

        print (response)

        if 'PhysicalResourceId' in event:
            response['PhysicalResourceId'] = event['PhysicalResourceId']
        else:
            response['PhysicalResourceId'] = str(uuid.uuid4())

        send_response(event, response)

        api_exception_json = json.dumps(api_exception_obj)
        raise LambdaException(api_exception_json)

def send_response(request, response):

    """
        Função criada para enviar a resposta para o cloudformation
        Input:
            Request:
                - Tipo: dict
                - Descrição: Dicionario com informações do event
            response:
                - Tipo: dict
                - Descrição: Dicionario com informações do response
    """

    if 'ResponseURL' in request and request['ResponseURL']:
        try:
            body = json.dumps(response)
            requests.put(request['ResponseURL'], data=body)
            print(response)
        except:
            print("Failed to send the response to the provdided URL")
    return response

def add_target(**kwargs):
    
    info = kwargs['data']
    print (info)
    
    if 'InputTransformer' in info:
        inputPathsMap = dict(info["InputTransformer"]["InputPathsMap"])
        inputTemplate = json.dumps(info["InputTransformer"]["InputTemplate"]).replace('"<', '<').replace('>"', '>')

        print('inputTemplace: ' + inputTemplate)
        
        response = s3_client.put_targets(
            Rule=info['Rule'],
            Targets=[
                {
                    "Arn": info['Arn'],
                    "Id": info['Id'],
                    "RoleArn": info['RoleArn'],
                    "InputTransformer":{
                        "InputPathsMap": inputPathsMap,
                        "InputTemplate": inputTemplate
                    },
                    "BatchParameters": {
                      "JobDefinition": info['BatchParameters']['JobDefinition'],
                      "JobName": info['BatchParameters']['JobName']
                    }
                }
            ]
        )    

    else:
        response = s3_client.put_targets(
            Rule=info['Rule'],
            Targets=[
                {
                    "Arn": info['Arn'],
                    "Id": info['Id'],
                    "RoleArn": info['RoleArn'],
                    "BatchParameters": {
                      "JobDefinition": info['BatchParameters']['JobDefinition'],
                      "JobName": info['BatchParameters']['JobName']
                    }
                }
            ]
        )  

    return response

def update_target(**kwargs):

    info = kwargs['data']
    data = kwargs['data']
    print (info)
    
    response = s3_client.list_targets_by_rule(
        Rule=info['Rule']
    )
    print (response)
    
    ServiceToken = info.pop('ServiceToken')
    Rule = info.pop('Rule')
    Arn = info.pop('Arn')

    targetReceive = info
    targetIdReceive = targetReceive['Id']
    
    for target in response['Targets']:
        targetId = target['Id']
        print('targetId: ' + targetId)

        if (targetIdReceive == targetId) and (target != targetReceive):
            print ('Deletando...')
            print (kwargs['data'])
            
            info['ServiceToken'] = ServiceToken
            info['Rule'] = Rule
            info['Arn'] = Arn

            delete_target(data=info)

            print ('Atualizando...')
            add_target(data=info)

def delete_target(**kwargs):

    info = kwargs['data']
    print (info)
    
    response = s3_client.remove_targets(
        Rule=info['Rule'],
        Ids=[
            info['Id']
        ]
    )

    return response

class LambdaException(Exception):
    pass