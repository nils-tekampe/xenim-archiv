import urllib, json
from urllib import urlopen
# from urllib import Request
import sys, codecs
import os.path
import pickle
from subprocess import call


recordings = {}
dirname='./'
filename=''
last_modified=''

# if os.path.isfile('recordings.txt'):
#     with open('recordings.txt', 'rb') as handle:
#       recordings = pickle.loads(handle.read())

# url = "http://feeds.streams.xenim.de/api/v1/episode/?list_endpoint"
json_url_epsiodes = "http://feeds.streams.demo.xenim.de/api/v1/episode/?list_endpoint"
# json_url_epsiodes = "http://tekampe.org"
# conn = urllib.Request.urlopen(json_url_epsiodes, timeout=30)
# # last_modified = conn.info().getdate('last-modified')
# print conn.headers['last-modified']

response = urllib.urlopen(json_url_epsiodes)
# print response.headers['last-modified']
print response.info().getdate('last-modified')

data = json.loads(response.read().decode("utf-8-sig"))

utf8_writer = codecs.getwriter('UTF-8')
sys.stdout = utf8_writer(sys.stdout, errors='replace')

for objects in data['objects']:
    if objects['status'] =='RUNNING':
        episode_title=objects['title']
        episode_id=objects['id']
        episode_podcast=objects['podcast']

        for url in objects['streams']:
            epsidode_streaming_url=url['url']
            epsidode_streaming_codec=url['codec']
            # print epsidode_streaming_url
        json_podcast_url='http://feeds.streams.demo.xenim.de' + episode_podcast

# Only proceed if this recording is not yet running.
if not (episode_id in recordings):
    recordings[episode_id]=episode_id

    # Looking up the podcast data that belongs to the episode
    response_podcast = urllib.urlopen(json_podcast_url)
    data_podcast = json.loads(response_podcast.read().decode("utf-8-sig"))

    podcast_name = data_podcast['name']


    # Building the local filename and the command for streaming

    filename=podcast_name + '_' + episode_title + '_' + episode_id
    command= 'streamripper '+ epsidode_streaming_url  + ' -d '+ dirname +' -a ' + filename + '.'+epsidode_streaming_codec+ ' -m 600 > /dev/null 2>&1'
    print command
    call(command)
    # call ('streamripper')
#Saving the recordings dictionary
with open('recordings.txt', 'wb') as handle:
  pickle.dump(recordings, handle)
#
#   try:
#     retcode = call("mycmd" + " myarg", shell=True)
#     if retcode < 0:
#         print >>sys.stderr, "Child was terminated by signal", -retcode
#     else:
#         print >>sys.stderr, "Child returned", retcode
# except OSError as e:
#     print >>sys.stderr, "Execution failed:", e
