import logging

from random import randint

from flask import Flask, render_template

from flask_ask import Ask, statement, question, session, audio, current_stream

import soundcloud

app = Flask(__name__)

ask = Ask(app, "/")

logging.getLogger("flask_ask").setLevel(logging.DEBUG)

ROUTINE_INDEX = "index"

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
        "title": "Jump in a Cold Shower",
        "text": "Make sure to end your shower with at least 30 seconds of super cold water. You'll feel incredible afterwards."
    },
    {
        "title": "Drink some Tea or Coffee",
        "text": "There is no life before coffee"
    },
    {
        "title": "Exercise",
        "text": "Get your blood flowing, and your metabolism revving. GET SOME!"
    }
]

@ask.launch
def new_game():
    card_title = "Morning Routine"
    text = "Welcome to your morning routine. 15 minutes of discipline to let you own the day."
    prompt = "First thing's first, get out of bed!!!"

    welcome_msg = render_template('welcome')

    return question(welcome_msg).reprompt("get up bitch")

@ask.intent("GetNextEventIntent")
def next_routine():
    if not session.attributes:
        session.attributes[ROUTINE_INDEX] = 1
    else:
        session.attributes[ROUTINE_INDEX] += 1
    routine_index = session.attributes.get(ROUTINE_INDEX)
    routine_text = render_template('routine_{}'.format(routine_index))

    if routine_index == 2:
        # create a client object with your app credentials
        client = soundcloud.Client(client_id='803c9b912c2633e3b8bc388e98277b83')

        # fetch track to stream
        track = client.get('/tracks/247140951')

        # get the tracks streaming URL
        stream_url = client.get(track.stream_url, allow_redirects=False)

        # print the tracks stream URL
        print(stream_url.location)

        return audio(routine_text).play(stream_url.location)

    return question(routine_text).reprompt("are you done yet?")

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
