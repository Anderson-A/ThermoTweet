# Tweeting thermometer with DS18B20.
# If temperature goes below 60 degrees F or above 80 degrees F, a tweet will
# be sent to Johns Hopkins University.

# Code must be run from terminal and not from IDLE, or else
# Adafruit_CharLCD will not import.
# Remember to add "dtoverlay=w1-gpio" to the bottom of config.txt on your pi.

# Requires AdafruitChar_LCD library from https://github.com/adafruit/Adafruit_Python_CharLCD

# auth.py file should have your Twitter application keys in it

# By Anderson Adon andersonaadon@gmail.com

# Thermometer tutorial at https://learn.adafruit.com/adafruits-raspberry-pi-lesson-11-ds18b20-temperature-sensing/overview
# RPi tweeting tutorial at https://projects.raspberrypi.org/en/projects/getting-started-with-the-twitter-api
# LCD tutorial at https://pimylifeup.com/raspberry-pi-lcd-16x2/

import os
import glob
import time
import random
from twython import Twython

# Twitter API keys
from auth import (
    consumer_key,
    consumer_secret,
    access_token,
    access_token_secret
    )

twitter = Twython(
    consumer_key,
    consumer_secret,
    access_token,
    access_token_secret
    )

import Adafruit_CharLCD as LCD

# Raspberry Pi LCD pin configuration:
lcd_rs        = 25
lcd_en        = 24
lcd_d4        = 23
lcd_d5        = 17
lcd_d6        = 18
lcd_d7        = 22
lcd_backlight = 4

# Define LCD column and row size for 16x2 LCD.
lcd_columns = 16
lcd_rows    = 2

# Initialize the LCD using the pins above.
lcd = LCD.Adafruit_CharLCD(lcd_rs, lcd_en, lcd_d4, lcd_d5, lcd_d6, lcd_d7,
                           lcd_columns, lcd_rows, lcd_backlight)
lcd.clear()

# Starts interface for termometer
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

# Finds file from which to read temperature
base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'

def read_temp_raw():
    """Fethches two lines of message from the interface"""
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines

def read_temp():
    """Reads lines for errors and then gets temperature, converts to farenheit"""
    lines = read_temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        temp_f = temp_c * 9.0 / 5.0 + 32.0
        return temp_f

cold_messages = [
    "",
    "I'm not paying you $70,000 a year so I can freeze to death! ",
    "My room is colder than the ninth circle of hell. ",
    "Santa moved into my dorm today. ",
    "I guess I can have penguins in my room now. ",
    "Global warming is a Chinese hoax! ",
    "Do I go to Johns Hopkins or The Academy at the North Pole? ",
    "Maybe some premeds can help me treat my frostbite. ",
    ]

hot_messages = [
    "",
    "Satan moved into my dorm room today. ",
    "Who needs a tropical vacation when I have my room in AMR 1? ",
    "Global warming has become localized entirely within my dorm. ",
    "Can't study for my MCAT if my notes melt. ",
    ]

while True:
    temperature = read_temp()
    if temperature > 120.0:
        continue
    print(temperature)
    lcd.clear()
    lcd.message(str(temperature) + ' F')
    if temperature < 60.0:
        message = random.choice(cold_messages) + "My dorm room is currently %.4f degrees. @JohnsHopkins Turn up the heat in AMR 1!" % temperature
        twitter.update_status(status=message)
        print("Tweeted: %s" % message)
        lcd.message('\nTweet Sent')
    elif temperature > 80.0:
        message = random.choice(hot_messages) + "My dorm room is currently %.4f degrees. @JohnsHopkins Put the air conditioners back in AMR 1!" % temperature
        twitter.update_status(status=message)
        print("Tweeted: %s" % message)
        lcd.message('\nTweet Sent')
    time.sleep(900) # Check every fifteen minutes
