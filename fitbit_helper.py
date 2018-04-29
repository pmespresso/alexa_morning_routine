import requests
from datetime import datetime


def get_fitbit_timezone(token):
    profile_url = 'https://api.fitbit.com/1/user/-/profile.json'
    headers = {
                "accept": "application/x-www-form-urlencoded",
                "authorization": "Bearer {}".format(token)
              }
    resp = requests.get(profile_url, headers=headers)
    
    if(resp.ok):
        content = resp.json()
        if('user' in content and 'timezone' in content['user'] and content['user']['timezone']!=''):
            return content['user']['timezone']
        else:
            return 'Not Found'
    else:
        return 'Not Found'

def get_calories_from_exercise(date, start_time, end_time, token):

    # If start time is greater than end time
    if(int(start_time.split(':')[0])>int(end_time.split(':')[0])):
        return ' Looks like you left your exercise in the middle. Complete a full morning routine to get these insights. '
    
    speech_output = ' Try wearing and synchronizing your fitbit device for your morning routines to let me help you better. '
    act_url = 'https://api.fitbit.com/1/user/-/activities/calories/date/{}/1d/1min/time/{}/{}.json'.format(date, start_time, end_time)
    headers = {
                "accept": "application/x-www-form-urlencoded",
                "authorization": "Bearer {}".format(token)
              }
    resp = requests.get(act_url, headers=headers)
    if(resp.ok):
        content = resp.json()
        if('activities-calories' in content):
            if(len(content['activities-calories'])>0):
                calories_lost = content['activities-calories'][0]['value'].split('.')[0]
                if(calories_lost!='0'):
                    # Fibit worn and synchronized that day
                    speech_output = " Here is some motivation, You lost around, {} calories, the last time you exercised using this skill. If you think this is inaccurate, please sync your fitbit device using the fitbit app. ".format(str(calories_lost))
    
    return speech_output
    
#token = 'eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiI2NEpWNEoiLCJhdWQiOiIyMkNXVEciLCJpc3MiOiJGaXRiaXQiLCJ0eXAiOiJhY2Nlc3NfdG9rZW4iLCJzY29wZXMiOiJyYWN0IHJociByc2xlIiwiZXhwIjoxNTI0NzgxOTM0LCJpYXQiOjE1MjQ3NTMxMzR9.sDj0PLn7SFySQx_V1KmB_QxSR5lfauUhpCKRMASlg-A'
#date  = '2018-04-27'
#start_time = '20:00'
#end_time = '20:05'

#print(get_calories_for_exercise(date, start_time, end_time, token))