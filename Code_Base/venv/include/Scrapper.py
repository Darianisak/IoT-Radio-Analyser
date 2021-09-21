import json
import requests
import time


# https://www.delftstack.com/howto/python/python-get-json-from-url/
# https://www.programiz.com/python-programming/json

#   main performs analysis of The RockFM's web API to determine whether songs
#   have been heard played on air already for a given time period.
#
#   @param URL is the URL to pull a JSON file from
#   @param cycleCount is how many cycles the program should run for. A cycle
#       is a timer period of 2 minutes for example.
#   @param cooldown is how long the program should wait to grab the JSON again
#       if the song has not changed since the last JSON read.
def main(url, cycle_count, cool_down):
    #   Defines a Dictionary of Artist:Song[] pairings
    Artist_Songs = {}

    #   Defines a quick look up variable for the most recent song
    prev_song = ""

    #   Run the primary loop until the cycleCount is exceeded.
    while True:

        print("looped")

        #   Pull JSON file from webAPI and convert it to usable data.
        primitive = requests.get(url)
        processed = primitive.text
        currentJSON = json.loads(processed)

        #   Checks that the playingNow song of this JSON pull is different
        #   to the last one.
        if prev_song != currentJSON['nowPlaying'][0].get('name'):

            #   Calculate wait period
            convert_time(currentJSON['nowPlaying'][0].get('played_time'))

            #   Pull the current song name from the JSON
            song_name = currentJSON['nowPlaying'][0].get('name')
            #   Update the previous song value
            prev_song = song_name

            #   Pull the current artist name from JSON
            artist_name = currentJSON['nowPlaying'][0].get('artist')

            #   Pull the length of the song
            song_length = currentJSON['nowPlaying'][0].get('length_in_secs')

            #   Check if the band is present in the dictionary
            if artist_name not in Artist_Songs:

                #   Create a mapping for this band and add the current song to it.
                Artist_Songs[artist_name] = [song_name]

            elif song_name not in Artist_Songs.get(artist_name):

                #   Add the song to the already existent artist key mapping.
                Artist_Songs[artist_name] = Artist_Songs.get(artist_name).append(song_name)
            else:

                #   The song has already been played during the current runtime.
                print("Money")

            #   Decrement the cycle count
            cycle_count -= cycle_count
        else:

            #   If the time out period has expired and the song has not changed,
            #   an ad break could be happening, so wait a period of time before
            #   grabbing the JSON again.
            time.sleep(cool_down)

    #   The program has reached the allotted amount of cycles, so return and exit.
    return Artist_Songs


#   convertToSeconds is used to covert the 24 hour time format found in the
#   grabbed JSON files to seconds.
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


try:
    #   Calls the main method with args.
    print(str(main("https://radio-api.mediaworks.nz/radio-api/v3/station/therock/hawkesbay/web", 10, 80)))
    exit(0)
except KeyboardInterrupt:
    #   Handles runtime cancellation gracefully.
    print("Script was exited via KeyboardInterrupt.")
    exit(1)
