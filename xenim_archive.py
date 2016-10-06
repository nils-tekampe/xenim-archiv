#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This little program checks the JSON API of xenim.de and looks for running streams
# For all running episodes, the name of the corresponding Podcast is acquired and
# the stream is saved to disk.
# This program requires the tool streamripper to be available in the path.
# If you have any questions, please let me know via nils@tekampe.org.

import urllib, json
import sys, codecs
import os.path
import pickle
import os
from subprocess import Popen, PIPE


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

#Helper function to record a stream to disk
def record ( _url, _podcast_name, _episode_title,_episode_id):
    dirname='/Users/nils/Documents/streams' # The folder where the recordings should be stored
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
        command= 'streamripper '+ _url  + ' -d '+ dirname +' -a ' + filename + '.'+epsidode_streaming_codec+ ' -c -A -m 60 > /dev/null 2>&1'
        print "Now executing the following command: " + command
        process = Popen([command], stdout=PIPE, stderr=PIPE, shell=True)
        process.wait()
        print process
        # print "test"
        stdout, stderr = process.communicate()
        print stdout
        print stderr

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
running_streams = [stream for stream in data['objects'] if stream['status']=='RUNNING']
print "Number of runnig streams: " +  str(len(running_streams))

#Iterate thru the running streams
for stream in running_streams:
    episode_podcast=stream['podcast']
    episode_title=stream['title']
    episode_id=stream['id']

    urls=stream['streams']
    epsidode_streaming_url=urls[0]['url']
    epsidode_streaming_codec=urls[0]['codec']

    json_podcast_url='http://feeds.streams.demo.xenim.de' + episode_podcast # This is the URL where the corresponding Podcast information can be found
    # json_podcast_url='http://feeds.demo.streams.xenim.de' + episode_podcast
    print "Obtaining information about the podcast: " + json_podcast_url
    response_podcast = urllib.urlopen(json_podcast_url)
    data_podcast = json.loads(response_podcast.read().decode("utf-8-sig"))
    podcast_name = data_podcast['name']
    print "Name des zugehoerigen Podcast lautet: " + podcast_name
    record(_url=epsidode_streaming_url,_podcast_name=podcast_name,_episode_title=episode_title, _episode_id=episode_id)
