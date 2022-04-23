import tkinter as tk
import tkinter.font as font
from tkinter import ttk

from .common import common_images
from . import common

class AssetGroup:
    """
        asset tree structure : groups - categories - files
    """
    def __init__(self, asset_group, group_title):
        self.asset_group = asset_group
        self.group_title = group_title

        #print('in class: ', group_title)

class AssetCategory:
    pass


class AssetFile:
    pass


class AssetCopyBtn(ttk.Button):
    """
        
    """

    def __init__(self, parent, asset_group):
        # store tab

        self.parent = parent
        self.asset_group = asset_group
        
        title = self.asset_group.group_title
        width = len(title)*2
        # btn init
        ttk.Button.__init__(self, self.parent, text=title, width=width)

       
        
        