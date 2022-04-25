import tkinter as tk
import tkinter.font as font
from tkinter import ttk
from collections import OrderedDict
from pathlib import Path
import os
import json
from PIL import Image, ImageTk

from thonny import get_workbench
from thonny.ui_utils import show_dialog, CommonDialog


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

    def __init__(self, parent, group_obj):
        # store tab

        self.parent = parent
        self.group_obj = group_obj
        
        title = self.group_obj.group_title
        width = len(title)*2
        # btn init
        ttk.Button.__init__(self, self.parent, text=title, width=width, command=self.open_asset_dialog)

    def open_asset_dialog(self):
        show_dialog(AssetDialog(get_workbench(), self.group_obj))


class AssetDialog(CommonDialog):
    def __init__(self, master, group_obj):
        super().__init__(master)
        self.group_obj = group_obj

        main_frame = ttk.Frame(self)
        main_frame.grid(sticky=tk.NSEW, padx=15, pady=15)
        main_frame.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)

        self.title(self.group_obj.group_title)
        self.resizable(height=tk.FALSE, width=tk.FALSE)
        self.protocol("WM_DELETE_WINDOW", self._ok)

        # title
        text_font = common.dialog_title_font
        content = self.group_obj.group_title         
        head_label = ttk.Label(
            main_frame, text=content, font=text_font
        )
        head_label.pack(pady=15)

        #### combo_frame
        combo_frame = ttk.Frame(main_frame)
        combo_frame.pack(anchor=tk.W, padx=0, pady=15) 

        category_label = ttk.Label(combo_frame, text='類別：')
        category_label.pack(side=tk.LEFT)

        # category combobox
        self.asset_category_list = []
        category_title_list = []

        for key, obj in group_obj.categories.items():
            self.asset_category_list.append(key)
            category_title_list.append(obj.category_title)

        self.categories_combo = ttk.Combobox(combo_frame,
                                    values=category_title_list,
                                    state='readonly',)
        self.categories_combo.bind('<<ComboboxSelected>>', self.on_combo_select)
        self.categories_combo.current(0)

        self.categories_combo.pack(side=tk.LEFT)



        #### frame for file_view

        file_view_frame = ttk.Frame(main_frame)
        file_view_frame.pack()
        # file tree view

        s = ttk.Style()
        s.configure('Treeview', rowheight=80,
                     font=('Consolas', 10),
                     background='#f0f8ff')
        # s2 = ttk.Style()
        # s2.configure('Treeview.Heading', background="#66b5ff")

        self.file_view = ttk.Treeview(file_view_frame, 
                                columns=(1, 2, 3),
                                selectmode='extended', 
                                takefocus=False ,
                                height=4)
                               
        self.file_view.column(1, anchor='center')
        self.file_view.column(2, anchor='center')
        self.file_view.column(3, anchor='center')


        self.file_view.heading(1, text="檔名")
        self.file_view.heading(2, text="類型")
        self.file_view.heading(3, text="詳細資料")
        
        self.file_view.pack(side=tk.LEFT)

        self.scroll_bar = tk.Scrollbar(file_view_frame, orient=tk.VERTICAL)
        self.scroll_bar.pack(side=tk.RIGHT, fill=tk.Y)

        self.file_view.config(yscrollcommand=self.scroll_bar.set)
        self.scroll_bar.config(command=self.file_view.yview)

        # load files in 1st category
        self.on_combo_select()

        #### frame for destination
        destination_frame = ttk.Frame(main_frame)
        destination_frame.pack( pady=20) 

        # determine cwd 
        notebook = get_workbench().get_editor_notebook()
        cwd = get_workbench().get_local_cwd()
        if (
            notebook.get_current_editor() is not None
            and notebook.get_current_editor().get_filename() is not None
        ):
            cwd = os.path.dirname(notebook.get_current_editor().get_filename())
        self.cwd = cwd
        font = common.dialog_font
        category_label = ttk.Label(destination_frame, text='目的地： ' + self.cwd + '  ', font=font)
        category_label.pack(side=tk.LEFT)

        # button
        self.copy_button = ttk.Button(destination_frame, 
                                    text=" 複製「檔案及檔名」", 
                                    width=20 ,
                                    )
        self.copy_button.pack(side=tk.LEFT) 

    def on_combo_select(self, event=None):
        # delete all element
        for iid in self.file_view.get_children():
            self.file_view.delete(iid)

        # insert files according to category
        index = self.categories_combo.current()
        category = self.asset_category_list[index]

        category_obj = self.group_obj.categories[category]
        for i, f_obj in enumerate(category_obj.files.values()):

            if f_obj.file_type in ('jpg', 'png'):
                file_type = f_obj.file_type + ' 圖片'
            elif f_obj.file_type in ('mp4', ):
                file_type = f_obj.file_type + ' 影片'
            else:
                file_type = f_obj.file_type

            info_values = (f_obj.file_title, file_type,
                            f_obj.file_info)
            self.file_view.insert(parent='',
                                  index=i,
                                  iid=f_obj.asset_file,
                                  image=f_obj.thumbnail_img,
                                  values=info_values,
                                  )
            #print(asset_file_obj.file_title)

        self.file_view.yview_moveto('0.0')


    def _ok(self, event=None):
        self.destroy()
        
        