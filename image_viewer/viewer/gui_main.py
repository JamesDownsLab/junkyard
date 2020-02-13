# -*- coding: utf-8 -*-
import os
import tkinter as tk

from tkinter import ttk
from PIL import Image
from tkinter.filedialog import askopenfilename
from tkinter import messagebox
from .gui_imageframe import ImageFrame
from .logic_config import Config
from .logic_logger import logging, handle_exception

class MainGUI(ttk.Frame):
    """ GUI of Image Viewer """
    def __init__(self, mainframe, image):
        """ Initialize the Frame """
        logging.info('Open GUI')
        self.image = image
        ttk.Frame.__init__(self, master=mainframe)
        self.__create_instances()
        self.__create_main_window()
        self.__create_widgets()
        self.__open_image(image)

    def __create_instances(self):
        """ Instances for GUI are created here """
        self.__config = Config()  # open config file of the main window
        self.__imframe = None  # empty instance of image frame (canvas)

    def __create_main_window(self):
        """ Create main window GUI"""
        self.__default_title = 'Image Viewer'
        self.master.title(self.__default_title)
        self.master.geometry(self.__config.get_win_geometry())  # get window size/position from config
        self.master.wm_state(self.__config.get_win_state())  # get window state
        # self.destructor gets fired when the window is destroyed
        self.master.protocol('WM_DELETE_WINDOW', self.destroy)
        #
        # Add menubar to the main window BEFORE iconbitmap command. Otherwise it will shrink
        # in height by 20 pixels after each opening of the window.
        #
        self.__is_fullscreen = False  # enable / disable fullscreen mode
        self.__bugfix = False  # BUG! when change: fullscreen --> zoomed --> normal
        self.__previous_state = 0  # previous state of the event
        # List of shortcuts in the following format: [name, keycode, function]
        # Bind events to the main window
        self.master.bind('<Motion>', self.__motion)  # track and handle mouse pointer position
        self.master.bind('<F11>', self.__fullscreen_toggle)  # toggle fullscreen mode
        self.master.bind('<Escape>', lambda e=None, s=False: self.__fullscreen_toggle(e, s))
        self.master.bind('<F5>', self.__default_geometry)  # reset default window geometry
        # Handle main window resizing in the idle mode, because consecutive keystrokes <F11> - <F5>
        # don't set default geometry from full screen if resizing is not postponed.
        self.master.bind('<Configure>', lambda event: self.master.after_idle(
            self.__resize_master, event))  # window is resized
        # Handle keystrokes in the idle mode, because program slows down on a weak computers,
        # when too many key stroke events in the same time.
        self.master.bind('<Key>', lambda event: self.master.after_idle(self.__keystroke, event))

    def __fullscreen_toggle(self, event=None, state=None):
        """ Enable/disable the fullscreen mode """
        if state is not None:
            self.__is_fullscreen = state
        else:
            self.__is_fullscreen = not self.__is_fullscreen  # toggling the boolean
        # Hide menubar in fullscreen mode or show it otherwise
        self.master.wm_attributes('-fullscreen', self.__is_fullscreen)  # fullscreen mode on/off

    def __motion(self, event):
        """ Track mouse pointer and handle its position """
        if self.__is_fullscreen:
            y = self.master.winfo_pointery()

    def __keystroke(self, event):
        """ Language independent handle events from the keyboard
            Link1: http://infohost.nmt.edu/tcc/help/pubs/tkinter/web/key-names.html
            Link2: http://infohost.nmt.edu/tcc/help/pubs/tkinter/web/event-handlers.html """
        #print(event.keycode, event.keysym, event.state)  # uncomment it for debug purposes
        if event.state - self.__previous_state == 4:  # check if <Control> key is pressed
            for shortcut in self.__shortcuts:
                if event.keycode == shortcut[1]:
                    shortcut[2]()
        else:  # remember previous state of the event
            self.__previous_state = event.state

    def __default_geometry(self, event=None):
        """ Reset default geomentry for the main GUI window """
        self.__fullscreen_toggle(state=False)  # exit from fullscreen
        self.master.wm_state(self.__config.default_state)  # exit from zoomed
        self.__config.set_win_geometry(self.__config.default_geometry)  # save default to config
        self.master.geometry(self.__config.default_geometry)  # set default geometry

    def __resize_master(self, event=None):
        """ Save main window size and position into config file.
            There is a bug when changing window from fullscreen to zoomed and then to normal mode.
            Main window somehow remembers zoomed mode as normal, so I have to explicitly set
            previous geometry from config INI file to the main window. """
        if self.master.wm_attributes('-fullscreen'):  # don't remember fullscreen
            self.__bugfix = True  # fixing bug
            return
        if self.master.state() == 'normal':
            if self.__bugfix is True:  # fixing bug for: fullscreen --> zoomed --> normal
                self.__bugfix = False
                # Explicitly set previous geometry to fix the bug
                self.master.geometry(self.__config.get_win_geometry())
                return
            self.__config.set_win_geometry(self.master.winfo_geometry())
        self.__config.set_win_state(self.master.wm_state())

    def __create_widgets(self):
        """ Widgets for GUI are created here """
        # Create placeholder frame for the image
        self.master.rowconfigure(0, weight=1)  # make grid cell expandable
        self.master.columnconfigure(0, weight=1)
        self.__placeholder = ttk.Frame(self.master)
        self.__placeholder.grid(row=0, column=0, sticky='nswe')
        self.__placeholder.rowconfigure(0, weight=1)  # make grid cell expandable
        self.__placeholder.columnconfigure(0, weight=1)

    def __set_image(self, image):
        """ Close previous image and set a new one """
        self.__close_image()  # close previous image
        self.__imframe = ImageFrame(placeholder=self.__placeholder, image=image,
                                    roi_size=self.__config.get_roi_size())
        # self.master.title(self.__default_title + ': {}'.format(path))  # change window title
        # self.__config.set_recent_path(path)  # save image path into config

    @handle_exception(0)
    def __open_image(self, image):
        self.__set_image(image)

    def __close_image(self):
        """ Close image """
        if self.__imframe:
            self.__imframe.destroy()
            self.__imframe = None
            self.master.title(self.__default_title)  # set default window title
            # Disable 'Close image' submenu of the 'File' menu

    def destroy(self):
        """ Destroy the main frame object and release all resources """
        self.__close_image()
        self.__config.destroy()
        logging.info('Close GUI')
        self.quit()
