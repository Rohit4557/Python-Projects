from gtts import gTTS
import os

class Shoutout:
    def __init__(self,oldpro):
        '''input the name and name of the project of the teacher'''
        self.name=[]
        self.oldpro=oldpro
    def addmyname(self,nameu,project):
        '''takes name and user's project'''
        if(project==self.oldpro):
            self.name.append(nameu)
    def shoutout(self,password):
        if password==2345:
            if self.name:
                message=""
                for nm in self.name:
                    message+=f"shoutout to {nm}. "
                tts = gTTS(text=message, lang='en')
                tts.save("shoutout.mp3")
                os.system("start shoutout.mp3") 

c1=Shoutout("repel")
c1.addmyname("rohit","repel")
c1.addmyname("rajan","repel")
c1.shoutout(2345)



