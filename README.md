# What each script does
- ___gmusic.py___ is the original playlist reversing script.
- ___gmusic-repeat.py___ is a work-in-progress script for implementing a more efficient algorithm than is used by _gmusic.py_.
- A script for synchronising a Google Play Music playlist and a Spotify playlist is to be developed. 


# Arguments
The user can run _gmusic.py_ with the _-r_ flag, which will find the most recent playlist to have been reversed by the script, by searching the text file _gmusiclog.txt_. If the script has not been run before, or if the _-r_ flag has not been supplied, the script will prompt the user for the playlist they wish to reverse. 

#NOTES:
The first line of gmusic.py tells bash which file to use to run the script.
 
By then using chmod +x gmusic.py, we make it executable in its own right (i.e. no need to say python3 gmusic.py)

Then by adding ~/bin/gmusic to PATH in .bashrc, we can simply type gmusic.py in a terminal and it will run as usual

MORE EFFICIENT METHOD:
for each song in original playlist:
    check if in reversed playlist
