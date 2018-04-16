import logging

from random import randint

from flask import Flask, render_template

from flask_ask import Ask, statement, question, session, audio

import soundcloud

app = Flask(__name__)

ask = Ask(app, "/")

logging.getLogger("flask_ask").setLevel(logging.DEBUG)

ROUTINE_INDEX = "index"

@ask.launch
def new_game():
    welcome_msg = render_template('welcome')
    return question(welcome_msg)

@ask.intent("GetNextEventIntent")
def next_routine():
    if not session.attributes:
        print("hello from this side -> " + str(session.attributes))
        session.attributes[ROUTINE_INDEX] = 1
    else:
        print("hello from the other side -> " + str(session.attributes))
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

    are_you_done = render_template('are_you_done')
    return question(routine_text).reprompt(are_you_done)


@ask.intent('AMAZON.PauseIntent')
def pause():
    return audio('Paused the stream.').stop()

@ask.intent('AMAZON.ResumeIntent')
def resume():
    return audio('Resuming.').resume()

@ask.session_ended
def session_ended():
    return "{}", 200

if __name__ == '__main__':
    app.run(debug=True)
