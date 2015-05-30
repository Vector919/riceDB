"""Defines the Render class."""

import ast
import curses
import getpass
import os
import sys

from . import query, w3m, util

# python 2 compatibility shim
try:
    import urllib.request as request
except ImportError:
    import urllib as request

SEARCHBAR_OFFSET = 2
SEARCHLEFT_OFFSET = 8


class Renderer(object):
    """
    Manages display for the terminal UI
    """
    def __init__(self, w3m_binary='/usr/lib/w3m/w3mimgdisplay'):

        self.results = None
        self.first_pic = True
        self.w3m_enabled = False

        if os.path.exists(w3m_binary):
            self.w3m = w3m.W3MImage_display(w3m_binary)
            self.w3m_enabled = True

    def handle_scroll(self):
        k = self.scr.getkey()
        self.end()
        print(k)
        exit()

    def loop(self):
        if self.index == -1:
            try:
                self.textarea.erase()
                query_string = self.text.edit().strip()
                if query_string == "exit":
                    self.end()
                    return 1
                results = query.Query(query_string).get_results()
                self.populate(results)
            except Exception as e:
                print(e)
        else:
            self.handle_scroll()
        return 0

    # This will draw into a box defined by the passed in parameters
    def draw_image(self, temp_file, x, y, w, h, re=False):
        # Font dimensions
        fw, fh = util.get_font_dimensions()
        # Image dimensions
        iw, ih = util.get_image_dimensions(temp_file)
        # Box dimensions
        bw, bh = w * fw, h * fh
        
        # Scale the image to the box
        if iw > ih:
          scale = 1.0 * bw / iw
        else:
          scale = 1.0 * bh / ih
        iw = scale * iw
        ih = scale * ih

        # Get margin
        x_m = (bw - iw) / 2
        y_m = (bh - ih) / 2

        # Get x, y coordinates
        x = x * fw + x_m
        y = y * fh + y_m
        #self.w3m.clear(x, y, w=iw, h=ih)
        if self.first_pic:
          self.w3m.draw(temp_file, 1, x, y, w=iw, h=ih)
        else:
          self.w3m.redraw(temp_file, 1, x, y, w=iw, h=ih)

    def populate(self, results):
        if not self.results == None:
          del self.results
        self.results = curses.newpad(max(len(results), curses.LINES - 1), curses.COLS//2)
        self.results.clear()
        for i in range(curses.LINES - SEARCHBAR_OFFSET):
          self.results.insch(i, curses.COLS//2 - 2, curses.ACS_VLINE)
        i = 0
        for result in results:
          # print(result)
          self.results.addstr(i, 0, result.name)
          if (not result.images == None) and (self.w3m_enabled):
            try:
                images_array = ast.literal_eval(result.images) 
                temp_file = util.RDBDIR + 'tmp'
                #os.remove(temp_file)
                # print(result.images[0])
                request.urlretrieve(images_array[0], temp_file)
                self.draw_image(temp_file, curses.COLS - curses.COLS/2, SEARCHBAR_OFFSET, curses.COLS/2, curses.LINES - SEARCHBAR_OFFSET)
                if self.first_pic:
                  self.first_pic = False
            except Exception as e:
                # Who cares? it's just a picture.
                self.end()
                print(str(e))
                pass
          i += 1

        self.results.noutrefresh(0, 0, SEARCHBAR_OFFSET, 0, curses.LINES-1, curses.COLS-1)

    def alert(self, message):
        print(message)

    def prompt(self, message):
        print(message)
        return sys.stdin.readline()

    def get_pass(self, message):
        return getpass.getpass(message)

    def pick_packs(self, pack_list):
        """
        View for user to select a package from a list of options
        """
        counter = 1
        if len(pack_list) == 0:
            print("Nothing was found for your specified rice, please try again")
            exit()
        for pack in pack_list:
            print(str(counter) +" " + str(pack.program) + "/" + str(pack.name) + " " + str(pack.version))
            print(str(pack.description) + "\n")
            counter+=1
        print("--------------------------------------------")
        print("Please select the rice you'd like to install")
        choice = input()
        if choice or choice == "q":
            exit()
        else:
                try:
                    choice = int(choice)

                except ValueError:
                    self.alert("That's not a valid number")
                    exit()
        choice-=1
        while choice < 0 or choice > counter:
            print('That is not a valid choice, please try again')
            choice = input()
        return pack_list[choice]

    def end(self):
        self.scr.clear()
        curses.nocbreak()
        self.scr.keypad(False)
        curses.echo()
        curses.endwin()
