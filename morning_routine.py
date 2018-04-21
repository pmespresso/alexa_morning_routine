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
                and it will encourage you to do another task, and, another and, another."
    },
    {
        "title": "Meditate to solve your challenges!",
        "text": "regular meditation gives you time to practice control of your emotions,\
                which then influences how you react to challenges throughout the day."
    },
    {
        "title": "Health is more important than you think!",
        "text": "getting into your body and exercising even for 30 seconds a day, has a \
                dramatic effect on your your mood and quiets mental chatter."
    },
    {
        "title": "Shower to lose fat?",
        "text": "a quick 5 to 20 minutes cold shower focusing on the back area helps\
                the body to engage in some amount of fat burning"
    },
    {
        "title": "The Metabolism Boost!",
        "text": "drinking some light tea in the morning will get your metabolism fired up!"
    }
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
    return next_routine()


@ask.intent("GetNextEventIntent")
def next_routine():
    global MAX_ROUTINE_REACHED
    if not session.attributes:
        session.attributes[ROUTINE_INDEX] = 1
    else:
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

    if(MAX_ROUTINE_REACHED):
        return statement(routine_text)\
                        .standard_card(title = card_title, text = card_text)
    else:
        return question(routine_text)\
                    .reprompt("are you done yet?")\
                    .standard_card(title = card_title, text = card_text)

                    
@ask.intent("BenefitsEventIntent")
def benefits_handler():
    motivation = choice(motivation_list)
    r_response = get_user_state(session.user.userId)
    print("GET USER STATE RESPONSE : {}".format(r_response))
    # Respond according to the routine stage user is at!
    if(type(r_response)==int):
        motivation = motivation_list[r_response-1]
    
    motivation['text'] += " Now come on, go ahead and finish your routine. If you need any motivation along the way, let me know."
    
    return question(motivation['text'])\
                .reprompt("To continue, just say next routine.")\
                .standard_card(title = motivation['title'], text = motivation['text'])

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
