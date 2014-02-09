import json
import urllib2
import urllib

class Limits:
    
    @staticmethod
    def LIMITS(start = 0, num = 0):
        limit = {}
        limit["start"] = start
        if num > 0:
            limit["end"] = start + num
        return limit

class Filter:
    """Class to build a filter parameter for JSON queries.
    
    Permits combination of filters via AND and/or OR methods.
    """
    @staticmethod
    def AND(filters):
        """filters should be passed as a list"""
        return {"AND": filters}
        
    @staticmethod
    def OR(filters):
        """filters should be passed as a list"""
        return {"or": filters}
        
    @staticmethod
    def FILTER(field, operator, value):
        return {"field": field,
                 "operator": operator,
                 "value": value}

class Sort:
    """Class to build sort parameter for JSON queries."""
    
    # List of params - useful if you've got autocomplete...
    NONE  = "none"
    LABEL  = "label"
    DATE  = "date"
    SIZE  = "size"
    FILE  = "file"
    PATH  = "path"
    DRIVETYPE  = "drivetype"
    TITLE  = "title"
    TRACK  = "track"
    TIME  = "time"
    ARTIST  = "artist"
    ALBUM  = "album"
    ALBUMTYPE  = "albumtype"
    GENRE  = "genre"
    COUNTRY  = "country"
    YEAR  = "year"
    RATING  = "rating"
    VOTES  = "votes"
    TOP250  = "top250"
    PROGRAMCOUNT  = "programcount"
    PLAYLIST  = "playlist"
    EPISODE  = "episode"
    SEASON  = "season"
    TOTALEPISODES  = "totalepisodes"
    WATCHEDEPISODES  = "watchedepisodes"
    TVSHOWSTATUS  = "tvshowstatus"
    TVSHOWTITLE  = "tvshowtitle"
    SORTTITLE  = "sorttitle"
    PRODUCTIONCODE  = "productioncode"
    MPAA  = "mpaa"
    STUDIO  = "studio"
    DATEADDED  = "dateadded"
    LASTPLAYED  = "lastplayed"
    PLAYCOUNT  = "playcount"
    LISTENERS  = "listeners"
    BITRATE  = "bitrate"
    RANDOM = "random"
    
    class sortorder:
        ASCENDING = "ascending"
        DESCENDING = "descending"
        
    @staticmethod
    def SORT(sort = TITLE, 
             sortorder = sortorder.ASCENDING, 
             ignorearticle = True):
        
        return {"method": sort,
                 "order": sortorder,
                 "ignorearticle": ignorearticle}

class SimpleXBMCJSON():
    """XBMCJSON class"""
    
    class sortorder:
        """Quasi-enum class for implementing sort order."""
        ASCENDING = "ascending"
        DESCENDING = "descending"
    
    # Define some constants
    # TODO - turn these into quasi-enum classes to allow user to 
    # choose properties
    ARTIST_PROPERTIES = [ "instrument",
                          "style",
                          "mood",
                          "born",
                          "formed",
                          "description",
                          "genre",
                          "died",
                          "disbanded",
                          "yearsactive",
                          "musicbrainzartistid",
                          "fanart",
                          "thumbnail"]
                          
    ALBUM_PROPERTIES = ["artist",
                        "artistid",
                        "albumlabel",
                        "year",
                        "thumbnail",
                        "genre"] 
 
    MOVIE_PROPERTIES = ["thumbnail", "file"] 
    
    # XBMC libraries
    AUDIO = 0
    VIDEO = 1
    PICTURES = 2
    
    # Autovivification class to simplify creation of parameter dicts
    # Thanks to Google and StackOverflow for this one!
    class AutoVivification(dict):
        """Implementation of perl's autovivification feature."""
        def __getitem__(self, item):
            try:
                return dict.__getitem__(self, item)
            except KeyError:
                value = self[item] = type(self)()
                return value

########################################################################
# Methods to initiates class and send requests                         #
########################################################################    
    def __init__(self, server="http://localhost:8080/jsonrpc"):
        """Initialise the class.
        
        Defaults to server on localhost unless overriden.
        
        TODO: add authentication
        """
        self.server = server

    def __buildRequest(self, method, params):
        """Build the JSON request.
        
        Returns it in dict format.
        """
        jsondict = {}
        jsondict["id"] = 1
        jsondict["method"] = method
        jsondict["jsonrpc"] = "2.0"
        if not params is None:
            jsondict["params"] = params
            
        return jsondict
        
    def __sendRequest(self,method, params = None):
        """Submit the JSON request.
        
        Returns the "result" field of JSON response or None.
        
        Can also be used to send any JSON request not directly 
        implemented in this class.
        """
        jsonrequest = json.dumps(self.__buildRequest(method,params))

        req = urllib2.Request(self.server, jsonrequest, 
                              {'Content-Type': 'application/json'})
        f = urllib2.urlopen(req)
        response = f.read()

        f.close()
        response = json.loads(response)
        try:
            return response["result"]
        except:
            return None

########################################################################
# XBMC input control methods                                           #
########################################################################
    def Left(self):
        return self.__sendRequest("Input.Left")
        
    def Right(self):
        return self.__sendRequest("Input.Right")
        
    def Up(self):
        return self.__sendRequest("Input.Up")
    
    def Down(self):
        return self.__sendRequest("Input.Down")
        
    def Home(self):
        return self.__sendRequest("Input.Home")
        
    def Back(self):
        return self.__sendRequest("Input.Back")

########################################################################
# GUI methods                                                          #
########################################################################        
    def ShowNotification(self, title, message):
        """Shows pop-up notification.
        
        TODO: add image and display time.
        """
        params = {}
        params["title"] = title
        params["message"] = message
        return self.__sendRequest("GUI.ShowNotification",params)

########################################################################
# Player methods                                                       #
########################################################################        
    def PlayerOpenFile(self, item):
        """Opens file.
        
        Takes local path or URL.
        """
        params = self.AutoVivification()
        params["item"]["file"] = item
        return self.__sendRequest("Player.Open",params)

    def PlayerPlayMovie(self, movieid):
        """Opens file.
        
        Takes local path or URL.
        """
        params = self.AutoVivification()
        params["item"]["movieid"] = movieid
        return self.__sendRequest("Player.Open",params)
        
    def GetActivePlayers(self):
        return self.__sendRequest("Player.GetActivePlayers")

    def PlayerPlayAlbum(self, albumid):
        """Opens file.
        
        Takes local path or URL.
        """
        params = self.AutoVivification()
        params["item"]["albumid"] = albumid
        return self.__sendRequest("Player.Open",params)
        
    def PlayerPlayTVEpisode(self, episodeid):
        params = self.AutoVivification()
        params["item"]["episodeid"] = episodeid
        return self.__sendRequest("Player.Open",params)        

########################################################################
# Library methods                                                      #
########################################################################
        
    def ScanLibrary(self, library):        
        """Updates library. 
        
        Must send AUDIO or VIDEO property.
        """
        if library == self.AUDIO:
            return self.__sendRequest("AudioLibrary.Scan")
        elif library == self.VIDEO:
            return self.__sendRequest("VideoLibrary.Scan")
        else:
            raise Exception("Can't scan library. Invalid library.")

#### AUDIO LIBRARY #####################################################
            
    def AudioGetArtists(self, mylimits = Limits.LIMITS(), mysort = Sort.SORT(), myfilter = None, properties = None):
        
        params = {}
                
        if not mylimits is None:
            params["limits"] = mylimits

        if not mysort is None:
            params["sort"] = mysort

        if not myfilter is None:
            params["filter"] = myfilter
        
        if not properties is None:
            params["properties"] = properties    
        
        
        return self.__sendRequest("AudioLibrary.GetArtists", params)
        
    def AudioGetArtistInfo(self, artistid):
        params = {}
        params["artistid"] = artistid
        params["properties"] = self.ARTIST_PROPERTIES
        return self.__sendRequest("AudioLibrary.GetArtistDetails",
                                   params)
        
    def AudioGetAlbums(self, artistid = None, mylimits = Limits.LIMITS(), mysort = Sort.SORT(), myfilter = None, properties = None):
        params = self.AutoVivification()
        
        if not mylimits is None:
            params["limits"] = mylimits

        if not mysort is None:
            params["sort"] = mysort

        if not myfilter is None:
            params["filter"] = myfilter
        
        if not properties is None:
            params["properties"] = properties    
        
        if artistid is not None:
            params["filter"]["artistid"] = artistid

        return self.__sendRequest("AudioLibrary.GetAlbums",params)

#### VIDEO LIBRARY #####################################################

    def GetMovies(self, myproperties = MOVIE_PROPERTIES, mylimits = Limits.LIMITS(), mysort = Sort.SORT(), myfilter = None):
        """Method to return movies in library.
        
        Optional parameters:
          start = number of first result (default 0)
          num = number of results to return (default 0 i.e. all)
          sort = how to sort results - uses sort class 
                 (default = sort.TITLE)
          sortorder = ascending/descending (default sortorder.ASCENDING)
          ignorearticle = ignore a/an/the (default True)
        """
        params = self.AutoVivification()
        
        if len(myproperties) > 0:
            params["properties"] = myproperties
        
        if not mylimits is None:
            params["limits"] = mylimits

        if not mysort is None:
            params["sort"] = mysort

        if not myfilter is None:
            params["filter"] = myfilter
        return self.__sendRequest("VideoLibrary.GetMovies",params)

    def GetMovieLibrarySize(self, myproperties = MOVIE_PROPERTIES, mylimits = Limits.LIMITS(), mysort = Sort.SORT(), myfilter = None):
        """Returns the number of movies in the video library."""
        return len(self.GetMovies(myproperties=myproperties, mylimits=mylimits, mysort=mysort, myfilter=myfilter)["movies"])


    def GetTVShows(self, mylimits = Limits.LIMITS(), mysort = Sort.SORT(), myfilter = None, properties = None):
        """Returns list of TV shows"""
        params = self.AutoVivification()
        
        
        if not mylimits is None:
            params["limits"] = mylimits

        if not mysort is None:
            params["sort"] = mysort

        if not myfilter is None:
            params["filter"] = myfilter
        
        if not properties is None:
            params["properties"] = properties    
        
        return self.__sendRequest("VideoLibrary.GetTVShows", params)
        
    def GetTVSeasons(self, tvshowid, mylimits = Limits.LIMITS(), properties = None):
        
        params = {}
        
        if not properties is None:
            params["properties"] = properties
        
        if not mylimits is None:
            params["limits"] = mylimits
        
        params["tvshowid"] = tvshowid
        
        return self.__sendRequest("VideoLibrary.GetSeasons", params)
        
    def GetTVEpisodes(self, tvshowid, seasonid = -1, properties = None, mylimits = Limits.LIMITS(), mysort = Sort.SORT(), myfilter = None):
        
        params = {}        
        
        if not mylimits is None:
            params["limits"] = mylimits

        if not mysort is None:
            params["sort"] = mysort

        if not myfilter is None:
            params["filter"] = myfilter
            
        if not properties is None:
            params["properties"] = properties
        
        params["tvshowid"] = tvshowid    
        params["season"] = seasonid
        
        return self.__sendRequest("VideoLibrary.GetEpisodes", params)
        

#### MISCELLANEOUS METHODS #############################################
        
    def Ping(self):
        if self.__sendRequest("JSONRPC.Ping") == "pong":
            return True
        else:
            return False

    def GetURL(self, path):
        params = {}
        params["path"] = path
        try:
            return self.__sendRequest("Files.PrepareDownload",
                                        params)["details"]["path"]
        except:
            return None




