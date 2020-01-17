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
                desiredPlaylist = contents[playlistLocation+10:endOfPlaylist]


        with open(dir_path + '/.gmusiclog.txt', 'a+') as log:
            
            # Write authentication stuff to logfile
            x = datetime.datetime.now()
            timeString = ( str(x.day) + '/' + str(x.month) + '/' + str(x.year) + '  ' +
                           str(x.hour) + ':' + str(x.minute) + ':' + str(x.second) + '.' +
                           str(x.microsecond) )
            log.write('Login performed at ' + timeString + '\n')

            
    
    # Get user input for desired playlist if autorepeat is not enabled
    if repeat == False and playlist_name == '':
        desiredPlaylist = input('Name of the playlist being reversed (case sensetive): ')
    elif playlist_name != '':
        # If a name is given this overrides all else
        desiredPlaylist = playlist_name
    else:
        print('Autorepeat enabled, reversing playlist: ' + desiredPlaylist + '\n')
        
    reversedPlaylist = desiredPlaylist + 'REVERSED'

    allPlaylists = mc.get_all_playlists()
    desiredPlaylistIndex = -1
    reversedPlaylistIndex = -1

    for n in allPlaylists:
        if n['name'] == reversedPlaylist:
            reversedPlaylistIndex = n
            reversedID = n['id']
        elif n['name'] == desiredPlaylist:
            desiredPlaylistIndex = n
            desiredID = n['id']

    if desiredPlaylistIndex != -1:
        # Playlist exists, so we check to see if it has also been reversed
        # We also cache the playlist name so that it can be automatically re-reversed next time
        with open(dir_path + '/.gmusiclog.txt', 'a+') as log:
            log.write('PLAYLIST: ' + desiredPlaylist + '\n')

        if reversedPlaylistIndex != -1:
            # Playlist has been reversed, we delete the old one before proceeding
            print('The ' + desiredPlaylist +
                  ' playlist has been reversed.' +
                  '\n' +
                  'Deleting the reverse and creating a new one now.')
            mc.delete_playlist(reversedID)

        else:
            print('The ' + desiredPlaylist + ' playlist has not been reversed, creating the reverse now.')

        reversedID = mc.create_playlist(reversedPlaylist)

        fullContents = mc.get_all_user_playlist_contents()
        for n in fullContents:
            if n['name'] == desiredPlaylist:
                trackDict = n['tracks']
                numSongs = len(trackDict)
                while numSongs > 0:
                    numSongs -= 1
                    dicto = trackDict[numSongs]
                    try:
                        subDict = dicto['track']
                        print(str(numSongs+1) + ' - ' + subDict['title'])
                        mc.add_songs_to_playlist(reversedID,subDict['storeId'])
                    except:
                        print('\n' +
                              'Error adding track no. %d the usual way, trying a backup method'
                              % (numSongs+1))
                        try:
                            mc.add_songs_to_playlist(reversedID,dicto['trackId'])
                            # Ths print is only here to find a way to print the song name
                            print('\n' +
                                  'Backup method worked! Song no. %d added successfully.'
                                  % (numSongs+1))
                        except:
                            print('That didn\'t work either :(')
                        print()


    else:
        # No such playlist exists
        print('No playlist by the name of ' + desiredPlaylist +
              ' found. Did you spell it correctly? A reminder here that the playlist name is case sensetive.')



'''
If this script is run by itself, check for the -r flag
'''
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Flags for auto repeat')
    parser.add_argument('--repeat', '-r', action='store_true') # action='store_true' => default false
    args = parser.parse_args()
    reverseplaylist(repeat = args.repeat)
