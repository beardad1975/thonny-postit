import tkinter as tk
import tkinter.font as font
from tkinter import ttk
from collections import OrderedDict
from pathlib import Path
import json
from PIL import Image, ImageTk

from .common import common_images
from . import common

class AssetGroup:
    """
        asset tree structure : groups - categories - files
    """
    def __init__(self, asset_group, group_title):
        self.asset_group = asset_group
        self.group_title = group_title

        #load asset cetegories
        self.categories = OrderedDict()

        categories_path = Path(__file__).parent / 'assets' / asset_group
        
        with open(categories_path / 'categories_info.json', encoding='utf8') as fp:
            categories_info = json.load(fp)
        
        for c in categories_info:
            asset_category = c['asset_category']
            category_title = c['category_title']
            self.categories[asset_category] = AssetCategory(asset_group,
                                                        asset_category, category_title)

        #print('categories: ', self.categories)

class AssetCategory:
    def __init__(self, asset_group, asset_category, category_title):
        self.asset_group = asset_group
        self.asset_category = asset_category
        self.category_title = category_title

        #load asset cetegories
        self.files = OrderedDict()

        files_path = Path(__file__).parent / 'assets' / asset_group / asset_category
        
        with open(files_path / 'files_info.json', encoding='utf8') as fp:
            files_info = json.load(fp)
        
        for f in files_info:
            asset_file = f['asset_file']
            thumbnail = f['thumbnail']
            file_title = f['file_title']
            file_type = f['file_type']
            file_info = f['file_info']

            self.files[asset_file] = AssetFile(asset_group, asset_category, 
                                            asset_file, thumbnail, file_title,
                                            file_type, file_info)
        #print('files: ', self.files)

class AssetFile:
    def __init__(self, asset_group, asset_category, asset_file, 
                thumbnail, file_title, file_type, file_info):
        self.asset_group = asset_group
        self.asset_category = asset_category
        self.asset_file = asset_file
        self.thumbnail = thumbnail
        self.file_title = file_title
        self.file_type = file_type
        self.file_info = file_info

        # load thumbnail image
        thumbnail_path = Path(__file__).parent / 'assets' / asset_group / asset_category /  thumbnail
        _im = Image.open(thumbnail_path)       
        self.thumbnail_img = ImageTk.PhotoImage(_im)


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

       
        
        