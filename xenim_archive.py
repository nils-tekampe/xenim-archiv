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
import time
from subprocess import Popen, PIPE,STDOUT
import subprocess
from threading import Thread, Lock
import logging, logging.config

logger = logging.getLogger("xenim")

base_url="http://feeds.streams.demo.xenim.de"

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
def record ( _url, _podcast_name, _episode_title,_episode_id, _epsidode_streaming_codec):
    logger.info( "Starting record function for " + _podcast_name)
    dirname='/Users/nils/Documents/streams' # The folder where the recordings should be stored
    recordings = {} # All recordings are saved into this dict so that they are only started once
    if os.path.isfile('/tmp/recordings.txt'):
        with open('/tmp/recordings.txt', 'rb') as handle:
          recordings = pickle.loads(handle.read())

    # Only proceed if this recording is not yet running.
    lck = Lock()
    if not (_episode_id in recordings):
        lck.acquire()
        logger.info( _podcast_name + ": Found the following new podcast stream: " + _url)
        logger.info( "episode_id: "+ _episode_id)
        lck.release()
        # Adding the recording to the hashtable so that is is only started once
        lck.acquire()
        recordings[_episode_id]=_url
        #Saving the recordings dictionary so that they will be available for next start
        with open('/tmp/recordings.txt', 'wb') as handle:
          pickle.dump(recordings, handle)
        lck.release()
        # Building the local filename and the command for ripping
        filename=_podcast_name + '_' + _episode_title
        command= 'streamripper '+ _url  + ' -d '+ dirname +' -a ' + filename + '.'+_epsidode_streaming_codec+ ' -c -A -m 60 --codeset-filesys=UTF-8 --codeset-id3=UTF-8 --codeset-metadata=UTF-8 --codeset-relay=UTF-8'
        #command= 'streamripper '+ _url  + ' -d '+ dirname +' -a ' + filename + '.'+_epsidode_streaming_codec+ ' -c -A -m 60'
        lck.acquire()
        logger.info( _podcast_name + ": Now executing the following command: " + command)
        lck.release()

        process = Popen([command], stdout=PIPE, stderr=STDOUT, shell=True)
        while True:
            line = process.stdout.readline()
            if len(line)==0:
                break
            lck.acquire()
            sys.stdout.write(_podcast_name+": ")
            sys.stdout.write(line)
            lck.release()

        process.wait()
        return_code = process.wait()
        if return_code != 0:
            raise subprocess.CalledProcessError(return_code, command)

        # In this moment the ripping has finished. So we need to remove the stream from the hashtable
        lck.acquire()
        del recordings[_episode_id]
        #Saving the recordings dictionary so that they will be available for next start
        with open('/tmp/recordings.txt', 'wb') as handle:
          pickle.dump(recordings, handle)
        lck.release()
    else:
        lck.acquire()
        logger.info( "Skipping podcast " +_podcast_name + " as record seems already be running")
        lck.release()

###########################
#Main function starts here#
###########################
def main():

    logger.setLevel(logging.INFO)

    # create the logging file handler
    fh = logging.FileHandler("/tmp/xenim.log")
    sh = logging.StreamHandler()

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)

    # add handler to logger object
    logger.addHandler(fh)
    logger.addHandler(sh)

    logger.info("Starting xenim recording script")


    if which('streamripper')==None:
        logger.error('Could not find streamripper in the path. Please install streamripper and add it to the path. The call this script again. Will exit now.')
        exit (1)

    logger.info("Retreiving list of all episodes.")

    json_url_epsiodes = base_url+"/api/v1/episode/?list_endpoint" # The URL to receive all episodes
    # Open the URL
    response = urllib.urlopen(json_url_epsiodes)
    data = json.loads(response.read().decode("utf-8-sig"))

    # We need to replace the output function as we have unicode characters
    utf8_writer = codecs.getwriter('UTF-8')
    sys.stdout = utf8_writer(sys.stdout, errors='replace')

    # Parse the answer. Look for running episodes only
    logger.info("Filtering for running episodes")
    running_streams = [stream for stream in data['objects'] if stream['status']=='RUNNING']
    logger.info("Number of runnig streams: " +  str(len(running_streams)))

    # List of threads that we start
    threads=[]
    #Iterate thru the running streams
    for stream in running_streams:
        # Gettging some information on the stream
        episode_podcast=stream['podcast']
        episode_title=unicode(stream['title'])
        episode_id=stream['id']
        urls=stream['streams']
        epsidode_streaming_url=urls[0]['url']
        epsidode_streaming_codec=urls[0]['codec']

        #json_podcast_url='http://feeds.streams.xenim.de' + episode_podcast # This is the URL where the corresponding Podcast information can be found
        json_podcast_url=base_url + episode_podcast
        logger.info("Obtaining information about the podcast: " + json_podcast_url)
        response_podcast = urllib.urlopen(json_podcast_url)
        data_podcast = json.loads(response_podcast.read().decode("utf-8-sig"))
        podcast_name = unicode(data_podcast['name'])
        logger.info("Name des zugehoerigen Podcast lautet: " + podcast_name)
        t=Thread(target=record,args=(epsidode_streaming_url,podcast_name,episode_title, episode_id,epsidode_streaming_codec,))
        threads.append(t)
        t.start()

    # wait for all threads to finish
    time.sleep(25)
    for t in threads:
        t.join()
    logger.info("Exiting skript")


if __name__ == '__main__':
    main()
