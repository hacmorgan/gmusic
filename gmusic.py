#!/usr/bin/python3

from gmusicapi import Mobileclient
import os
import datetime
import time
import argparse

def reverseplaylist(playlist_name = '', repeat = False, quick = False):
    mc = Mobileclient()
    mc.__init__()

    # Find location of this script
    dir_path = os.path.dirname(os.path.realpath(__file__))
    
    # Check whether this is the first time the program has been run by searching the directory for the log file
    file_list = os.listdir(dir_path)
    
    # No log file means not run
    if '.gmusiclog.txt' not in file_list:
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

    # Log file exists, we will check whether the user has requested autorepeat
    else:
        print('\n' +
              'This is not the first time this program has been run in this folder' +
              '\n' +
              'performing login.' +
              '\n')

        # Open the logfile to read device id and previous playlists
        with open(dir_path + '/.gmusiclog.txt', 'r') as log:
            # Get device ID
            devID = log.readline().strip()
            # Look for the playlist name from the bottom of the list
            contents = log.read()
            
        # Perform login
        mc.oauth_login(devID)
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
    desired_playlist_index = -1
    reversed_playlist_index = -1
    for n in allPlaylists:
        if n['name'] == reversed_playlist:
            reversed_playlist_index = n
            reversedID = n['id']
        elif n['name'] == desired_playlist:
            desired_playlist_index = n
            desiredID = n['id']

    # Desired playlist exists, so we check to see if it has also been reversed
    if desired_playlist_index != -1:
        # We cache the playlist name so that it can be automatically re-reversed next time
        with open(dir_path + '/.gmusiclog.txt', 'a+') as log:
            log.write('PLAYLIST: ' + desired_playlist + '\n')

        # Desired playlist has been reversed, we can either delete the old one before proceeding
        # or perform a quick update
        if reversed_playlist_index != -1:
            print('The ' + desired_playlist +
                  ' playlist has been reversed.')

            # Determine whether to do a quick update or not
            if quick == True:
                print('performing quick update')
                quick_update(mc, desiredID, reversedID)
                return
            else:
                print('Performing full update\n' +
                      'Deleting the old playlist...\n')
                mc.delete_playlist(reversedID)

        # Desired playlist has not been reversed, create the reverse
        else:
            print('The ' + desired_playlist + ' playlist has not been reversed, creating the reverse now.')

        # If we have got this far, the reversed playlist doesn't exist
        print('Generating reversed song list...')
        reversedID, id_list = create_new(mc, desired_playlist)
        print('Adding songs to the playlist...')
        mc.add_songs_to_playlist(reversedID, id_list)
        print('Done!')
            
    # No such playlist exists
    else:
        print('No playlist by the name of ' + desired_playlist +
              ' found. Did you spell it correctly? A reminder here that the playlist name is case sensetive.')


        

'''
This function iterates forward through the original playlist and backward
through the reversed playlist, searching for matches
'''
def quick_update(mc, desiredID, reversedID):
    # Get full contents
    full_contents = mc.get_all_user_playlist_contents()

    # Extract the correct dictionaries
    for n in full_contents:
        if n['id'] == desiredID:
            desired_dict = n['tracks']
        elif n['id'] == reversedID:
            reversed_dict = n['tracks']

    # First we must check if it is necessary to delete any entries
    songs_to_delete = []
    for sub_reversed_dict in reversed_dict:
        if is_song_in_playlist(desired_dict, sub_reversed_dict) == False:
            songs_to_delete.append(sub_reversed_dict['id'])
    if songs_to_delete != []:
        mc.remove_entries_from_playlist(songs_to_delete)
    print('Deleting the following songs: ')
    print(songs_to_delete)

    # Now we find any songs that are in the desired playlist but are not in the reversed
    songs_to_add = []
    for sub_desired_dict in desired_dict:
        if is_song_in_playlist(reversed_dict, sub_desired_dict) == False:
            if 'track' in sub_desired_dict:
                songs_to_add.append(sub_desired_dict['track']['storeId'])
            else:
                songs_to_add.append(sub_desired_dict['trackId'])
    if songs_to_add != []:
        mc.add_songs_to_playlist(reversedID, songs_to_add)
    print('Adding the following songs: ')
    print(songs_to_add)
        


        
'''
Determine whether a given playlist contains a given song
'''
def is_song_in_playlist(playlist_dict, song_dict):
    # If we have lots of song detail
    if 'track' in song_dict:
        for sub_playlist_dict in playlist_dict:
            if 'track' not in sub_playlist_dict:
                continue
            elif sub_playlist_dict['track']['storeId'] == song_dict['track']['storeId']:
                return True

    # Otherwise we must have only a small amount of detail
    else:
        for sub_playlist_dict in playlist_dict:
            if 'track' in sub_playlist_dict:
                continue
            elif sub_playlist_dict['trackId'] == song_dict['trackId']:
                return True

    # Return false if no match found
    return False





'''
Function to create a new playlist and populate it with the songs in reverse order
'''
def create_new(mc, desired_playlist):
    # Create the new playlist and a list to store song ids to add to it
    reversed_playlist = desired_playlist + 'REVERSED'
    reversedID = mc.create_playlist(reversed_playlist)
    id_list = []
    
    # Find the appropriate playlist dictionary
    full_contents = mc.get_all_user_playlist_contents()
    for n in full_contents:
        if n['name'] == desired_playlist:
            trackDict = n['tracks']
            break
    
    # Begin looping
    numSongs = len(trackDict)
    while numSongs > 0:
        numSongs -= 1
        dicto = trackDict[numSongs]
        if 'track' in dicto:
            subDict = dicto['track']
            print(str(numSongs+1) + ' - ' + subDict['title'])
            id_list.append(subDict['storeId'])
        else:
            print('\n' +
                  'Could not add track no. %d the usual way, trying a backup method'
                  % (numSongs+1))
            if 'trackId' in dicto:
                id_list.append(dicto['trackId'])
                # Ths print is only here to find a way to print the song name
                print('Backup method worked! Song no. %d added successfully.\n'
                      % (numSongs+1))
            else:
                print('That didn\'t work either :(\n')

    # Return the playlist id and list of song ids to call the add function once
    return reversedID, id_list




                

        

'''
If this script is run by itself, check for the -r flag
'''
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = 'Flags for auto repeat and quick update')
    parser.add_argument('--repeat', '-r', action = 'store_true') # action='store_true' => default false
    parser.add_argument('--quick', '-q', action = 'store_true')
    args = parser.parse_args()
    reverseplaylist(repeat = args.repeat, quick = args.quick)
