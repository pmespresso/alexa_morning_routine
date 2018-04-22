import logging

from random import randint, choice

from flask import Flask, render_template

from flask_ask import Ask, statement, question, session, audio, current_stream

import soundcloud

import json

from dynamo_functions import get_user_state, insert_user_state

app = Flask(__name__)

ask = Ask(app, "/")

logger = logging.getLogger("flask_ask")
logger.setLevel(logging.DEBUG)

ROUTINE_INDEX = "index"
MAX_ROUTINE = 6
MAX_ROUTINE_REACHED = False

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

@ask.launch
def new_game():
    card_title = "Morning Routine"
    text = "Welcome to your morning routine. 15 minutes of discipline to let you own the day."
    prompt = "First thing's first, get out of bed!!!"

    # Check if existing user or new user
    r_response = get_user_state(session.user.userId)
    if( str(r_response)=='Not Found' or str(r_response)=='Error' or r_response==1):
    
        # New user or Existing user with state 1
        # If New User, Insert with state 1
        if(str(r_response)!='1'):
            w_response = insert_user_state(session.user.userId, 1)
        
        # Start from the beginning
        welcome_msg = render_template('welcome')
        return question(welcome_msg)\
                    .reprompt(prompt)\
                    .standard_card(title = card_title, text = text)
    else:
    
        # Existing User
        # Ask whether to resume or start over
        resume_msg = render_template('resume_routine')
        session.attributes[ROUTINE_INDEX] = r_response
        return question(resume_msg)\
                    .reprompt(resume_msg)\
                    .standard_card(title = 'Resume or Start Over?', text = resume_msg)
        
@ask.intent("StartOverEventIntent")
def start_over():
    if(ROUTINE_INDEX in session.attributes):
        del session.attributes[ROUTINE_INDEX]
    return next_routine()


@ask.intent("ResumeEventIntent")
def resume_routine():
    return next_routine(INCREMENT_FLAG=False)


@ask.intent("GetNextEventIntent")
def next_routine(INCREMENT_FLAG=True):
    global MAX_ROUTINE_REACHED
    
    inc_flag = INCREMENT_FLAG
    print("The INCREMENT_FLAG = {}".format(INCREMENT_FLAG))
    
    if not session.attributes or ROUTINE_INDEX not in session.attributes:
        session.attributes[ROUTINE_INDEX] = 1
    else:
        if(INCREMENT_FLAG is None):
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
    
    w_response = insert_user_state(session.user.userId, routine_index)
    print('Update - user {} \nwith routine {}'.format(session.user.userId, routine_index))
    
    if routine_index == 2:
        # create a client object with your app credentials
        #client = soundcloud.Client(client_id='803c9b912c2633e3b8bc388e98277b83')

        # fetch track to stream
        #track = client.get('/tracks/247140951')

        # get the tracks streaming URL
        #stream_url = client.get(track.stream_url, allow_redirects=False)

        # print the tracks stream URL
        #print(stream_url.location)

        #return audio(routine_text).play(stream_url.location)
        return question('meditation happens now')\
                    .reprompt("are you done yet?")\
                    .standard_card(title = card_title, text = card_text)
                    
    if routine_index == 3:
        return ExerciseHandler()

    if(MAX_ROUTINE_REACHED):
        return statement(routine_text)\
                        .standard_card(title = card_title, text = card_text)
    else:
        return question(routine_text)\
                    .reprompt("If you are not done yet, just ask me to play some music.")\
                    .standard_card(title = card_title, text = card_text)

                    
@ask.intent('ExerciseEventIntent')
def ExerciseHandler():
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
    else:
        start_text = ''
        session.attributes['exercise_level'] += 1
    
    if(session.attributes['exercise_level'] == MAX_EXERCISE_LEVELS):    
        next_exercise = " Awesome. You are all done with the exercise. To go to the next routine, say mission accomplished! "
    elif(session.attributes['exercise_level'] < MAX_EXERCISE_LEVELS):
        next_exercise = " To start the next exercise, say next exercise."
    else:
        return question("You are already done with your exercise. Say resume routine to continue.")\
                    .reprompt("Say resume routine to continue.")\
                    .standard_card(text = 'You are already done with your exercise.', title = 'Say Resume routine to continue!')
    
    exercise_title = exercise_list[session.attributes['exercise_level']-1]['title']
    exercise_text = exercise_list[session.attributes['exercise_level']-1]['text']
    
    timer = " <audio src=\"https://s3.amazonaws.com/alexa-workout-sounds/Tick_Tock_35.mp3\" /> "
    whistle = " <audio src=\"https://s3.amazonaws.com/alexa-workout-sounds/police-whistle-daniel_simon.mp3\" /> "
    
    if(session.attributes['exercise_level'] == MAX_EXERCISE_LEVELS):    
        next_exercise = " Awesome. You are all done with the exercise. To go to the next routine, say mission accomplished! "
    else:
        next_exercise = " To start the next exercise, say next exercise."
    speech_output = "<speak>{}</speak>".format(
                                                start_text +
                                                ' The Next Exercise is ' +
                                                exercise_title + '. ' +
                                                exercise_text +
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

@ask.intent("BenefitsEventIntent")
def BenefitsHandler():
    motivation = choice(motivation_list).copy()
    r_response = get_user_state(session.user.userId)
    print("GET USER STATE RESPONSE : {}".format(r_response))
    # Respond according to the routine stage user is at!
    if(type(r_response)==int):
        motivation = motivation_list[r_response-1].copy()
    
    motivation['text'] += " If you need any more motivation along the way, let me know. To resume your routine, say continue. "
    
    return question(motivation['text'])\
                .reprompt("To continue, just say continue or resume routine.")\
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
    return next_routine()

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

@ask.intent("SkipIntent")
def skip_routine():
    return next_routine()

@ask.intent('AMAZON.PauseIntent')
def pause():
    return audio('Paused the stream.').stop()

@ask.intent('AMAZON.ResumeIntent')
def resume():
    return audio('Resuming.').resume()

@ask.intent('AMAZON.StopIntent')
def stop():
    return audio('stopping').clear_queue(stop=True)

@ask.session_ended
def session_ended():
    return "{}", 200

def _infodump(obj, indent=2):
    msg = json.dumps(obj, indent=indent)
    logger.info(msg)

if __name__ == '__main__':
    app.run(debug=True)
