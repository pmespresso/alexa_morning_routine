import logging

from random import randint, choice

from flask import Flask, render_template

from flask_ask import Ask, statement, question, session, audio, current_stream, context, request

import soundcloud

import json

import requests

from dynamo_functions import get_user_state, insert_user_state, update_user_state, update_user_exercise_start, update_user_exercise_end, get_exercise_times

import pytz

from datetime import datetime

from fitbit_helper import get_calories_from_exercise, get_fitbit_timezone

from response_builders import build_speechlet_response_ssml, build_response

app = Flask(__name__)

ask = Ask(app, "/")

logger = logging.getLogger("flask_ask")
logger.setLevel(logging.DEBUG)

ROUTINE_INDEX = "index"
MAX_ROUTINE = 6
MAX_ROUTINE_REACHED = False
FITBIT = False

exercise_date = ''
exercise_start_time = ''
exercise_end_time = ''
exercise_insight = ''

routine_cards = [
    {
        "title": "Wake Up",
        "text": "First thing's first, get out of bed!!!"
    },
    {
        "title": "Make your bed!",
        "text": "The easiest way to start the day off on the right foot."
    },
    {
        "title": "Meditate",
        "text": "Just a little meditation to take care of your mind."
    },
    {
        "title": "Exercise",
        "text": "Get your blood flowing, and your metabolism revving. GET SOME!"
    },
    {
        "title": "Jump in a Cold Shower",
        "text": "Make sure to end your shower with at least 30 seconds of super cold water. You'll feel incredible afterwards."
    },
    {
        "title": "Drink some Tea or Coffee",
        "text": "There is no life before coffee"
    },
    {
        "title": "You're all done. Have an amazing day",
        "text": "Your morning routine has come to an end. Make sure to follow up tomorrow morning."
    }
]

motivation_list = [
    {
        "title": "Why you should make your bed!",
        "text": "If you make your bed every morning, you will have accomplished\
                the first task of the day. It will give you a small sense of pride,\
                and it will encourage you to do another task, and, another, and, another. "
    },
    {
        "title": "Meditate to solve your challenges!",
        "text": "regular meditation gives you time to practice control of your emotions,\
                which then influences how you react to challenges throughout the day. "
    },
    {
        "title": "Health is more important than you think!",
        "text": "getting into your body and exercising even for 30 seconds a day, has a \
                dramatic effect on your your mood and quiets mental chatter. "
    },
    {
        "title": "Shower to lose fat?",
        "text": "a quick 5 to 20 minutes cold shower, focusing on the back area, helps\
                the body to engage in some amount of, fat burning. "
    },
    {
        "title": "The Metabolism Boost!",
        "text": "drinking some light tea in the morning will get your metabolism fired up! "
    }
]

songs_list = [
    "https://s3.amazonaws.com/alexa-workout-sounds/Jay_Jay_conv_130.mp3",
    "https://s3.amazonaws.com/alexa-workout-sounds/Water_Lily_conv_130.mp3",
    "https://s3.amazonaws.com/alexa-workout-sounds/Wish_You_d_Come_True_conv_130.mp3"
]


def link_question(text):
    print('inside link')
    card_title = 'Link this skill with Fitbit.'
    speech_output = text
    reprompt_text = ' Say Next Routine to continue. '
    should_end_session = False
    card_type = 'LinkAccount'
    return json.dumps(build_response(session.attributes, build_speechlet_response_ssml(\
        card_title, speech_output, reprompt_text, should_end_session, card_type)))
 

@ask.intent('AMAZON.HelpIntent')
def help():
    speech_output = ''' I will guide you through your morning routine everyday, and give you motivation along the way. This skill is based on Tim Ferris's\
                         famous morning routine that is followed by a majority of people. If you link your fitbit\
                         device with this skill, I can keep track of how you are doing. After you complete a task, say, next task, to go to the next task. Ask me to play music at any time if you\
                         are still completing the task. If you ever need motivation to do a task, say, motivate me, to let me change your mind. Lastly, say, give\
                         me some insights, to let me help you understand your fitbit achievements for this morning routine. Say Stop, to exit this skill.\
                    '''
    card_title = 'Here to Help!'
    prompt = ' Say resume routine to continue. '
    card_text = ''' Based on Tim Ferris's famous morning routine.
                    Say Resume Task, or Next Task to navigate between tasks.
                    Say Done Or Mission Accomplished, to confirm finishing the task.
                    Say Motivate me, to get motivation to complete a task.
                    Say Give me Some Insights, to get fitbit based insights.
                    Say Stop, to exit this skill'''
                    
    return question(speech_output)\
                .reprompt(prompt)\
                .standard_card(title = card_title, text = card_text)

@ask.launch
def new_game():
    
    card_title = "Morning Routine"
    text = "Welcome to your morning routine. 15 minutes of discipline to let you own the day."
    prompt = "First thing's first, get out of bed!!!"
    
    # FITBIT API
    if('accessToken' in session.user and len(session.user.accessToken)>5):
        print('FITBIT enabled')
    else:
        print('FITBIT Not Enabled')
        
    
    print('ACCESS TOKEN : {}'.format(session.user.accessToken))
    
    # Check if existing user or new user
    r_response = get_user_state(session.user.userId)
    
    # IF 1.) New User or 2.) Existing user with routine index 1
    if( str(r_response)=='Not Found' or str(r_response)=='Error' or r_response==1):
    
        welcome_msg = render_template('welcome')
        
        # If New User, Insert with state 1
        if(str(r_response)!='1'):
            w_response = insert_user_state(session.user.userId, 1)
            welcome_msg = ''' Hey there! You're one step closer to your own success. Let me give you a quick introduction. I will guide you \
                         through your morning routine everyday, and give you motivation along the way. This skill is based on Tim Ferris's\
                         famous morning routine that is followed by a majority of people. If you link your fitbit\
                         device with this skill, I can keep track of how you are doing. After you complete a task, say, next task, to go to the next task. Ask me to play music at any time if you\
                         are still completing the task. If you ever need motivation to do a task, say, motivate me, to let me change your mind. Lastly, say, give\
                         me some insights, to let me help you understand your fitbit achievements for this morning routine. Say Stop, to exit this skill.\
                    '''
        session.attributes[ROUTINE_INDEX] = 0
        
        # Start from the beginning
        
        return question(welcome_msg)\
                    .reprompt(prompt)\
                    .standard_card(title = card_title, text = text)
    # ELSE 3.) Existing user with routine index > 1
    else:
    
        # Existing User
        # Ask whether to resume or start over
        resume_msg = render_template('resume_routine')
        session.attributes[ROUTINE_INDEX] = r_response
        return question(resume_msg)\
                    .reprompt('say continue previous routine to start from where you left off, or, say start a new one. ')\
                    .standard_card(title = 'Resume or Start Over?', text = resume_msg)
        
@ask.intent("StartOverEventIntent")
def start_over():
    #if(ROUTINE_INDEX in session.attributes):
    #    del session.attributes[ROUTINE_INDEX]
    session.attributes[ROUTINE_INDEX] = 1
    return next_routine(INCREMENT_FLAG=False)


@ask.intent("ResumeEventIntent")
def resume_routine():
    return next_routine(INCREMENT_FLAG=False)


@ask.intent("GetNextEventIntent")
def next_routine(INCREMENT_FLAG=True):
    global MAX_ROUTINE_REACHED
    
    print("The INCREMENT_FLAG = {}".format(INCREMENT_FLAG))
    
    if not session.attributes or ROUTINE_INDEX not in session.attributes:
        r_response = get_user_state(session.user.userId)
        
        if( str(r_response)=='Not Found' or str(r_response)=='Error'):
            session.attributes[ROUTINE_INDEX] = 1
        else:
            if(INCREMENT_FLAG is None or INCREMENT_FLAG):
                session.attributes[ROUTINE_INDEX] = (r_response+1)
            else:
                session.attributes[ROUTINE_INDEX] = r_response
    
    else:
        if(INCREMENT_FLAG is None or INCREMENT_FLAG):
            session.attributes[ROUTINE_INDEX] += 1
    routine_index = session.attributes.get(ROUTINE_INDEX)
    routine_text = render_template('routine_{}'.format(routine_index))
    card_title = routine_cards[routine_index]['title']
    card_text =  routine_cards[routine_index]['text']
    
    # Update routine state in dynamodb
    # Resetting for next time
    if(routine_index==MAX_ROUTINE):
        MAX_ROUTINE_REACHED = True
        routine_index=1
    
    if('user' in session and 'userId' in session.user):
        w_response = update_user_state(session.user.userId, routine_index)
    else:
        print('CCOCOCOOCOCOCOCOCOCOCOOCOCO')
        print(context)
        w_response = update_user_state(context.System.user.userId, routine_index)
        
    print('Update - user \nwith routine {}'.format(routine_index))
    
    
    
    if routine_index == 2:
        # create a client object with your app credentials
        client = soundcloud.Client(client_id='803c9b912c2633e3b8bc388e98277b83')

        # fetch track to stream
        track = client.get('/tracks/247140951')

        # get the tracks streaming URL
        stream_url = client.get(track.stream_url, allow_redirects=False)

        # print the tracks stream URL
        #print(stream_url.location)

        #session.attributes['audio_url'] = stream_url.location
        
        return audio(routine_text).play(stream_url.location)
        #return question('meditation happens now')\
        #            .reprompt("are you done yet?")\
        #            .standard_card(title = card_title, text = card_text)
                    
    if routine_index == 3:
        return ExerciseHandler()

    if(MAX_ROUTINE_REACHED):
        print('MAX ROUTINE REACHED : {}'.format(MAX_ROUTINE_REACHED))
        if('accessToken' not in session.user):
            routine_text += ' Link this skill with your Fitbit device, to get insights on how youre doing.'
        return statement(routine_text)\
                        .standard_card(title = card_title, text = card_text)
    else:
        return question(routine_text)\
                    .reprompt("If you are not done yet, just ask me to play some music.")\
                    .standard_card(title = card_title, text = card_text)

                    
@ask.intent('ExerciseEventIntent')
def ExerciseHandler():
    global exercise_start_time, exercise_end_time, exercise_date, exercise_insight
    MAX_EXERCISE_LEVELS = 5
    exercise_list = [
        {
            "title": "Jumping Jacks",
            "text": "Stand tall with your feet together and your hands at your sides.\
                    Quickly raise your arms above your head while jumping your feet out\
                    to the sides. Immediately reverse the movement to jump back to the \
                    standing position. "
        },
        {
            "title": "Squats",
            "text": "Keep your back straight, with your neutral spine, and your chest and \
                    shoulders up. Keep looking straight ahead at that spot on the wall. As \
                    you squat down, focus on keeping your knees in line with your feet. Many\
                    new lifters need to focus on pushing their knees out so they track with\
                    their feet. "
        },
        {
            "title": "High Knees",
            "text": "Stand up straight and place your feet about hip-width apart. Place your\
                    hands palms down facing the floor, hovering just above your belly button. Quickly \
                    drive your right knee up to meet your right hand, bring the same leg back to the\
                    ground immediately bring the left knee coming up to meet your left hand. "
        },
        {
            "title": "Lunge and Knee",
            "text": "Keep your upper body straight, with your shoulders back and relaxed and chin up.\
                    Step forward with one leg, lowering your hips until both knees are bent at about\
                    a 90 degree angle. "
        },
        {
            "title": "Push Up",
            "text": "Begin on your hands and knees with your hands underneath your shoulders \
                    but slightly wider than your shoulders and then come into a plank position.\
                    Begin to bend your elbows, lowering your body towards the floor, and bring\
                    yourself back up. "
        }       
    ]
    
    three_second = "We will start in 3 seconds. <break time='0.5s' /> 3 <break time='1s' /> 2 <break time='1s' /> 1 <break time='1s' /> "
    
    if 'exercise_level' not in session.attributes:
        start_text = render_template('routine_3')
        start_text += " We will be doing 5 exercises in around 5 to 7 minutes. Each exercise\
                        will be done in the first 35 seconds followed by 25 seconds rest. "
        session.attributes['exercise_level'] = 1
        
        # IF FITBIT IS ENABLED
        if('accessToken' in session.user):
            # Get the previous Times and get fitbit api response
            r_resp = get_exercise_times(session.user.userId)

            print('GOT EXERCISE TIMES : {}'.format(r_resp))
            
            if(r_resp!='Not Found' and r_resp!='Error'):
                exercise_date = r_resp.split(',')[0].split(' ')[0]
                exercise_start_time = r_resp.split(',')[0].split(' ')[1]
                exercise_end_time = r_resp.split(',')[1].split(' ')[1]
                if(session.user.accessToken):
                    exercise_insight = get_calories_from_exercise(exercise_date, exercise_start_time, exercise_end_time, session.user.accessToken)
            
            print('EXERCISE INSIGHT : {}'.format(exercise_insight))
            
            
            # Store the time zone
            timezone = get_fitbit_timezone(session.user.accessToken)
            session.attributes['timezone'] = timezone
            
            print('TIMEZONE : {}'.format(timezone))
            tz = pytz.timezone(timezone)
            ct = datetime.now(tz=tz).strftime("%Y-%m-%d %H:%M")
            w_resp = update_user_exercise_start(session.user.userId, ct)
    else:
        start_text = ''
        exercise_insight = ''
        session.attributes['exercise_level'] += 1
    
    if(session.attributes['exercise_level'] == MAX_EXERCISE_LEVELS): 
        if('accessToken' in session.user):
            tz = pytz.timezone(session.attributes['timezone'])
            ct = datetime.now(tz=tz).strftime("%Y-%m-%d %H:%M")
            w_resp = update_user_exercise_end(session.user.userId, ct)
        next_exercise = " Awesome. You are all done with the exercise. To go to the next task, say mission accomplished! "
    elif(session.attributes['exercise_level'] < MAX_EXERCISE_LEVELS):
        next_exercise = " To start the next exercise, say next exercise."
    else:
        if(session.attributes[ROUTINE_INDEX]==3):
            return question("You are already done with your exercise. Say next task to continue.")\
                    .reprompt("Say next task to continue.")\
                    .standard_card(text = 'You are already done with your exercise.', title = 'Say Next task to continue!')
        else:
            return question("You are already done with your exercise. Say resume task to continue.")\
                        .reprompt("Say resume task to continue.")\
                        .standard_card(text = 'You are already done with your exercise.', title = 'Say Resume task to continue!')
    
    exercise_title = exercise_list[session.attributes['exercise_level']-1]['title']
    exercise_text = exercise_list[session.attributes['exercise_level']-1]['text']
    
    timer = " <audio src=\"https://s3.amazonaws.com/alexa-workout-sounds/Tick_Tock_35.mp3\" /> "
    whistle = " <audio src=\"https://s3.amazonaws.com/alexa-workout-sounds/police-whistle-daniel_simon.mp3\" /> "

    speech_output = "<speak>{}</speak>".format(
                                                start_text +
                                                exercise_insight +
                                                ' The Next Exercise is ' +
                                                exercise_title + '. ' +
                                                three_second +
                                                timer +
                                                whistle +
                                                ' Rest for 25 seconds. ' +
                                                " <break time='10s' /> <break time='10s' /> <break time='5s' /> " +
                                                next_exercise
                                               )
    print(speech_output)
    return question(speech_output)\
                .reprompt(next_exercise)\
                .standard_card( text = exercise_text, title = exercise_title)

                
@ask.intent("InsightsEventIntent")
def InsightsHandler():
    global exercise_insight
    
    if('accessToken' not in session.user):
        exercise_insight = 'Link your fitbit device with this skill on your alexa app to start getting insights.'
        return link_question(exercise_insight)
    else:
        # Get the previous Times and get fitbit api response
        r_resp = get_exercise_times(session.user.userId)
        print('GOT EXERCISE TIMES : {}'.format(r_resp))
        
        if(r_resp!='Not Found' and r_resp!='Error'):
            exercise_date = r_resp.split(',')[0].split(' ')[0]
            exercise_start_time = r_resp.split(',')[0].split(' ')[1]
            exercise_end_time = r_resp.split(',')[1].split(' ')[1]
            exercise_insight = get_calories_from_exercise(exercise_date, exercise_start_time, exercise_end_time, session.user.accessToken)
        else:
            exercise_insight = ' Complete at least 1 morning routine for insights. '
    
    print('EXERCISE INSIGHT : {}'.format(exercise_insight))
    return question(exercise_insight)\
                        .reprompt("Say resume task to continue.")\
                        .standard_card(text = exercise_insight, title = 'Your Fitbit Insights!')
    

@ask.intent("BenefitsEventIntent")
def BenefitsHandler():
    motivation = choice(motivation_list).copy()
    r_response = get_user_state(session.user.userId)
    print("GET USER STATE RESPONSE : {}".format(r_response))
    # Respond according to the routine stage user is at!
    if(type(r_response)==int):
        motivation = motivation_list[r_response-1].copy()
    
    motivation['text'] += " If you need any more motivation along the way, let me know. To resume your task, say continue. "
    
    return question(motivation['text'])\
                .reprompt("To continue, just say continue or resume task.")\
                .standard_card(title = motivation['title'], text = motivation['text'])


@ask.intent("PlayMusicEventIntent")
def play_music():
    url = choice(songs_list)
    speech_text = '''<speak> Here you go, <audio src="{}" /> <break time="1.5s"/> If you're not done yet,\
                    say, keep it going, otherwise just say continue. </speak>'''.format(url)
    return question(speech_text)\
                .reprompt("If you're not done yet, just say, keep playing the music, otherwise, just say continue. ")\
                .standard_card(title = 'Playing some morning music', text = 'Enjoy the music while completing your routine!')



@ask.on_playback_finished()
def stream_finished(token):
    _infodump('Playback has finished for stream with token {}'.format(token))
    update_user_state(context.System.user.userId, 3)

@ask.on_playback_started()
def started(offset, token):
    _infodump('STARTED Audio Stream at {} ms'.format(offset))
    _infodump('Stream holds the token {}'.format(token))
    _infodump('STARTED Audio stream from {}'.format(current_stream.url))

@ask.on_playback_stopped()
def stopped(offset, token):
    _infodump('STOPPED Audio Stream at {} ms'.format(offset))
    _infodump('Stream holds the token {}'.format(token))
    _infodump('Stream stopped playing from {}'.format(current_stream.url))
 
@ask.intent('AMAZON.PauseIntent')
def pause():
    return audio('I paused your meditation track.').stop()

@ask.intent('AMAZON.ResumeIntent')
def resume():
    return audio('Resuming your meditation track.').resume()

@ask.intent('AMAZON.StopIntent')
def stop():
    goodbye = render_template('good_bye')
    return audio(goodbye).clear_queue(stop=True)

@ask.intent('AMAZON.NextIntent')
def next():
    #update_user_state(context.System.user.userId, 3)
    session.attributes[ROUTINE_INDEX] = 2
    return next_routine()
    
@ask.intent('AMAZON.PreviousIntent')
def previous():
    return audio('You cannot go back at this stage. Lets continue with the meditation.').resume()
    
@ask.intent('AMAZON.ShuffleOffIntent')
def shuffleoff():
    return audio('There is only one meditation track. Lets continue with the meditation. ').resume()
    
@ask.intent('AMAZON.ShuffleOnIntent')
def shuffleon():
    return audio('There is only one meditation track. Lets continue with the meditation. ').resume()
    
@ask.intent('AMAZON.StartOverIntent')
def startover():
    session.attributes[ROUTINE_INDEX] = 2
    return resume_routine()

@ask.intent('AMAZON.CancelIntent')
def cancel():
    goodbye = render_template('good_bye')
    return audio(goodbye).clear_queue(stop=True)
    
@ask.intent('AMAZON.LoopOffIntent')
def loopoff():
    return audio('').resume()
    
@ask.intent('AMAZON.RepeatIntent')
def repeat():
    return audio('Lets continue with our meditation.').resume()
    
@ask.intent('AMAZON.LoopOnIntent')
def loopon():
    return audio('').resume()

@ask.session_ended
def session_ended():
    return "{}", 200

def _infodump(obj, indent=2):
    #print('INTENT : '+request.intent.name)
    #msg = json.dumps(obj, indent=indent)
    #logger.info(msg)
    logger.info('\n---------------------------------------------\n')

if __name__ == '__main__':
    app.run(debug=True)
