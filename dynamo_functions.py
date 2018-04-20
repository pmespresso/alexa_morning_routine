import boto3

boto3.setup_default_session(region_name='us-east-1')

# DynamoDB Databases
dynamodb = boto3.resource('dynamodb')
user_table = dynamodb.Table('morning_routine_users')

def get_user_state(user_id):
    ''' 
        Intent : Get user routine state.
        Params : user_id - Alexa User ID
        Return : State<int>/Error<String>/Not Found<String>
    '''
    try:
        response = user_table.get_item(Key={'user_id': user_id})
    except Exception as e:
        print(e.response['Error']['Message'])
        return 'Error'
    else:
        if('Item' in response and 'state' in response['Item']):
            return response['Item']['state']
        else:
            return 'Not Found'
            
def insert_user_state(user_id, state=1):
    '''
        Intent : Insert User Routine State
        Params : user_id - Alexa User ID
                 state - Routine State
        Return : success flag - True/False 
    '''
    try:
        response = user_table.put_item(
           Item={
                'user_id': user_id,
                'state': state
            }
        )
        print("Inserted {} with routine state {}".format(user_id,state))
        return True
    except Exception as e:
        print(e.response['Error']['Message'])
        return False