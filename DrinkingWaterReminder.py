#Drink Water Reminder

from win11toast import toast
from gtts import gTTS
import os
import time

reminders = 1
message = "Rohit Bhaiya paani peelo"

tts = gTTS(text=message, lang="en")
tts.save("remind.mp3")

for i in range(reminders):
    toast(message)
    os.system("start remind.mp3")
    time.sleep(3)  # 10-minute gap
os.remove("remind.mp3")
