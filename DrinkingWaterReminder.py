#Drink Water Reminder

#bewlow are the all packanges and modules required for the project
from playsound import playsound #for the soundplay and a good helper in deleting the file later without error
from win11toast import toast #for the notification
from gtts import gTTS #for the google text to speech conversion
import os #for deletion
import time #for time delays btw reminders

reminders = 2
message = "Please Developer DRink THe WAter"

tts = gTTS(text=message, lang="en")
tts.save("remind.mp3")

for i in range(reminders):
    toast(message)
    playsound("remind.mp3")
    time.sleep(3)  # time gap in seconds
os.remove("remind.mp3")
