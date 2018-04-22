# alexa_morning_routine

## 6 Morning Routines to Own the Day

1. Get out of bed within 2 minutes of waking up 
  * We will add accountability here with a hardware component that senses whether or not you've actually left your bed or you just lied to Alexa, by detecting pressure changes on your mattress.
2. Make your bed
3. Meditate --> Plays ambient noise pulled from soundcloud for the duration.
4. Exercise
  * Can add accountability by connecting to Fitbit/Apple Watch/etc. to confirm heart rate change.
5. Jump in a Cold Shower
6. Drink some tea or coffee
  * Can automate this part by connecting to your coffee machine so you exit the shower to the smell of freshly brewed coffee.

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

`pip install boto3`

`python3 morning_routine.py`

(in a separate terminal window/tab)

`path/to/ngrok http 5000`

Copy the forwarding address into the Endpoints tab in the Alexa Dev GUI https://developer.amazon.com/alexa/console/ask/test


