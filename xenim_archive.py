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

def record ( _url, _podcast_name, _episode_title,_episode_id):
    dirname='/Volumes/SDMemory/streams/' # The folder where the recordings should be stored
    recordings = {} # All recordings are saved into this dict so that they are only started once
    # if os.path.isfile('recordings.txt'):
    #     with open('recordings.txt', 'rb') as handle:
    #       recordings = pickle.loads(handle.read())

    # Only proceed if this recording is not yet running.
    if not (_episode_id in recordings):
        print "Found the following new podcast stream: " + _url
        # Adding the recording to the hashtable so that is is only started once
        recordings[_episode_id]=_url
        #Saving the recordings dictionary so that they will be available for next start
        with open('recordings.txt', 'wb') as handle:
          pickle.dump(recordings, handle)
        # Building the local filename and the command for ripping
        filename=_podcast_name + '_' + _episode_title
        command= 'streamripper '+ _url  + ' -d '+ dirname +' -a ' + filename + '.'+epsidode_streaming_codec+ ' -A -m 600 > /dev/null 2>&1'
        # command='sleep 100'
        # try:

        process = Popen([command], stdout=PIPE, stderr=PIPE, shell=True)
        stdout, stderr = process.communicate()

            # retcode=call(command,shell=True)
        #     if retcode==0:
        #         print "Sucesfully downloaded the podcast. Will now exit."
        #     else:
        #         print "streamripper returned with a code other than 0:"
        #         print retcode
        # except:
        #     print("Unexpected error:", sys.exc_info()[0])


###########################
#Main function starts here#
###########################

if which('streamripper')==None:
    print 'Could not find streamripper in the path. Please install streamripper and add it to the path. The call this script again. Will exit now.'
    exit (1)

# json_url_epsiodes = "http://feeds.streams.demo.xenim.de/api/v1/episode/?list_endpoint" # The URL to receive all episodes
print "Retreiving list of all episodes."
json_url_epsiodes = "http://feeds.streams.demo.xenim.de/api/v1/episode/?list_endpoint" # The URL to receive all episodes
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
            print "Obtaining information about the podcast"
            json_podcast_url='http://feeds.streams.demo.xenim.de' + episode_podcast
            response_podcast = urllib.urlopen(json_podcast_url)
            data_podcast = json.loads(response_podcast.read().decode("utf-8-sig"))
            podcast_name = data_podcast['name']

            record(_url=epsidode_streaming_url,_podcast_name=podcast_name,_episode_title=episode_title, _episode_id=episode_id)
