#!/usr/bin/python3

from gmusicapi import Mobileclient
from os import listdir
import datetime
import time
import argparse

mc = Mobileclient()
mc.__init__()

parser = argparse.ArgumentParser(description='Flags for auto repeat')
parser.add_argument('-r', action='store_true') # action='store_true' => default false
args = parser.parse_args()

# initialise a boolean to determine whether the autorepeat function can be used
autoRepeat = False

# Check whether this is the first time the program has been run by searching the directory for the log file
fileExists = False
fileList = listdir("/home/hamish/bin/gmusic")
for file in fileList:
    if file.find('gmusiclog') != -1:
        fileExists = True
        break

# If this is the first time, create a log file, store the device ID
if fileExists == False:
    print()
    print('This is the first time this program has been run in this folder, performing initial authentication.')
    print()
    devID = 'ffffffff'
    mc.perform_oauth()
    try:
        mc.oauth_login(devID)
    except Exception as e: 
        error = str(e)
        IDpos = error.find('*')
        nextIDpos = error.find('\n', IDpos+1, len(error))
        devID = error[IDpos+2:nextIDpos]
        # print(devID)

    mc.oauth_login(devID)
    log = open('/home/hamish/bin/gmusic/gmusiclog.txt', 'w') 
    log.write(devID + '\n')
    x = datetime.datetime.now()
    timeString = str(x.day) + '/' + str(x.month) + '/' + str(x.year) + '  ' + str(x.hour) + ':' + str(x.minute) + ':' + str(x.second) + '.' + str(x.microsecond)
    log.write('Initial authentication performed at ' + timeString + '\n')
    log.close()
else:
    # Log file exists, we will check whether the user has requested autorepeat
    print()
    print('This is not the first time this program has been run in this folder, performing login.' + '\n')
    log = open('/home/hamish/bin/gmusic/gmusiclog.txt', 'r')

    # Get device ID
    devID = log.readline().strip()

    # Look for the playlist name
    contents = log.read()
    playlistLocation = contents.rfind('PLAYLIST')
    if playlistLocation != -1:
        endOfPlaylist = contents.find('\n', playlistLocation, len(contents))
        if args.r == True:
            autoRepeat = True
            desiredPlaylist = contents[playlistLocation+10:endOfPlaylist]
            print('Autorepeat enabled, reversing playlist: ' + desiredPlaylist + '\n')
    log.close()
    print()
    mc.oauth_login(devID)
    x = datetime.datetime.now()
    timeString = str(x.day) + '/' + str(x.month) + '/' + str(x.year) + '  ' + str(x.hour) + ':' + str(x.minute) + ':' + str(x.second) + '.' + str(x.microsecond)
    log = open('/home/hamish/bin/gmusic/gmusiclog.txt', 'a')
    log.write('Login performed at ' + timeString + '\n')
    log.close()

# Get user input for desired playlist if autorepeat is not enabled
if autoRepeat == False:
    desiredPlaylist = input('Name of the playlist being reversed (case sensetive): ')

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
    log = open('/home/hamish/bin/gmusic/gmusiclog.txt', 'a')
    log.write('PLAYLIST: ' + desiredPlaylist + '\n')
    log.close()
    
    if reversedPlaylistIndex != -1:
        # Playlist has been reversed, we will update the reverse
        print('The ' + desiredPlaylist + ' playlist has been reversed, updating the reverse.')        
    else:
        print('The ' + desiredPlaylist + ' playlist has not been reversed, creating the reverse now.')
            
    # Get full contents
    fullContents = mc.get_all_user_playlist_contents()
    for n in fullContents:
        if n['name'] == desiredPlaylist:
            trackDict = n['tracks']
            numSongs = len(trackDict)
        elif n['name'] == reversedPlaylist:
            reversedTrackDict = n['tracks']
            reversedNumSongs = len(reversedTrackDict)

    # Loop backwards through the original playlist. 
    # If the song does not exist in the playlist:
        # Add it to the playlist in the right spot
    # If the song does exist in the playlist:
        # Delete all the songs before it
        # Move back a song in the original playlist
        # Move forward a song in the reversed playlist

    numMatchesTitleAlbumArtist = 0

    numMatchesStoreID = 0
    numMatchesTrackID = 0
    numMatchesBothIDs = 0

    x = 0


    for i in range(numSongs-1,-1):
        # # reversedNumSongs -= 1
        # origDict = trackDict[i]

        # # Check for a subdict
        # if 'track' in origDict:

        #     # Extract subdict
        #     subOrigDict = origDict['track']

        #     # Loop through reversed playlist
        #     for j in range(reversedNumSongs):

        #         revDict = reversedTrackDict[j]
                
        #         # Check for a subdict in the reversed song
        #         if 'track' in revDict:

        #             if subOrigDict['title'] == subRevDict['title'] and \
        #                subOrigDict['album'] == subRevDict['album'] and \
        #                subOrigDict['artist'] == subRevDict['artist']:
        #                 numMatchesTitleAlbumArtist += 1
        #             if subOrigDict['storeId'] == subRevDict['storeId']:
        #                 numMatchesStoreID += 1
        #                 numMatchesBothIDs += 1
                
        # else: # There is no subdict
        #     for j in range(reversedNumSongs):
        #         revDict = reversedTrackDict[j]
        #         if 'track' not in revDict:
        #             print(revDict)
        #             if origDict['trackId'] == revDict['trackId']:
                        

        try:
            subOrigDict = origDict['track']
            for j in range(reversedNumSongs):
                revDict = reversedTrackDict[j]
                try:
                    subRevDict = revDict['track']
                    if subOrigDict['title'] == subRevDict['title'] and \
                       subOrigDict['album'] == subRevDict['album'] and \
                       subOrigDict['artist'] == subRevDict['artist']:
                        numMatchesTitleAlbumArtist += 1
                    if subOrigDict['storeId'] == subRevDict['storeId']:
                        numMatchesStoreID += 1
                        numMatchesBothIDs += 1
                except Exception:
                    pass
        
        # If there is no subdict
        except Exception:
            for j in range(reversedNumSongs):
                try:
                    subRevDict = revDict['track']
                except Exception:
                    print(revDict)
                    if origDict['trackId'] == revDict['trackId']:
                        numMatchesTrackID += 1
                        numMatchesBothIDs += 1


    print('\n\n\n')
    print(f'Number of matches based on song, artist, album: {numMatchesTitleAlbumArtist}')
    print(f'Number of matches based on store ID: {numMatchesStoreID}')
    print(f'Number of matches based on track ID: {numMatchesTrackID}')
    print(f'Number of matches based on both IDs: {numMatchesBothIDs}')
        

        # if i == 25 or i == 50:
        #     print(origDict)
        #     print()
        
        

            




    # # Loop through original playlist and modify 
    # while numSongs > 0:
    #     numSongs -= 1
    #     dicto = trackDict[numSongs]
    #     try:
    #         subDict = dicto['track']
    #         print(str(numSongs+1) + ' - ' + subDict['title'])

    #         mc.add_songs_to_playlist(reversedID,subDict['storeId'])
    #     except:
    #         print()
    #         print('Error adding track no. %d the usual way, trying a backup method' % numSongs)
    #         try:
    #             mc.add_songs_to_playlist(reversedID,dicto['trackId'])
    #             print('Backup method worked! Song no. %d added successfully.' % numSongs)
    #         except:
    #             print('That didn\'t work either :(')
    #         print()

    
else:
    # No such playlist exists
    print('No playlist by the name of ' + desiredPlaylist + ' found. Did you spell it correctly? A reminder here that the playlist name is case sensetive.')
