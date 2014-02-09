#-------------------------------------------------------------------------------
#---[ Imports ]-----------------------------------------------------------------
#-------------------------------------------------------------------------------
import sys, pygame
from menu import *
from image import *
from math import ceil

from simplexbmcjson import SimpleXBMCJSON, Filter, Limits, Sort
from xbmcimages import xbmcimages

## ---[ main ]------------------------------------------------------------------
#  This function runs the entire screen and contains the main while loop
#
def main():
   
   # Filter movie folders
   # Need unique name in folder path 
   menu1folder = "afp://192.168.1.6/4TB-Movies/3D Movies" # 3D MOVIES
   menu2folder = "afp://192.168.1.6/4TB-Movies/HD Movies" # HD MOVIES
   menu4folder = "afp://192.168.1.6/4TB-Movies/Movies" # MOVIES
   
   tvthumbs = [ {"size": ( 315, 205), "offset": 10, "preserveratio": True},
                {"size": (315, 205), "offset": 10, "preserveratio": False}
              ]
   
   # TV Thumbnail size
   # 0 - square with black borders - image maintains aspect ratio
   # 1 - 16:9
   tvthumbsize = 1              
   
   
   # Where is our XBMC located
   # Needs trailing slash
   host = "http://192.168.1.10:8080/"
   
   # Function to do 3D movies menu 
   def UpdateMovieMenu(menu, rootscreen, restrictfolder = None):
       movie_imgs = []
       menu.menu_items=[]
       # Let's get the movies we need - just 8 records as that's all
       # we can display on one screen
       # TODO: Padding if not enough results
       if restrictfolder is None:
           myfilter = None
       else:
           myfilter = Filter.FILTER("path", "contains", restrictfolder)
       movielimits = Limits.LIMITS((menu.page * 8), 8)
       totalmovies = xbmc.GetMovieLibrarySize(myfilter=myfilter)
       maxpages = ceil(totalmovies/8.0) - 1
       for movie in xbmc.GetMovies(mylimits=movielimits,myfilter=myfilter)['movies']:
           # Get the movie thumbnail
           movieimage = pygame.transform.scale(libraryimages.getMovieThumb(movie),(205, 315))
           # Create the button
           button = ('Null', rootscreen + 900, movieimage, lambda i = movie["movieid"]: xbmc.PlayerPlayMovie(i))
           # Add it to a list
           movie_imgs.append(button)
       
       if 0 < (totalmovies - (menu.page * 8)) < 8:
           for a in range(8 - (totalmovies - (menu.page * 8))):
               button = ("None", rootscreen + 900, emptyimage, None)
               movie_imgs.append(button)
       # Once we've added all the movie thumbs
       # Add home button 
       movie_imgs.append(('Home', 0, None, None))
       # Add a "previous" button if we're not on first page
       if menu.page > 0:
           movie_imgs.append(('Prev', rootscreen + 900, None, lambda m=menu: m.prevPage()))
       # Add "next" button
       # TODO: remove "Next" if on last page
       if menu.page * 8 < (totalmovies - 8):
           movie_imgs.append(('Next', rootscreen + 900, None, lambda m=menu: m.nextPage())) 
           
       if menu.page < maxpages:
           if maxpages - menu.page > 10:
               jump = 10
           else:
               jump = int(maxpages - menu.page)
           
           movie_imgs.append(('+%d' % jump, rootscreen + 900, None, lambda m=menu, j=jump: m.nextPage(j))) 
       # Add the buttons to the menu
       menu.add_buttons(movie_imgs)
       # Return the menu
       return menu

   # Function to do TV Shows menu
   def UpdateTVMenu(menu, rootscreen):
       # There are 3 screens for TV:
       # 101 - TV Shows
       # 102 - Seasons
       # 103 - Episodes
       tv_imgs = []
       menu.menu_items=[]
       # Let's get the movies we need - just 8 records as that's all
       # we can display on one screen

       tvlimits = Limits.LIMITS((menu.page * 8), 8)
       
       # TV SHOWS
       if rootscreen == 101:
           menu.y = 15
           menu.x = 200
           totaltv = xbmc.GetTVShows()["limits"]["total"]
           for tvshow in xbmc.GetTVShows(mylimits=tvlimits, properties=["thumbnail"])['tvshows']:
               # Get the thumbnail
               tvimage = pygame.transform.scale(libraryimages.getMovieThumb(tvshow),(205, 315))
               # Create the button
               button = ('Null', 102, tvimage, lambda tvshowid = tvshow["tvshowid"]: menu.setTVShow(tvshowid))
               # Add it to a list
               tv_imgs.append(button)
                
           
       # SEASONS    
       elif rootscreen == 102:
           menu.y = 15
           menu.x = 200
           totaltv = xbmc.GetTVSeasons(menu.tvshow)["limits"]["total"]
           for tvshow in xbmc.GetTVSeasons(menu.tvshow, mylimits=tvlimits, properties=["thumbnail", "season"])['seasons']:
               # Get the thumbnail
               tvimage = pygame.transform.scale(libraryimages.getMovieThumb(tvshow),(205, 315))
               # Create the button
               button = ('Null', 103, tvimage, lambda tvseason = tvshow["season"]: menu.setTVSeason(tvseason))
               # Add it to a list
               tv_imgs.append(button)
    
       
       # EPISODES
       elif rootscreen == 103:
           menu.y = 15
           menu.x = 75
           thumbsize = tvthumbs[tvthumbsize]["size"]
           episodesort = Sort.SORT(sort=Sort.EPISODE, sortorder = Sort.sortorder.ASCENDING)
           totaltv = len(xbmc.GetTVEpisodes(menu.tvshow, menu.tvseason)["episodes"])
           for tvshow in xbmc.GetTVEpisodes(menu.tvshow, menu.tvseason, mylimits=tvlimits, properties=["thumbnail"], mysort = episodesort)['episodes']:
               # Get the thumbnail
               tvimage = pygame.transform.scale(libraryimages.getMovieThumb(tvshow),(275, 179))
               if tvthumbs[tvthumbsize]["preserveratio"]:
                   thumb = libraryimages.aspect_scale(libraryimages.getMovieThumb(tvshow), thumbsize)
                   yoffset = int((128 - thumb.get_rect()[3]) / 2)
               else:
                   thumb = pygame.transform.scale(libraryimages.getMovieThumb(tvshow),thumbsize)
                   yoffset = 0

               tvimage.blit(thumb, (0, yoffset))
               # Create the button
               button = ('Null', 103, tvimage, lambda i = tvshow["episodeid"]: xbmc.PlayerPlayTVEpisode(i))
               # Add it to a list
               tv_imgs.append(button)
    
       if 0 < (totaltv - (menu.page * 8)) < 8:
           for a in range(8 - (totaltv - (menu.page * 8))):
               button = ("None", rootscreen + 900, pygame.transform.scale(emptyimage, (tvimage.get_rect()[2], tvimage.get_rect()[3])), None)
               tv_imgs.append(button)               

       # Once we've added all the movie thumbs
       # Add home button 
       tv_imgs.append(('Home', 0, None, lambda: menu.ResetPage()))
       
       if rootscreen == 102:
           tv_imgs.append(('Shows', 101, None, lambda: menu.ResetPage()))

       if rootscreen == 103:
           tv_imgs.append(('Seasons', 102, None, lambda: menu.ResetPage()))

                  
       # Add a "previous" button if we're not on first page
       if menu.page > 0:
           tv_imgs.append(('Prev', rootscreen + 900, None, lambda m=menu: m.prevPage()))
       # Add "next" button
       # TODO: remove "Next" if on last page
       if menu.page * 8 < (totaltv - 8):
           tv_imgs.append(('Next', rootscreen + 900, None, lambda m=menu: m.nextPage()))
           

       # Add the buttons to the menu
       menu.add_buttons(tv_imgs)
       # Return the menu
       return menu

   # Function to do music menu
   def UpdateMusicMenu(menu, rootscreen):
       # There are 2 screens for Music:
       # 201 - Artists
       # 202 - Albums

       audio_imgs = []
       menu.menu_items=[]
       # Let's get the movies we need - just 8 records as that's all
       # we can display on one screen

       audiolimits = Limits.LIMITS((menu.page * 8), 8)
       
       # Artists
       if rootscreen == 201:
           totalmusic = xbmc.AudioGetArtists()["limits"]["total"]
           sorting = Sort.SORT(sort="artist", sortorder=Sort.sortorder.ASCENDING)
           for artist in xbmc.AudioGetArtists(mylimits=audiolimits, mysort=sorting, properties=["thumbnail"])['artists']:
               # Get the thumbnail
               artistimage = pygame.transform.scale(libraryimages.getMovieThumb(artist, (256, 256)),(256, 256))
               # Create the button
               button = ('Null', 202, artistimage, lambda artistid = artist["artistid"]: menu.setArtist(artistid))
               # Add it to a list
               audio_imgs.append(button)
                
           
       # ALBUMS   
       elif rootscreen == 202:
           totalmusic = xbmc.AudioGetAlbums(menu.artist)["limits"]["total"]
           sorting = Sort.SORT(sort="album", sortorder=Sort.sortorder.ASCENDING)
           for album in xbmc.AudioGetAlbums(menu.artist, mysort=sorting, mylimits=audiolimits, properties=["thumbnail"])['albums']:
               # Get the thumbnail
               albumimage = pygame.transform.scale(libraryimages.getMovieThumb(album, (256, 256)),(256, 256))
               # Create the button
               button = ('Null', 202, albumimage, lambda i=album["albumid"]: xbmc.PlayerPlayAlbum(i))
               # Add it to a list
               audio_imgs.append(button)
    

    
       if 0 < (totalmusic - (menu.page * 8)) < 8:
           for a in range(8 - (totalmusic - (menu.page * 8))):
               button = ("None", rootscreen + 900, pygame.transform.scale(emptyimage, (256, 256)), None)
               audio_imgs.append(button)               

       # Once we've added all the movie thumbs
       # Add home button 
       audio_imgs.append(('Home', 0, None, lambda: menu.ResetPage()))
       
       if rootscreen == 202:
           audio_imgs.append(('Artists', 201, None, lambda m=menu: m.SavedPage()))
       # Add a "previous" button if we're not on first page
       if menu.page > 0:
           audio_imgs.append(('Prev', rootscreen + 900, None, lambda m=menu: m.prevPage()))
       # Add "next" button
       # TODO: remove "Next" if on last page
       if menu.page * 8 < (totalmusic - 8):
           audio_imgs.append(('Next', rootscreen + 900, None, lambda m=menu: m.nextPage())) 
       # Add the buttons to the menu
       menu.add_buttons(audio_imgs)
       # Return the menu
       return menu
    
   # Uncomment this to center the window on the computer screen
   os.environ['SDL_VIDEO_CENTERED'] = '1'

   # Uncomment this to position the screen x_ and y_ pixels from the top left
   # corner of the monitor/screen
   #x_ = 560
   #y_ = 100
   #if os.name != 'mac':
   #   os.environ['SDL_VIDEO_WINDOW_POS'] = str(x_) + "," + str(y_)

   # initiate class to send JSON requests
   xbmc = SimpleXBMCJSON(host + "jsonrpc")
   
   # Check that XBMC is online
   if not xbmc.Ping():
       print "Can't connect to XBMC. Exiting..."
       sys.exit(1)
   
   # Initiate class to get images from XBMC library    
   libraryimages = xbmcimages(host) 
       
   # Initialize Pygame
   pygame.init()

   # Create a window of 1280x720 pixels
   screen = pygame.display.set_mode((1280, 720))

   # Set the window caption
   pygame.display.set_caption("Touchscreen XBMC Remote")

   # Images to use for background & empty cases for fillers
   bkg = load_image('bkg.jpg', 'images')
   emptyimage = load_image('empty.png', 'images')

   # Set a background image.
   screen.blit(bkg, (0, 0))
   pygame.display.flip()

   # Create 6 different menus.  All of them being a mix of images and text buttons.
   
   # Home menu
   menu0 = cMenu(640, 500, 200, 50, 'horizontal', 3, screen,
                [('3D Movies',     1, None, None),
                 ('HD Movies',     2, None, None),
                 ('TV Shows',      101, None, None),
                 ('  Movies',      4, None, None),
                 ('   Music',      201, None, None),
                 ('     Quit',     9, None, None)])
   
   # 3D Movies
   menu1 = cMenu(200, 15, 10, 10, 'horizontal', 4, screen, [('a',1,None,None)])

   # HD Movies
   menu2 = cMenu(200, 15, 10, 10, 'horizontal', 4, screen, [('a',1,None,None)])

   # TV Shows
   menu3 = cMenu(200, 15, 10, 10, 'horizontal', 4, screen, [('Home', 0, None, None)])

   # SD Movies
   menu4 = cMenu(200, 15, 10, 10, 'horizontal', 4, screen, [('a',1,None,None)])
   
   # Create base music menu
   menu5 = cMenu(113, 79, 10, 10, 'horizontal', 4, screen, [('Home', 0, None, None)])


   # Center Main Menu horizontally on the draw_surface (the entire screen here)
   menu0.set_center(True,False)

   # Create the state variables (make them different so that the user event is
   # triggered at the start of the "while 1" loop so that the initial display
   # does not wait for user input)
   state = 0
   prev_state = 1

   # rect_list is the list of pygame.Rect's that will tell pygame where to
   # update the screen (there is no point in updating the entire screen if only
   # a small portion of it changed!)
   rect_list = []

   # Ignore mouse motion (greatly reduces resources when not needed)
   #pygame.event.set_blocked(pygame.MOUSEMOTION)

   # The main while loop
   while 1:
      # Check if the state has changed, if it has, then post a user event to
      # the queue to force the menu to be shown at least once
      if prev_state != state:
         pygame.event.post(pygame.event.Event(EVENT_CHANGE_STATE, key = 0))
         prev_state = state
         if state > 900:
             prev_state = state = state - 900

            # Reset the screen before going to the next menu.  Also, put a
            # caption at the bottom to tell the user what is going one
         screen.blit(bkg, (0, 0))
            #~ screen.blit(TEXT[state][0], (15, 530))
            #~ screen.blit(TEXT[state][1], (15, 550))
            #~ screen.blit(TEXT[state][2], (15, 570))
         pygame.display.flip()

      # Get the next event
      e = pygame.event.wait()

      # Update the menu, based on which "state" we are in - When using the menu
      # in a more complex program, definitely make the states global variables
      # so that you can refer to them by a name
      if e.type == pygame.KEYDOWN or e.type == EVENT_CHANGE_STATE or e.type == pygame.MOUSEBUTTONDOWN:
         if state == 0:
            rect_list, state = menu0.update(e, state)
         elif state == 1:
            menu1 = UpdateMovieMenu(menu1, 1, menu1folder) 
            rect_list, state = menu1.update(e, state)
         elif state == 2:
            menu2 = UpdateMovieMenu(menu2, 2, menu2folder) 
            rect_list, state = menu2.update(e, state)
         elif state == 101 or state == 102 or state == 103:
            menu3 = UpdateTVMenu(menu3, state) 
            rect_list, state = menu3.update(e, state)
         elif state == 4:
            menu4 = UpdateMovieMenu(menu4, 4, menu4folder)
            rect_list, state = menu4.update(e, state)
         elif state == 201 or state == 202:
            menu5 = UpdateMusicMenu(menu5, state)
            rect_list, state = menu5.update(e, state)
         elif state == 6:
            rect_list, state = menu6.update(e, state)
         else:
            pygame.quit()
            sys.exit()

      # Quit if the user presses the exit button
      if e.type == pygame.QUIT:
         pygame.quit()
         sys.exit()
      if e.type == pygame.KEYDOWN:
         if e.key == pygame.K_ESCAPE:
            pygame.quit()
            sys.exit()

      # Update the screen
      pygame.display.update(rect_list)




   

## ---[ The python script starts here! ]----------------------------------------
# Run the script
if __name__ == "__main__":
   main()


#---[ END OF FILE ]-------------------------------------------------------------
