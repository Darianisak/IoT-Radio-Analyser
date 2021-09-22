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
    global Artist_Songs
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
                #   ValueErrors are thrown in cases where the current system time
                #   exceeds the estimate time of song completion. This can be caused
                #   by a few factors, however, two main reasons are extended add breaks,
                #   and network disconnects.
                print("Extended break or disconnect occurred; "
                      "follow standard wait protocol.")
                time.sleep(cool_down)

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


#   get_name_from_code is used to simplify the code base when determining api
#   urls based on user input.
#
#   @param station_code is a number from 1 to 8 inclusive, which represents
#       a given MediaWorks radio station name, as defined by the api.
#   @return the station_name of a MediaWorks radio station.
def get_name_from_code(station_code):
    if station_code == 1:
        return "therock"
    elif station_code == 2:
        return "maifm"
    elif station_code == 3:
        return "theedge"
    elif station_code == 4:
        return "georgefm"
    elif station_code == 5:
        return "morefm"
    elif station_code == 6:
        return "thebreeze"
    elif station_code == 7:
        return "thesound"
    elif station_code == 8:
        return "magic"
    else:
        #   This branch should never be reached, as it means that the while
        #   verification loop has somehow been bypassed.
        raise RuntimeError("Invalid station code provided with verification step"
                           " ignored.")


#   Post intro message to user.
print("Welcome to the MediaWorks radio programming analyser!\nThis script records"
      " each artist and song pairing for a given amount of songs by pulling\n"
      "publicly available JSON files from the specified stations web player.\n")

#   List out station options.
print("This application supports all of MediaWorks programming.\nOptions "
      "are listed as follows with numbers representing each:"
      "\n1::The Rock, 2::MaiFM, 3::The Edge, 4::GeorgeFM, 5::MoreFM, 6::The Breeze, 7::The Sound, and 8::Magic.")
station_code = int(input("Enter one of the above station names as displayed: "))

#   Verify that the provided station code is valid.
while station_code not in [1, 2, 3, 4, 5, 6, 7, 8]:
    station_code = int(input("Sorry, but the provided station code was invalid. Please resubmit: "))

#   Grab the station name from the user supplied station code.
station_name = get_name_from_code(station_code)

#   Allowing the user to interactively decide the region makes it more complicated
#   than it really should be. If a user wishes to change the region, simply
#   change the region_name below: be advised that it must match a region defined
#   by the MediaWorks web player system. So far as I can tell, changing regions
#   would only effect the adds played, which isn't something that this script
#   cares about.
region_name = "hawkesbay"

#   Takes the user input and generates an api link accordingly.
api_url = "https://radio-api.mediaworks.nz/radio-api/v3/station/" \
          + str(station_name) + "/" + str(region_name) + "/web"

#   Artist_Songs is defined in a global context not for cases where the program
#   terminates properly, but when a Keyboard interrupt occurs, for example.
global Artist_Songs;

#   Try:Except boiler plate code used to handle cases where operation is paused
#   during runtime. This isn't handled prior to this point because there is no
#   meaningful information present.
try:
    #   Calls the main method with args.
    print(str(main(api_url, 10, 80)))
    chime.success()
    exit(0)
except KeyboardInterrupt:
    #   Handles runtime cancellation gracefully.
    print("Script was exited via KeyboardInterrupt. "
          "Printing most recent recording status...")
    print(str(Artist_Songs))
    chime.success()
    exit(1)
