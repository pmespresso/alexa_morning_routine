# alexa_morning_routine

## 6 Morning Routines to Own the Day

1. Get out of bed within 2 minutes of waking up
2. Make your bed
3. Meditate --> Plays ambient noise pulled from soundcloud for the duration.
4. Jump in a Cold Shower
5. Drink some tea or coffee
6. Exercise

## Sample Skill Usage

* "Alexa, start my morning routine"

** "Okay, get out of bed. You have 2 minutes. 

* "Mission Accomplished"

** "Okay, now make your bed, you have 1 minute."

* "Mission Accomplished"

** "Okay, now time to meditate for 5 minutes." { Plays Ambient Noise }


## How to Run Locally

`git clone`

`source path/to/virtualenvs/alexa_morning_routine_env/bin/activate`

`pip install flask-ask`

`pip install soundcloud`

`python3 morning_routine.py`

(in a separate terminal window/tab)

`path/to/ngrok http 5000`

Copy the forwarding address into the Endpoints tab in the Alexa Dev GUI https://developer.amazon.com/alexa/console/ask/test


