def build_speechlet_response_ssml(title, output, reprompt_text, should_end_session, card_type='Simple'):
    
    # For Display
    #https://developer.amazon.com/docs/custom-skills/display-interface-reference.html#listtemplate2
    
    
    return {
        'outputSpeech': {
            'type': 'SSML',
            'ssml': "<speak>"+output+"</speak>"
        },
        'card': {
            'type': card_type,
            'title': title,
            'content': ''
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }

def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }