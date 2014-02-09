import urllib
import StringIO
import pygame
import os
import sys

class xbmcimages:
    """class to simplify getting images from xbmc
    for use in pygame.
    """
    def __init__(self, host="http://localhost:8080/", cache = "xbmcimagecache"):
        """Initiate the class.
        
        host = url and port of XBMC
        cache = name of folder to store images
        """
        self.host = host
        
        # Create the directory path for the image cache
        self.cache = os.path.join(os.path.dirname(sys.modules[self.__class__.__module__].__file__), cache)
        
        # if the cache doesn't exist then we need to create it!
        if not os.path.exists(self.cache):
            os.makedirs(self.cache)


### Base methods for getting image from a url and converting to a 
### pygame image

    def __LoadImageFromUrl(self, url, solid = False):
        f = urllib.urlopen(url)
        buf = StringIO.StringIO(f.read())
        image = self.__LoadImage(buf, solid)
        return image
        
    def __LoadImage(self, fileName, solid = False):
        image = pygame.image.load(fileName)
        image = image.convert()
        if not solid:
            colorkey = image.get_at((0,0))
            image.set_colorkey(colorkey, pygame.RLEACCEL)
        return image
        
    def __isCached(self, fileName):
        iscached = False
        if os.path.exists(fileName):
            iscached = True
        return iscached

    def render_textrect(self, string, font, rect, text_color, background_color, 
                        justification=0, vjustification=0, margin=0, shrink = False, 
                        SysFont=None, FontPath=None, MaxFont=0, MinFont=0):
        """Returns a surface containing the passed text string, reformatted
        to fit within the given rect, word-wrapping as necessary. The text
        will be anti-aliased.

        Takes the following arguments:

        string - the text you wish to render. \n begins a new line.
        font - a Font object
        rect - a rectstyle giving the size of the surface requested.
        text_color - a three-byte tuple of the rgb value of the
                     text color. ex (0, 0, 0) = BLACK
        background_color - a three-byte tuple of the rgb value of the surface.
        justification - 0 (default) left-justified
                        1 horizontally centered
                        2 right-justified

        Returns the following values:

        Success - a surface object with the text rendered onto it.
        Failure - raises a TextRectException if the text won't fit onto the surface.
        """
        
        """ Amended by el_Paraguayo:
         - cutoff=True - cuts off text instead of raising error
         - margin=(left,right,top,bottom) or 
         - margin=2 is equal to margin = (2,2,2,2) 
         - shrink=True adds variable font size to fit text
            - Has additional args:
                - SysFont=None - set SysFont to use when shrinking
                - FontPath=none - set custom font path to use when shrinking
                MaxFont=0 (max font size)
                MinFont=0 (min font size)
         - vjustification=0 adds vertical justification
            0 = Top
            1 = Middle
            2 = Bottom
        """
        
        class TextRectException(Exception):
            def __init__(self, message = None):
                self.message = message
            def __str__(self):
                return self.message

        def draw_text_rect(string, font, rect, text_color, background_color, 
                           justification=0, vjustification=0, margin=0, cutoff=True):
                               
            final_lines = []

            requested_lines = string.splitlines()

            # Create a series of lines that will fit on the provided
            # rectangle.

            for requested_line in requested_lines:
                if font.size(requested_line)[0] > (rect.width - (margin[0] + margin[1])):
                    words = requested_line.split(' ')
                    # if any of our words are too long to fit, return.
                    #~ for word in words:
                        #~ if font.size(word)[0] >= (rect.width - (margin * 2)):
                            #~ if not cutoff:
                                #~ raise TextRectException, "The word " + word + " is too long to fit in the rect passed."
                            
                    # Start a new line
                    accumulated_line = ""
                    for word in words:
                        test_line = accumulated_line + word + " "
                        # Build the line while the words fit.    
                        if font.size(test_line.strip())[0] < (rect.width - (margin[0] + margin[1])) :
                            accumulated_line = test_line 
                        else: 
                            if len(accumulated_line.split(" ")) == 1:
                                raise TextRectException, "Too Big"
                            final_lines.append(accumulated_line) 
                            accumulated_line = word + " " 
                    final_lines.append(accumulated_line)
                else: 
                    final_lines.append(requested_line) 

            # Let's try to write the text out on the surface.

            surface = pygame.Surface(rect.size) 
            surface.fill(background_color) 

            accumulated_height = 0 
            for line in final_lines: 
                if accumulated_height + font.size(line)[1] >= (rect.height - margin[2] - margin[3]):
                    if not cutoff:
                        raise TextRectException, "Once word-wrapped, the text string was too tall to fit in the rect."
                    else:
                        break
                if line != "":
                    tempsurface = font.render(line.strip(), 1, text_color)
                    if justification == 0:
                        surface.blit(tempsurface, (0 + margin[0], accumulated_height + margin[2]))
                    elif justification == 1: 
                        surface.blit(tempsurface, ((rect.width - tempsurface.get_width()) / 2, accumulated_height + margin[2]))
                    elif justification == 2:
                        surface.blit(tempsurface, (rect.width - tempsurface.get_width() - margin[1], accumulated_height + margin[2]))
                    else:
                        raise TextRectException, "Invalid justification argument: " + str(justification)
                accumulated_height += font.size(line)[1]

            if vjustification == 0:
                # Top aligned, we're ok
                pass
            elif vjustification == 1:
                # Middle aligned
                tempsurface = pygame.Surface(rect.size)
                tempsurface.fill(background_color)
                vpos = (0, (rect.size[1] - accumulated_height)/2)
                tempsurface.blit(surface, vpos, (0,0,rect.size[0],accumulated_height))
                surface = tempsurface
            elif vjustification == 2:
                # Bottom aligned
                tempsurface = pygame.Surface(rect.size)
                tempsurface.fill(background_color)
                vpos = (0, (rect.size[1] - accumulated_height - margin[3]))
                tempsurface.blit(surface, vpos, (0,0,rect.size[0],accumulated_height))
                surface = tempsurface
            else:
                raise TextRectException, "Invalid vjustification argument: " + str(justification)
            return surface
            
        surface = None
        
        if type(margin) is tuple:
            if not len(margin) == 4:
                try:
                    margin = (int(margin),  int(margin), int(margin), int(margin))
                except:
                    margin = (0,0,0,0)
        elif type(margin) is int:
            margin = (margin, margin, margin, margin)
        else:
            margin = (0,0,0,0)
        
        if not shrink:
            surface = draw_text_rect(string, font, rect, text_color, background_color, 
                                     justification=justification, vjustification=vjustification, 
                                     margin=margin, cutoff=False)
        
        else:
            fontsize = MaxFont
            fit = False
            while fontsize >= MinFont:
                if FontPath is None:
                    myfont = pygame.font.SysFont(SysFont,fontsize)
                else:
                    myfont = pygame.font.Font(FontPath,fontsize)
                try:
                    surface = draw_text_rect(string, myfont, rect,text_color, background_color, 
                                             justification=justification, vjustification=vjustification, 
                                             margin=margin, cutoff=False)
                    fit = True
                    break
                except:
                    fontsize -= 1
            if not fit:
                surface = draw_text_rect(string, myfont, rect, text_color, background_color, 
                                         justification=justification, vjustification=vjustification, 
                                         margin=margin)

        return surface     

    """
    aspect_scale.py - Scaling surfaces keeping their aspect ratio
    Raiser, Frank - Sep 6, 2k++
    crashchaos at gmx.net

    This is a pretty simple and basic function that is a kind of
    enhancement to pygame.transform.scale. It scales a surface
    (using pygame.transform.scale) but keeps the surface's aspect
    ratio intact. So you will not get distorted images after scaling.
    A pretty basic functionality indeed but also a pretty useful one.

    Usage:
    is straightforward.. just create your surface and pass it as
    first parameter. Then pass the width and height of the box to
    which size your surface shall be scaled as a tuple in the second
    parameter. The aspect_scale method will then return you the scaled
    surface (which does not neccessarily have the size of the specified
    box of course)

    Dependency:
    a pygame version supporting pygame.transform (pygame-1.1+)
    """

    def aspect_scale(self, img,(bx,by)):
        """ Scales 'img' to fit into box bx/by.
         This method will retain the original image's aspect ratio """
        ix,iy = img.get_size()
        if ix > iy:
            # fit to width
            scale_factor = bx/float(ix)
            sy = scale_factor * iy
            if sy > by:
                scale_factor = by/float(iy)
                sx = scale_factor * ix
                sy = by
            else:
                sx = bx
        else:
            # fit to height
            scale_factor = by/float(iy)
            sx = scale_factor * ix
            if sx > bx:
                scale_factor = bx/float(ix)
                sx = bx
                sy = scale_factor * iy
            else:
                sy = by

        return pygame.transform.scale(img, (int(sx),int(sy)))

### XBMC specifics
    def getMovieThumb(self, movie, size=(128,190)):
        """getMovieThumb: takes a movie item from the XBMC JSON result
        and returns a pygame image object.
        
        Method checks if file previously loaded and cached. If it doesn't
        exist, image will be saved in cache.
        """
        try:
            im = movie["thumbnail"][:-1]
            #filename = os.path.basename(urllib.unquote(im.split("imgobject.com")[1]).decode('utf8'))
            filename = os.path.basename(urllib.unquote(im).decode('utf8')).replace(" ", "")
            if not filename[-3].lower() == "jpg":
                filename = filename[:-3] + "jpg"
            image = os.path.join(self.cache, filename)
            if self.__isCached(image):
                return pygame.image.load(image)
            else:
                im = urllib.quote_plus(im)
                im = self.host + "image/" + im
                webimage = self.__LoadImageFromUrl(im, True)
                pygame.image.save(webimage, image)
                return webimage
        except:
            solid = pygame.Surface(size)
            movierect = pygame.Rect(0,0,size[0],size[1])
            movietext = self.render_textrect(movie["label"], None, movierect, 
                                            (255,255,255), (0,0,0), 1, shrink=True, 
                                            SysFont="freesans", MaxFont=32, MinFont=4, vjustification=1)
            
            #~ self, string, font, rect, text_color, background_color, 
                        #~ justification=0, vjustification=0, margin=0, shrink = False, 
                        #~ SysFont=None, FontPath=None, MaxFont=0, MinFont=0
            
            solid.blit(movietext,(0,0))
            return solid


