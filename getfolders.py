from simplexbmcjson import SimpleXBMCJSON
import sys
import os

host = "http://192.168.1.10:8080/"

xbmc = SimpleXBMCJSON(host + "jsonrpc")


result = xbmc.GetMovies(myproperties=["file"])

try:
    movies = result["movies"]

except:
    print "No Movies found in library"
    sys.exit(1)
    
print "Number of movies found:", str(len(movies))

folders = []

for movie in movies:
    if not os.path.dirname(movie["file"]) in folders:
        folders.append(os.path.dirname(movie["file"]))

print "Movies stored in following folders:"
for folder  in folders:
    print folder


