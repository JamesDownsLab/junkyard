# -*- coding: utf-8 -*-
import os
import tkinter as tk

from image_viewer.viewer.logic_logger import init_logging, logging
from image_viewer.viewer.gui_main import MainGUI

from PIL import Image

if __name__ == '__main__':
    init_logging()
    logging.info('Start software')
    this_dir = os.path.dirname(os.path.realpath(__file__))  # path to this directory
    os.chdir(this_dir)  # make path to this dir the current path
    image = Image.open("/home/ppxjd3/Pictures/Screenshot from 2020-01-22 14-38-32.png")

    root = tk.Tk()
    app = MainGUI(root, image)
    root.mainloop()
    logging.info('Finish software')
