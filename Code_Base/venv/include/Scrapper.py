import json
import requests
import time
import chime
from datetime import datetime


#   https://www.delftstack.com/howto/python/python-get-json-from-url/
#   https://www.programiz.com/python-programming/json
#   https://reposhub.com/python/miscellaneous/MaxHalford-chime.html

#   main performs analysis of The RockFM's web API to determine whether songs
#   have been heard played on air already for a given time period.
#
#   @param url is the URL to pull a JSON file from
#   @param cycle_count is how many cycles the program should run for. A cycle
#       is defined as a unique song played.
#   @param cool_down is how long the program should wait to grab the JSON again
#       if the song has not changed since the last JSON read.
def main(url, cycle_count, cool_down):

    print("Beginning analytics platform...")

    #   Defines a Dictionary of Artist:Song[] pairings
    Artist_Songs = {}

    #   Defines a quick look up variable for the most recent song
    prev_song = ""

    #   Run the primary loop until the cycleCount is exceeded.
    while cycle_count > 0:

        #   Pull JSON file from webAPI and convert it to usable data.
        primitive = requests.get(url)
        processed = primitive.text
        currentJSON = json.loads(processed)

        #   Checks that the playingNow song of this JSON pull is different
        #   to the last one.
        if prev_song != currentJSON['nowPlaying'][0].get('name'):

            #   Calculate wait period. This period is found by getting the
            #   estimated time of song completion and comparing it to the current
            #   system time. Once the program has waited for such a time
            #   period, it will grab the sites JSON and check for a new song.
            start_time = convert_time(currentJSON['nowPlaying'][0].get('played_time'))
            song_duration = currentJSON['nowPlaying'][0].get('length_in_secs')
            system_time = convert_time(datetime.now().strftime("%H:%M:%S"))
            wait_time = (start_time + int(song_duration) + 10) - system_time

            #   Pull the current song name from the JSON
            song_name = currentJSON['nowPlaying'][0].get('name')
            #   Update the previous song value
            prev_song = song_name

            #   Pull the current artist name from JSON
            artist_name = currentJSON['nowPlaying'][0].get('artist')

            #   Check if the band is present in the dictionary
            if artist_name not in Artist_Songs:

                #   Create a mapping for this band and add the current song to it.
                print("New Artist && Song: " + artist_name + ": '" + song_name +
                      "' Start time was " + currentJSON['nowPlaying'][0].get('played_time')
                      + " with the next song expected in " + str(wait_time) +
                        " seconds.")
                Artist_Songs[artist_name] = [song_name]

            elif song_name not in Artist_Songs.get(artist_name):

                #   Add the song to the already existent artist key mapping.
                print("New Song: " + artist_name + " " + song_name +
                      " Start time was " + currentJSON['nowPlaying'][0].get('played_time')
                      + " with the next song expected in " + str(wait_time) +
                      " seconds.")
                Artist_Songs[artist_name] = Artist_Songs.get(artist_name).append(song_name)
            else:

                #   The song has already been played during the current
                #   so cue audio alerts to notify the user.
                chime.success()
                chime.success()
                chime.success()
                chime.success()
                chime.success()
                print("Duplicate song found! " + artist_name + " " + song_name)

            #   Force the system to wait to grab a new JSON until the expected
            #   new song period has been reached.
            try:
                time.sleep(wait_time)
            except ValueError:
                #   It's highly unlikely, but ValueErrors can be thrown if
                #   time.sleep is given a negative value. This could occur
                #   if lag and timing problems cause an old JSON to be delivered
                #   after the system time has already exceeded the estimated
                #   time. This is very unlikely, but it doesn't hurt to handle
                #   it anyway.
                print("Network disconnect has occurred; Flood until restablished.")

            #   As a new song entry was added, decrement the cycle_count value.
            cycle_count = cycle_count - 1
        else:

            #   If the time out period has expired and the song has not changed,
            #   an ad break could be happening, so wait a period of time before
            #   trying to grab the JSON again.
            print("Expected time fell short, waiting a further " + str(cool_down) + " seconds")
            time.sleep(cool_down)

    #   The program has reached the allotted amount of cycles, so return
    #   and exit.
    return Artist_Songs


#   convertToSeconds is used to covert the 24 hour time format found in the
#   grabbed JSON files and sys time to seconds.
#
#   @param fullTime is the 24hr representation of a time, given in the string
#       format: "HH:MM:SS".
#   @return the amount of seconds that fullTime represents.
def convert_time(full_time):
    #   Substrings the hour, minute, and second components out of full_time
    hour_base = full_time[0:2]
    minute_base = full_time[3:5]
    second_base = full_time[6:8]

    #   Converts the retrieved times to integer seconds and returns the total
    hour_seconds = int(hour_base) * 3600
    minute_second = int(minute_base) * 60
    total_time = hour_seconds + minute_second + int(second_base)
    return total_time


#   Post intro message to user
print("Welcome to the MediaWorks radio programming analyser!\nThis script records"
      " each artist and song pairing for a given amount of songs by pulling\n"
      "publicly available JSON files from the specified stations web player.\n")

#   List out station options
print("This application supports all of MediaWorks programming.\nOptions include"
      ", and should be inputted as so: therock, maifm, theedge, georgefm, morefm,"
      "\nthebreeze, thesound, and magic.")
station_name = input("Enter one of the above station names as displayed: ")

#   Allowing the user to interactively decide the region makes it more complicated
#   than it really should be. If a user wishes to change the region, simply
#   change the region_name below: be advised that it must match a region defined
#   by the MediaWorks web player system.
region_name = "hawkesbay"

api_url = "https://radio-api.mediaworks.nz/radio-api/v3/station/" \
          + str(station_name) + "/" + str(region_name) + "/web"

try:
    #   Calls the main method with args.
    print(str(main(api_url, 10, 80)))
    chime.success()
    exit(0)
except KeyboardInterrupt:
    #   Handles runtime cancellation gracefully.
    print("Script was exited via KeyboardInterrupt.")
    chime.success()
    exit(1)
