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
            return int(response['Item']['state'])
        else:
            return 'Not Found'
            
def get_exercise_times(user_id):
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
        print('RESPONSE FROM GETTING EXERCISE TIMES : {}'.format(response))
        if('Item' in response and 'exercise_start_time' in response['Item'] and 'exercise_end_time' in response['Item']):
            return response['Item']['exercise_start_time']+','+response['Item']['exercise_end_time']
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
                'state': state,
                'exercise_start_time': '',
                'exercise_end_time': ''
            }
        )
        print("Inserted {} with routine state {}".format(user_id,state))
        return True
    except Exception as e:
        print(e.response['Error']['Message'])
        return False
   
def update_user_state(user_id, state):
    '''
        Intent : Insert User Routine State
        Params : user_id - Alexa User ID
                 state - Routine State
        Return : success flag - True/False 
    '''
    try:
        response = user_table.update_item(
           Key = {'user_id': user_id},
           AttributeUpdates={
                'state': {
                             'Value': state,
                             'Action': 'PUT'
                         }
            }
        )
        print("Updated {} with routine state {}".format(user_id,state))
        return True
    except Exception as e:
        print(e.response['Error']['Message'])
        return False
   
def update_user_exercise_start(user_id, start_time):
    '''
        Intent : Insert User Routine State
        Params : user_id - Alexa User ID
                 state - Routine State
        Return : success flag - True/False 
    '''
    try:
        response = user_table.update_item(
           Key = {'user_id': user_id},
           AttributeUpdates={
                'exercise_start_time': {
                             'Value': start_time,
                             'Action': 'PUT'
                         }
            }
        )
        
        print("Updated {} with exercise start time {}".format(user_id, start_time))
        return True
    except Exception as e:
        print(e.response['Error']['Message'])
        return False
        
def update_user_exercise_end(user_id, end_time):
    '''
        Intent : Insert User Routine State
        Params : user_id - Alexa User ID
                 state - Routine State
        Return : success flag - True/False 
    '''
    try:
        response = user_table.update_item(
           Key = {'user_id': user_id},
           AttributeUpdates={
                'exercise_end_time': {
                             'Value': end_time,
                             'Action': 'PUT'
                         }
            }
        )
        print("Updated {} with exercise end time {}".format(user_id,end_time))
        return True
    except Exception as e:
        print(e.response['Error']['Message'])
        return False