import tkinter as tk
import tkinter.font as font
from tkinter import ttk

from .common import common_images
from . import common

class AssetCopyBtn(ttk.Button):

    def init(self, tab_name, group_name):
        # store tab
        self.tab_name = tab_name
        self.tab = common.postit_tabs[tab_name]

        # frame init
        ttk.Button.__init__(self, self.tab.frame, text='檔案複製')

       
        
        