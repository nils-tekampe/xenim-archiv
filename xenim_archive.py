# This little program checks the JSON API of xenim.de and looks for running streams
# For all running episodes, the name of the corresponding Podcast is acquired and
# the stream is saved to disk.
# This program requires the tool streamripper to be available in the path.
# If you have any questions, please let me know via nils@tekampe.org.

import urllib, json
import sys, codecs
import os.path
import pickle
from subprocess import call, PIPE, Popen
import os

# Helper function to check for the availability of streamripper.
# Thanks to http://stackoverflow.com/questions/377017/test-if-executable-exists-in-python
def which(program):
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None

recordings = {} # All recordings are saved into this dict so that they are only started once
dirname='/Volumes/SDMemory/streams/' # The folder where the recordings should be stored
filename=''

if which('streamripper')==None:
    print 'Could not find streamripper in the path. Please install streamripper and add it to the path. The call this script again. Will exit now.'
    exit (1)

# if os.path.isfile('recordings.txt'):
#     with open('recordings.txt', 'rb') as handle:
#       recordings = pickle.loads(handle.read())

# json_url_epsiodes = "http://feeds.streams.demo.xenim.de/api/v1/episode/?list_endpoint" # The URL to receive all episodes
print "Retreiving list of all episodes."
json_url_epsiodes = "http://feeds.streams.xenim.de/api/v1/episode/?list_endpoint" # The URL to receive all episodes
# Open the URL
response = urllib.urlopen(json_url_epsiodes)
data = json.loads(response.read().decode("utf-8-sig"))

# We need to replace the output function as we have unicode characters
utf8_writer = codecs.getwriter('UTF-8')
sys.stdout = utf8_writer(sys.stdout, errors='replace')

# Parse the answer. Look for running episodes only
print "Filtering for running episodes"
for objects in data['objects']:
    if objects['status'] =='RUNNING':
        episode_title=objects['title']
        episode_id=objects['id']
        episode_podcast=objects['podcast']

        for url in objects['streams']:
            epsidode_streaming_url=url['url']
            epsidode_streaming_codec=url['codec']
        # json_podcast_url='http://feeds.streams.demo.xenim.de' + episode_podcast # This is the URL where the corresponding Podcast information can be found
        json_podcast_url='http://feeds.streams.xenim.de' + episode_podcast # This is the URL where the corresponding Podcast information can be found

# Only proceed if this recording is not yet running.
if not (episode_id in recordings):
    print "Found the following new podcast stream: " + json_podcast_url
    # Adding the recording to the hashtable so that is is only started once
    recordings[episode_id]=episode_id
    #Saving the recordings dictionary so that they will be available for next start
    with open('recordings.txt', 'wb') as handle:
      pickle.dump(recordings, handle)
    # Looking up the podcast data that belongs to the episode
    response_podcast = urllib.urlopen(json_podcast_url)
    data_podcast = json.loads(response_podcast.read().decode("utf-8-sig"))
    podcast_name = data_podcast['name']

    # Building the local filename and the command for ripping
    filename=podcast_name + '_' + episode_title + '_' + episode_id
    command= 'streamripper '+ epsidode_streaming_url  + ' -d '+ dirname +' -a ' + filename + '.'+epsidode_streaming_codec+ ' -A -m 600 > /dev/null 2>&1'
    # command='sleep 100'
    try:

        process = Popen([command], stdout=PIPE, stderr=PIPE) 
        stdout, stderr = process.communicate()

        retcode=call(command,shell=True)
        if retcode==0:
            print "Sucesfully downloaded the podcast. Will now exit."
        else:
            print "streamripper returned with a code other than 0:"
            print retcode
    except:
        print("Unexpected error:", sys.exc_info()[0])
