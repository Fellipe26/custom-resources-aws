import json
import requests
import boto3
import uuid


s3_client = boto3.client('s3')
global response_aws_client

def lambda_handler(event, context):

    """ lambda responsavel por realizar a criação do diretorio do S3."""

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
            response_aws_client = create_s3_folder(data=data)

        elif event.get('RequestType') == 'Update':
            print('Update')
            response_aws_client = update_s3_folder(data=data)

        elif event.get('RequestType') == 'Delete':
            print('Delete') 
            delete_s3_folder(data=data)

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

def create_s3_folder(**kwargs):
    
    info = kwargs['data']
    print (info)
    keys = info['Key']

    for key in keys : 
        print ('Create folder: ' + key)
        response = s3_client.put_object(
            Bucket=info['Bucket'],
            Key=(key + '/')
        )

    return response

def update_s3_folder(**kwargs):

    info = kwargs['data']
    print (info)
    print ('Deletando...')
    delete_s3_folder(data=info)
    print ('Criando...')
    create_s3_folder(data=info)

def delete_s3_folder(**kwargs):

    info = kwargs['data']
    print (info)
    
    keys = info['Key']

    for key in keys : 
        print ('Deleting folder: ' + key)
        response = s3_client.delete_object(
            Bucket=info['Bucket'],
            Key=(key + '/')
        )
    return response

class LambdaException(Exception):
    pass