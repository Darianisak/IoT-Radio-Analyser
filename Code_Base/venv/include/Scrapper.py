import json, requests

# https://www.delftstack.com/howto/python/python-get-json-from-url/
# https://www.programiz.com/python-programming/json

#   Test loading from a web page
#   Get the json website via an http request
url = requests.get("https://radio-api.mediaworks.nz/radio-api/v3/station/therock/hawkesbay/web")
#   Get the text content of the url
text = url.text
print(text)
#   Convert the url text to json file
webJson = json.loads(text)
print(webJson['nowPlaying'])


#   Test of loading a json from a local file
with open('/Users/darianculver/Desktop/rock_test.json') as jsonFile:
    data = json.load(jsonFile)

#   test output
print(len(data))
print(data['nowPlaying'])