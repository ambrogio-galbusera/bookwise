from sense_hat import SenseHat
from openai import OpenAI
from time import sleep
import pychromecast
import os
import base64
import requests


sense = SenseHat()

# OpenAI API Key
api_key = "sk-hf12xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

# This board's IP address or hostname
this_server="192.168.1.104"

# Chromecast device friendly name
cc_device="Garage speaker"


# Path to your image
image_path = "/tmp/image.jpg"

# colors
r = (255, 0, 0)
p = (204, 0, 204)
o = (255, 128, 0)
y = (255, 255, 0)
g = (0, 255, 0)
a = (0, 255, 255)
b = (0, 0, 255)
pr = (128, 0, 255)
e = (0, 0, 0)

red_heart = [
e, e, e, e, e, e, e, e,
e, r, r, e, r, r, e, e,
r, r, r, r, r, r, r, e,
r, r, r, r, r, r, r, e,
r, r, r, r, r, r, r, e,
e, r, r, r, r, r, e, e,
e, e, r, r, r, e, e, e,
e, e, e, r, e, e, e, e
]

pink_heart = [
e, e, e, e, e, e, e, e,
e, p, p, e, p, p, e, e,
p, p, p, p, p, p, p, e,
p, p, p, p, p, p, p, e,
p, p, p, p, p, p, p, e,
e, p, p, p, p, p, e, e,
e, e, p, p, p, e, e, e,
e, e, e, p, e, e, e, e
]

orange_heart = [
e, e, e, e, e, e, e, e,
e, o, o, e, o, o, e, e,
o, o, o, o, o, o, o, e,
o, o, o, o, o, o, o, e,
o, o, o, o, o, o, o, e,
e, o, o, o, o, o, e, e,
e, e, o, o, o, e, e, e,
e, e, e, o, e, e, e, e
]

# Function to encode the image
def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')

def getAbstract():

    # Getting the base64 string
    base64_image = encode_image(image_path)

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    payload = {
        "model": "gpt-4-vision-preview",
        "messages": [
          {
            "role": "user",
            "content": [
              {
                "type": "text",
                "text": "Make an abstract of the text you can read in this image. Do not complain about image quality"
              },
              {
                "type": "image_url",
                "image_url": {
                  "url": f"data:image/jpeg;base64,{base64_image}"
                }
              }
            ]
          }
        ],
        "max_tokens": 300
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    return response

def saveAudio(response):
    client = OpenAI(api_key=api_key)
    audio = client.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=response
    )

    audio.stream_to_file("/home/admin/bookwise/speech.mp3")

def playAudio(file):
    chromecasts, browser = pychromecast.get_listed_chromecasts(friendly_names=[cc_device])
    print(chromecasts)
    cast = chromecasts[0]
    cast.wait()
    mc = cast.media_controller
    mc.play_media("http://"+this_server+":9000/"+file, content_type = "audio/mp3")

def showLove():
    heart_colors = [red_heart, pink_heart, orange_heart]
    for color in heart_colors:

        sense.set_pixels(color)
        sleep(1)

    # Clear the LED display
    sense.clear()

def bookDetected():
    # all pixels on
    sense.clear(255,255,255)

    playAudio("processing.mp3")

    # take picture
    print("Taking picture")
    sleep(5)
    os.system("libcamera-still -t 1000 --qt-preview --vflip=1 --hflip=1 --autofocus-on-capture=1 -o /tmp/image.jpg")

    # some show...
    sense.set_pixels(red_heart)

    # invoke chatgpt
    print("Loading page abstract")
    response = getAbstract()
    print(response.json())

    # some show...
    sense.set_pixels(pink_heart)

    abstract = response.json()['choices'][0]['message']['content']
    print("TTS on {}".format(abstract))
    saveAudio(abstract)

    playAudio("done.mp3")
    showLove()

    sense.clear(0,0,0)
    print("DONE")

def bookRemoved():
    playAudio("speech.mp3")
    showLove()

sense.clear(0,0,0)
waitForReleased = False

#saveAudio("Hello. Let me read the last page")
#os.system("cp speech.mp3 processing.mp3")
#saveAudio("Welcome to Bookwise")
#os.system("cp speech.mp3 welcome.mp3")
#saveAudio("Done. See you soon!")
#os.system("cp speech.mp3 done.mp3")

playAudio("welcome.mp3")
#playAudio("processing.mp3")
#bookDetected()

while True:
    print("Waiting for event {}".format(waitForReleased))
    event = sense.stick.wait_for_event()
    print("Event {} {}".format(event.direction, event.action))

    if (event.direction == "middle"):
        if (event.action == "pressed") and not waitForReleased:
            print("Book detected")
            bookDetected()
            sense.stick.get_events()
            waitForReleased = True
        elif (event.action == "released") and waitForReleased:
            print("Book removed")
            bookRemoved()
            waitForReleased = False

    sleep(0.1)


