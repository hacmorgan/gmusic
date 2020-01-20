#!/usr/bin/python3

from gmusicapi import Mobileclient
import os
import datetime
import time
import argparse

def reverseplaylist(playlist_name = '', repeat = False):
    mc = Mobileclient()
    mc.__init__()

    # Find location of this script
    dir_path = os.path.dirname(os.path.realpath(__file__))
    
    # Check whether this is the first time the program has been run by searching the directory for the log file
    fileList = os.listdir(dir_path)
    if '.gmusiclog.txt' not in fileList:
        # No log file means not run
        print('\n' +
              'This is the first time this program has been run in this folder.' +
              '\n' +
              'performing initial authentication.' +
              '\n')

        # Autorepeat cannot be true without logfile, override if true
        repeat = False

        # Start with a bogus device ID to determine real id from error message
        devID = 'ffffffff'
        mc.perform_oauth()
        try:
            mc.oauth_login(devID)
        except Exception as e: 
            error = str(e)
            IDpos = error.find('*')
            nextIDpos = error.find('\n', IDpos+1, len(error))
            devID = error[IDpos+2:nextIDpos]
            # Perform login
            mc.oauth_login(devID)

        # Write authentication stuff to logfile
        with open(dir_path + '/.gmusiclog.txt', 'w') as log:
            log.write(devID + '\n')
            x = datetime.datetime.now()
            timeString = ( str(x.day) + '/' + str(x.month) + '/' + str(x.year) + '  ' +
                           str(x.hour) + ':' + str(x.minute) + ':' + str(x.second) + '.' +
                           str(x.microsecond) )
            log.write('Initial authentication performed at ' + timeString + '\n')

    else:
        # Log file exists, we will check whether the user has requested autorepeat
        print('\n' +
              'This is not the first time this program has been run in this folder' +
              '\n' +
              'performing login.' +
              '\n')

        # Open the logfile
        with open(dir_path + '/.gmusiclog.txt', 'r') as log:
            # Get device ID
            devID = log.readline().strip()
            # Perform login
            mc.oauth_login(devID)
            # Look for the playlist name from the bottom of the list
            contents = log.read()
            playlistLocation = contents.rfind('PLAYLIST')
            if playlistLocation != -1:
                # Define end of playlist to make defining desired playlist a little cleaner
                endOfPlaylist = contents.find('\n', playlistLocation, len(contents))
                desired_playlist = contents[playlistLocation+10:endOfPlaylist]


        with open(dir_path + '/.gmusiclog.txt', 'a+') as log:
            
            # Write authentication stuff to logfile
            x = datetime.datetime.now()
            timeString = ( str(x.day) + '/' + str(x.month) + '/' + str(x.year) + '  ' +
                           str(x.hour) + ':' + str(x.minute) + ':' + str(x.second) + '.' +
                           str(x.microsecond) )
            log.write('Login performed at ' + timeString + '\n')

             
    # Get user input for desired playlist if autorepeat is not enabled
    if repeat == False and playlist_name == '':
        desired_playlist = input('Name of the playlist being reversed (case sensetive): ')
    elif playlist_name != '':
        # If a name is given this overrides all else
        desired_playlist = playlist_name
    else:
        print('Autorepeat enabled, reversing playlist: ' + desired_playlist + '\n')

    # Establish the name of the reversed playlist
    reversed_playlist = desired_playlist + 'REVERSED'

    # Check to see whether the desired and reversed playlists exist yet
    allPlaylists = mc.get_all_playlists()
    desired_playlistIndex = -1
    reversed_playlist_index = -1
    for n in allPlaylists:
        if n['name'] == reversed_playlist:
            reversed_playlist_index = n
            reversedID = n['id']
        elif n['name'] == desired_playlist:
            desired_playlistIndex = n
            desiredID = n['id']

    # Playlist exists, so we check to see if it has also been reversed
    if desired_playlistIndex != -1:
        # We also cache the playlist name so that it can be automatically re-reversed next time
        with open(dir_path + '/.gmusiclog.txt', 'a+') as log:
            log.write('PLAYLIST: ' + desired_playlist + '\n')

        if reversed_playlist_index != -1:
            # Playlist has been reversed, we delete the old one before proceeding
            print('The ' + desired_playlist +
                  ' playlist has been reversed.' +
                  '\n' +
                  'Deleting the reverse and creating a new one now.')

            # If both playlists exist already, see how far we can iterate through both until we reach a discrepancy
            iterate_through(mc, desiredID, reversedID)
            return
            mc.delete_playlist(reversedID)

        else:
            print('The ' + desired_playlist + ' playlist has not been reversed, creating the reverse now.')

        reversedID = mc.create_playlist(reversed_playlist)

        fullContents = mc.get_all_user_playlist_contents()
        for n in fullContents:
            if n['name'] == desired_playlist:
                trackDict = n['tracks']
                numSongs = len(trackDict)
                while numSongs > 0:
                    numSongs -= 1
                    dicto = trackDict[numSongs]
                    if 'track' in dicto:
                        subDict = dicto['track']
                        print(str(numSongs+1) + ' - ' + subDict['title'])
                        mc.add_songs_to_playlist(reversedID,subDict['storeId'])
                    else:
                        print('\n' +
                              'Could not add track no. %d the usual way, trying a backup method'
                              % (numSongs+1))
                        if 'trackId' in dicto:
                            mc.add_songs_to_playlist(reversedID,dicto['trackId'])
                            # Ths print is only here to find a way to print the song name
                            print('Backup method worked! Song no. %d added successfully.'
                                  % (numSongs+1))
                        else:
                            print('That didn\'t work either :(')
                        print()

    else:
        # No such playlist exists
        print('No playlist by the name of ' + desired_playlist +
              ' found. Did you spell it correctly? A reminder here that the playlist name is case sensetive.')


'''
This function iterates forward through the original playlist and backward
through the reversed playlist, searching for matches
'''
def iterate_through(mc, desiredID, reversedID):
    # Get full contents
    fullContents = mc.get_all_user_playlist_contents()

    # Extract the correct dictionaries
    for n in fullContents:
        if n['id'] == desiredID:
            desired_dict = n['tracks']
        elif n['id'] == reversedID:
            reversed_dict = n['tracks']

    playlist_length = len(desired_dict)
    for i in range(playlist_length):
        sub_desired_dict = desired_dict[i]
        sub_reversed_dict = reversed_dict[-i-1]
        if 'track' not in sub_desired_dict and sub_desired_dict['trackId'] == sub_reversed_dict['trackId']:
            print('Matching trackIds (i.e. less detailed entry) for track no. ' + str(i))
            continue
        elif sub_desired_dict['track']['storeId'] == sub_reversed_dict['track']['storeId']:
            print('Matching storeIds (i.e. more detailed entry) for track no. ' + str(i))
            continue
        elif (elsewhere_in_playlist(reversed_dict, sub_desired_dict) == True or
              elsewhere_in_playlist(desired_dict, sub_reversed_dict) == True):
            # No match found, check if the song is elsehwere in the reversed playlist
            print('Found track somewhere else in playlist')
        else:
            # Delete the remainder of the reversed playlist by adding the entry IDs 
            


'''
Determine whether a given song is elsehwere in a playlist
'''
def elsewhere_in_playlist(reversed_dict, sub_desired_dict):
    if 'track' in sub_desired_dict:
        for sub_reversed_dict in reversed_dict:
            if 'track' not in sub_reversed_dict:
                continue
            elif sub_reversed_dict['track']['storeId'] == sub_desired_dict['track']['storeId']:
                return True
    else:
        for sub_reversed_dict in reversed_dict:
            if 'track' in sub_reversed_dict:
                continue
            elif sub_reversed_dict['trackId'] == sub_desired_dict['trackId']:
                return True

    # Return false if no match found
    return False
                

        

'''
If this script is run by itself, check for the -r flag
'''
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Flags for auto repeat')
    parser.add_argument('--repeat', '-r', action='store_true') # action='store_true' => default false
    args = parser.parse_args()
    reverseplaylist(repeat = args.repeat)
