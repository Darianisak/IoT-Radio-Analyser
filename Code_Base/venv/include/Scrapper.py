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
def main(URL, cycleCount, cooldown):

    #   Defines a Dictionary of Artist:Song[] pairings
    Artist_Songs = {}

    #   Defines a quick look up variable for the most recent song
    prev_song = ""

    #   Run the primary loop until the cycleCount is exceeded.
    while cycleCount > 0:

        #   Pull JSON file from webAPI and convert it to usable data.
        primitive = requests.get(URL)
        processed = primitive.text
        currentJSON = json.loads(processed)

        #   Checks that the playingNow song of this JSON pull is different
        #   to the last one.
        if prev_song != currentJSON['nowPlaying'][0].get('name'):

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
            cycleCount -= cycleCount
        else:

            #   If the time out period has expired and the song has not changed,
            #   an ad break could be happening, so wait a period of time before
            #   grabbing the JSON again.
            time.sleep(cooldown)
    return Artist_Songs



#   Calls the main method with args.
print(str(main("https://radio-api.mediaworks.nz/radio-api/v3/station/therock/hawkesbay/web", 10, 80)))