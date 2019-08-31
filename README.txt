NOTES:
The first line of gmusic.py tells bash which file to use to run the script.
 
By then using chmod +x gmusic.py, we make it executable in its own right (i.e. no need to say python3 gmusic.py)

Then by adding ~/bin/gmusic to PATH in .bashrc, we can simply type gmusic.py in a terminal and it will run as usual

MORE EFFICIENT METHOD:
for each song in original playlist:
    check if in reversed playlist