import requests
import time
from bs4 import BeautifulSoup
import os
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="/home/pi/Projektit/Saappitutka/data.json"
from google.cloud import texttospeech
import pygame

#Turns message text into sound
def speak_text(message):
    client = texttospeech.TextToSpeechClient()
    synthesis_input = texttospeech.types.SynthesisInput(text=message)
    voice = texttospeech.types.VoiceSelectionParams(
        language_code='fi-FI',
        ssml_gender=texttospeech.enums.SsmlVoiceGender.MALE)
    # Select the type of audio file you want returned
    audio_config = texttospeech.types.AudioConfig(
        audio_encoding=texttospeech.enums.AudioEncoding.MP3)
    response = client.synthesize_speech(synthesis_input, voice, audio_config)
    with open('output.mp3', 'wb') as out:
        out.write(response.audio_content)
        print('Audio content written to file "output.mp3"')

#Saves car name to file so it knows that car has already been checked
def save_id_to_file(id):
    try:
        with open("file.txt", "a") as f:
            f.write(str(id) +"\n")
    except (FileNotFoundError):
        with open("file.txt", "w") as f:
            f.write(str(id) +"\n")
      
#Checks if car has already been found by this bot
def car_exists(id):
    try:
        with open('file.txt') as f:
            for line in f: 
                if id in line:
                    return True
            else:
                return False
    except (FileNotFoundError):
        with open("file.txt", "w") as f:
            f.write(str(id) +"\n")
            
#Get all the necessary data from the car
def get_car_info(id):
        website='https://www.nettiauto.com/{0}'.format(id)    
        response = requests.get(website)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        #Scrapes power of the car
        power=""
        for power1 in soup.find_all('div', attrs={'class': 'acc_det'}):
            for power2 in power1.find_all('div'):
                for power3 in power2.find_all('b'):
                    power4 = power3.string
                    if "Hv" in power4:
                        power5 = power4.split()
                        power = power5[0]
        
        #Scrapes the location
        for location1 in soup.findAll("div", {"class": "fl ml10"}):
            for location2 in location1.find_all('a'):
                if location2.get('data-city'):
                    location = location2.get('data-city')
                else:
                    pass
            
        #Scrapes the all other data
        cars = soup.findAll("div", {"class": "mid_border br_blr5_border"})
        for maker in cars:
            manufacturer=maker.get('data-make')
            model=maker.get('data-model')
            price=maker.get('data-price')
            year=maker.get('data-year')
            mileage=maker.get('data-mileage')
            car_id=maker.get('data-id')           
            if power == "":
                car_data=(manufacturer + " " + model + " Vuosimallia " + year + "   Hintana " + price +
                          " euroa ja Tehosta ei mitään tietoa   Ajettu " + mileage + " Kilometriä ja sijaitsee paikkakunnalla "
                          + location)
            else:
                car_data=(manufacturer + " " + model + " Vuosimallia " + year + "                   Hintana " + price +
                          " euroa ja Teho " + power + " Kilowattia             Ajettu " + mileage + " Kilometriä ja sijaitsee paikkakunnalla "
                          + location)
            return car_data

def speak_car_data(car_data):
            speak_text(car_data)
            os.system('mpg321 topias_saab.mp3 &')
            time.sleep(6.5)
            os.system('mpg321 output.mp3 &')
            time.sleep(20)

while True:
    time.sleep(1)
    #Range tells how many pages to look use looking
    for x in range(2,0,-1):
        print(x, 'sivu')
        website="https://www.nettiauto.com/saab/vaihtoautot?sortCol=enrolldate&ord=DESC&page={}".format(x)
        response = requests.get(website)
        soup = BeautifulSoup(response.content, 'html.parser')
        cars = soup.select('a')    # Soup object type

        # Go through car makers in website 
        for car in cars:
            maker=str(car.get('data-make'))
            id=str(car.get('data-id'))
            if maker == 'Saab' and car_exists(id) == False:
                save_id_to_file(id)
                car_data=get_car_info(id)
                speak_car_data(car_data)
                print(car_data)
            else:
                pass
