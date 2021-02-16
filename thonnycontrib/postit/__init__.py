import os 
import datetime
import webbrowser
from pathlib import Path
import json
from collections import OrderedDict

import tkinter as tk
import tkinter.font as font
from tkinter import messagebox
from tkinter import ttk
from pathlib import Path
from PIL import Image, ImageTk

from thonny import get_workbench, get_shell, get_runner

from thonny.ui_utils import show_dialog, CommonDialog
from thonny.common import ToplevelCommand

from .base_postit import BasePostit
from .enclosed_postit import EnclosedPostit
from .dropdown_postit import DropdownPostit
from .common import ( CodeNTuple, common_images, TAB_DATA_PATH
                     )
from . import common


from .tools.enter_tool_postit import EnterToolPostit
from .tools.backspace_tool_postit import BackspaceToolPostit
from .tools.undo_tool_postit import UndoToolPostit, RedoToolPostit
from .tools.indenxt_tool_postit import IndentToolPostit, DedentToolPostit
from .tools.comment_tool_postit import CommentToolPostit
from .tools.pilcrow_tool_postit import PilcrowToolPostit
from .tools.variables_tool_postit import ( VariableMenuPostit,
        VariableAddToolPostit, VariableFetchToolPostit)
from .tools.copy_tool_postit import ( CopyToolPostit, PasteToolPostit,
        CutToolPostit )     
from .tools.symbol_tool_postit import SymbolToolPostit




#for test
from tkinter.messagebox import showinfo

#  tab data level
#  Mode(contain notebook) ----> TabGoup ----> Tab 
#       

class Mode:
    def __init__(self, mode_name, mode_label, has_more_tab):
        self.mode_name = mode_name
        self.mode_label = mode_label
        self.has_more_tab = has_more_tab
        self.groups = OrderedDict()



        #collect  tab group
        #print(TAB_DATA_PATH)
        #print(mode_name)
        with open(TAB_DATA_PATH / mode_name / 'groups_info.json') as fp:
            groups_info = json.load(fp)
        #print(info_data)

        for g in groups_info:
            group_name = g['group_name']
            group_label = g['group_label']
            group_path =  TAB_DATA_PATH / mode_name / g['group_name']
            self.groups[group_name] = TabGroup(group_name, mode_name, group_label, group_path)

    def gui_init(self):
        # make notebook
        self.notebook_frame = ttk.Frame(common.postit_view)
        self.notebook_frame.pack(side=tk.TOP, fill=tk.Y)
        #self.notebook_frame.pack(side=tk.TOP, fill=tk.Y)
        #style = ttk.Style(self.interior)
        #style = ttk.Style(notebook_frame.interior)
        style = ttk.Style(self.notebook_frame)
        style.configure('lefttab.TNotebook', tabposition='wn')
        #self.notebook = ttk.Notebook(self.interior, style='lefttab.TNotebook')
        #self.notebook = ttk.Notebook(notebook_frame.interior, style='lefttab.TNotebook')
        self.tab_notebook = ttk.Notebook(self.notebook_frame, style='lefttab.TNotebook')
        self.tab_notebook.pack(side='top',fill=tk.Y)

        #notebook event (keep cursor intact in editor)
        self.tab_notebook.bind('<<NotebookTabChanged>>',common.postit_view.on_tab_changed)
        self.tab_notebook.bind('<Button-1>',common.postit_view.on_tab_click)

    def add_more_tab(self):
        if self.has_more_tab:
            self.more_tab = MoreTab(self.tab_notebook)
        else:
            self.more_tab = None

class TabGroup:
    def __init__(self, group_name, mode_name, group_label, group_path):
        self.group_name = group_name
        self.mode_name = mode_name
        self.group_label = group_label
        self.group_path = group_path

        # 3 lists are the same size, all use circular_index
        self.fill_colors = []
        self.font_colors = []
        self.icon_images = []
        self.circular_index = 0

        # all tab data in order
        self.tabs = OrderedDict()

        # init action
        self.collect_icon_color()
        self.color_num = len(self.fill_colors)

        # collect tabs info
        with open(self.group_path / 'tabs_info.json') as fp:
            tabs_info = json.load(fp)
        #print(tabs_info)

        for t in tabs_info:
            tab_name = t['tab_name']
            tab_label = t['tab_label']
            #always_show = t['always_visible']
            tab_path = self.group_path / (tab_name+'.json')
            self.tabs[tab_name] = Tab(tab_name, group_name, mode_name, tab_label,  tab_path, self)

    def gui_init(self):
        # dummy
        pass    

    def collect_icon_color(self):
        icon_path = self.group_path / 'icons'
        with open(icon_path / 'icons_info.json') as fp:
            icons_info = json.load(fp)
        #print(icons_info)

        for i in icons_info:
            icon_filename = i['icon_filename']
            fill_color = i['fill_color']
            font_color = i['font_color']

            im = Image.open(icon_path / icon_filename)       
            self.icon_images.append(ImageTk.PhotoImage(im)) 
            self.fill_colors.append(fill_color)
            self.font_colors.append(font_color)       

    def next_icon_color(self):
        icon_image =  self.icon_images[self.circular_index]
        fill_color = self.fill_colors[self.circular_index]
        font_color = self.font_colors[self.circular_index]

        self.circular_index += 1
        if self.circular_index >= self.color_num:
            self.circular_index = 0
        return icon_image, fill_color, font_color


class Tab:
    def __init__(self, tab_name, group_name, mode_name, tab_label, tab_path, tab_group):
        self.tab_name = tab_name
        self.group_name = group_name
        self.mode_name = mode_name
        self.tab_label = tab_label
        #self.always_show = always_show
        self.tab_path = tab_path
        self.tab_group = tab_group

        #print('mode name:', mode_name, 'group name:', group_name)



        # #pick a color
        # color = self.pick_color()
        # self.fill_color = color['fill_color']
        # self.font_color = color['font_color']

        # #load image
        # if tab_type == 'more':
        #     abs_image_path =Path(__file__).parent/'images'/ 'more.png'
        # else:
        #     abs_image_path =Path(__file__).parent/'images'/color[tab_type+'_filename']
        # im = Image.open(abs_image_path)       
        # self.image = ImageTk.PhotoImage(im) 

    def gui_init(self):
        mode = common.postit_view.all_modes[self.mode_name]
        group = mode.groups[self.group_name]
        self.icon_image, self.fill_color, self.font_color =  group.next_icon_color()
        self.loaded = False
        self.visible = False

        # insert empty frame and hide
        
        self.tab_frame = CustomVerticallyScrollableFrame(mode.notebook_frame)
        mode.tab_notebook.insert('end',self.tab_frame,
                          text = self.tab_label,
                          image = self.icon_image,
                          compound="top",
                        )
        mode.tab_notebook.hide(self.tab_frame)

    def popup_init(self, example_vars):
        self.example_vars = example_vars
        self.popup_menu = tk.Menu(self.frame, tearoff=0)

        self.popup_menu.add_command(label="範例變數匯入",
            command=self.import_example_vars)

        self.frame.bind("<Button-3>", self.popup)


    def import_example_vars(self):
        s = '【匯入變數名稱】\n'
        for i in self.example_vars:
            s = s + i + '\n'
        s += '\n'

        ans = messagebox.askokcancel('範例變數匯入',s)
        #print(ans)
        if ans: # import vars into vars_menu
            vars_counter = common.share_vars_postit.vars_counter

            for var in self.example_vars:
                if var not in vars_counter:
                    vars_counter[var] = 1
            common.share_vars_postit.update_vars_menu()            
        else: # no
            return

    def popup(self, event):
        #if self.tool_name != 'variable_get':
        self.popup_menu.tk_popup(event.x_root, event.y_root)

    # @classmethod
    # def pick_color(cls):
    #     c = cls.color_data[cls.color_circular_index]
    #     cls.color_circular_index += 1
    #     if cls.color_circular_index >= cls.color_num:
    #         cls.color_circular_index = 0
    #     return c


class MoreTab:
    def __init__(self, notebook):
        im = Image.open(Path(__file__).parent / 'images' / 'more.png')       
        self.icon_image = ImageTk.PhotoImage(im) 

        # prepare  frame
        
        self.tab_frame = CustomVerticallyScrollableFrame(notebook)
        notebook.insert('end',self.tab_frame,
                          text = ' 　　 ',
                          image = self.icon_image,
                          compound=tk.CENTER,
                          padding='0i',
                        )

class PythonPostitView(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)

        common.postit_view = self 
        self.last_focus = None
        self.symbol_row_index = 0
        
        self.toolbar_init()
        
        self.current_mode = 'py4t'
        self.last_backend = ''
        get_workbench().bind("BackendRestart", self.switch_mode_by_backend, True)

        self.bind_all("<MouseWheel>", self.on_mousewheel,"+")

        # data structure of all modes, groups and tabs
        self.all_modes = OrderedDict()
        self.all_modes_init()

        

        #self.tab_groups_init()
        
        
        self.show_tab('py4t','builtin', 'data')
        self.show_tab('py4t','builtin', 'flow')
        self.show_tab('py4t','builtin', 'io')
        #self.show_tab('py4t','builtin', 'function')
        #self.show_tab('py4t','builtin', 'exception')
        #self.show_tab('py4t','builtin', 'oo')
        self.show_tab('py4t','eventloop', 'turtle4t')
        self.show_tab('py4t','eventloop', 'physics4t')
        self.show_tab('py4t','eventloop', 'threed4t')
        self.show_tab('bit','microbit', 'main')
        

        self.switch_mode_by_backend()
        frame = self.all_modes['py4t'].groups['eventloop'].tabs['physics4t'].tab_frame
        self.all_modes['py4t'].tab_notebook.select(frame)
        self.all_modes['bit'].tab_notebook.select(0)


        #self.add_tab_json('data')
        #self.add_tab_json('flow')
        #self.add_tab_json('io')

        # #add notebook tabs
        # self.add_tab('common', ' 基本 ','basic')
        # self.add_tab('data', ' 資料 ','basic')
        # self.add_tab('flow', ' 流程 ','basic')
        # self.add_tab('builtin', '程式庫','basic')
        # self.add_tab('turtle4t', ' 海龜 ','pack')
        # self.add_tab('physics', ' 物理 ','pack')
        # self.add_tab('threed', '  3D  ','pack')
        # self.add_tab('auto', ' 自動 ','pack')
        # self.add_tab('numpy', ' 陣列 ','pack')        
        # self.add_tab('cv', ' 視覺 ','pack')
        # self.add_tab('speech', ' 語音 ','pack')
        # self.add_tab('more',' 　　 ','more')

        # self.common_tab_init()
        # self.data_tab_init()
        # self.flow_tab_init()
        # self.builtin_tab_init()
        # self.turtle4t_tab_init()
        # self.physics_tab_init()
        # self.threed_tab_init()
        # self.auto_tab_init()
        # self.numpy_tab_init()
        # self.cv_tab_init()
        # self.speech_tab_init()

    def on_mousewheel(self, event):
        tab_notebook = self.all_modes[self.current_mode].tab_notebook
        tab_name = tab_notebook.select()
        if tab_name:
            tab = tab_notebook.nametowidget(tab_name)
            #print(type(tab),tab)
            tab._on_mousewheel(event)
        

    def switch_mode_by_backend(self, event=None):
        backend_in_option = get_workbench().get_option("run.backend_name")

        if backend_in_option == self.last_backend:
            # backend not changed, no need to switch
            #print('no need to switch mode')
            return
        else:
            # backend has changed, check which mode to switch
            #self.all_modes['bit'].notebook_frame.pack(expand=False)
            #self.all_modes['bit'].tab_notebook.pack(expand=False)
            #self.all_modes['py4t'].notebook_frame.pack(expand=False)
            #self.all_modes['py4t'].tab_notebook.pack(expand=False)
            if backend_in_option == 'microbit':
                
                #self.all_modes['bit'].tab_notebook.pack()
                self.all_modes['py4t'].notebook_frame.pack_forget()
                self.all_modes['py4t'].tab_notebook.pack_forget()
                #self.all_modes['py4t'].notebook_frame.config(expand=False)
                self.all_modes['bit'].notebook_frame.pack(side=tk.TOP, fill=tk.Y,expand=True)
                self.all_modes['bit'].tab_notebook.pack(side=tk.TOP, fill=tk.Y,expand=True)
                #self.all_modes['bit'].notebook_frame.config(expand=True)
                #self.all_modes['py4t'].tab_notebook.pack_forget()
                self.current_mode = 'bit'
            else:
                
                #self.all_modes['py4t'].tab_notebook.pack()   
                self.all_modes['bit'].notebook_frame.pack_forget()
                self.all_modes['bit'].tab_notebook.pack_forget()
                #self.all_modes['bit'].notebook_frame.config(expand=False)
                self.all_modes['py4t'].notebook_frame.pack(side=tk.TOP, fill=tk.Y,expand=True)
                self.all_modes['py4t'].tab_notebook.pack(side=tk.TOP, fill=tk.Y,expand=True)
                #self.all_modes['py4t'].notebook_frame.config(expand=True)
                #self.all_modes['bit'].tab_notebook.pack_forget()
                self.current_mode = 'py4t'              

            self.last_backend = backend_in_option

    def all_modes_init(self):        

        # # collect modes data , one notebook per mode
        # with open(TAB_DATA_PATH / 'modes_info.json') as fp:
        #     modes_info = json.load(fp) 
        # #print('modes info:' , modes_info)

        # # collect data first
        # for m in modes_info:
        #     mode_name = m['mode_name']
        #     mode_label =  m['mode_label']
        #     has_more_tab = m['has_more_tab'] 
        #     self.all_modes[mode_name] = Mode(mode_name, mode_label, has_more_tab)    

        self.all_modes['py4t'] = Mode('py4t', 'python學習模式', has_more_tab=True)
        self.all_modes['bit'] = Mode('bit', 'microbit模式', has_more_tab=False)


        # gui init second
        for mode in self.all_modes.values():
            mode.gui_init()
            for group in mode.groups.values():
                group.gui_init()
                for tab in group.tabs.values():
                    tab.gui_init()
            mode.add_more_tab()



        # notebook menu
        
        #self.tab_menu = tk.Menu(self.notebook, tearoff=0)
        #self.tab_menu.add_command(label='【便利貼】')
        #self.tab_menu.add_separator()
        #self.option = tk.BooleanVar()
        #self.option.set(True)
        #self.tab_menu.add_checkbutton(label="選項", onvalue=1, offvalue=0, 
        #        variable=self.option,
        #        command=lambda:self.remove_tab('flow'),
        #        )
        #
        #self.notebook.bind("<Button-3>", self.tab_menu_popup)

    # def tab_groups_init(self):
        
    #     #python tab group
    #     with open(PY_TAB_PATH / 'groups_info.json') as fp:
    #         groups_info = json.load(fp)
    #     #print(info_data)

    #     for g in groups_info:
    #         group_name = g['group_name']
    #         group_label = g['group_label']
    #         group_path =  PY_TAB_PATH / g['group_name']
    #         self.py4t_tab_groups[group_name] = TabGroup(group_label, group_path)

    def show_tab(self, mode_name, group_name, tab_name):
        mode = self.all_modes[mode_name]
        tab = mode.groups[group_name].tabs[tab_name]
        if not tab.visible:
            mode.tab_notebook.add(tab.tab_frame)
            if not tab.loaded:
                self.load_tab_json(mode_name, group_name, tab_name)
                tab.loaded = True
            tab.visible = True

    def load_tab_json(self, mode_name, group_name, tab_name):
        mode = self.all_modes[mode_name]
        tab = mode.groups[group_name].tabs[tab_name]
        with open(tab.tab_path) as fp:
            postit_list = json.load(fp)
        
        # if name in common.postit_tabs:
        #     print('tab', name, ' already exists')
        #     return

        # tab = PostitTab(name, tab_data['label'], tab_data['type'])
        # common.postit_tabs[name] = tab

        # tab.frame = CustomVerticallyScrollableFrame(self.notebook)
        # self.notebook.insert('end',tab.frame,
        #                   text = tab.label,
        #                   image = tab.image,
        #                   compound="top",
        #                 )

        # parse json data
        label_font = font.Font(size=11, weight=font.NORMAL, family='Consolas')

        for p in postit_list:
            if p['postit_type'] == 'dropdown_postit':
                temp_code_list = []
                for i in p["items"]:
                    temp_code_list.append(CodeNTuple(
                        menu_display=i['menu_display'],
                        code=i['code'],
                        code_display=i['code_display'],
                        note=i['note'],
                        long_note=i['long_note'] ))

                DropdownPostit(tab=tab, code_list = temp_code_list,
                    postfix_enter=p['postfix_enter']).pack(side=tk.TOP, anchor='w', padx=5, pady=8)    

            elif p['postit_type'] == 'ttk_label':
                ttk.Label(tab.tab_frame.interior, 
                    #text='='*6 +' 【 條件分支 】 '+'='*6,
                    text=p['text'],
                    font=label_font,    
                    compound=tk.LEFT, 
                ).pack(side=tk.TOP, padx=5, pady=8, anchor='w')

            elif p['postit_type'] == 'ttk_separator':
                ttk.Separator(tab.tab_frame.interior, orient=tk.HORIZONTAL
                    ).pack(side=tk.TOP, fill=tk.X, padx=0, pady=10)

        

    def common_tab_init(self):
        ### common postit
        # dropdown list postit
        temp_code_list = []
        temp_code_list.append(CodeNTuple(
                menu_display='印出 print',
                code='print()',
                code_display='print()',
                note='印出',
                long_note=False ))
        temp_code_list.append(CodeNTuple(
                menu_display='印出(多個引數)',
                code="print('你','好')",
                code_display="print('你','好')",
                note='印出(多個引數)',
                long_note=True ))
        temp_code_list.append(CodeNTuple(
                menu_display='印出(不換行)',
                code="print('早安', end='')",
                code_display="print('早安', end='')",
                note='印出(不換行)',
                long_note=True ))
        DropdownPostit(tab_name='common', code_list = temp_code_list,
            postfix_enter=False).pack(side=tk.TOP, anchor='w', padx=2, pady=8)
            
        #ttk.Separator(common_postit_tabs['common'].frame, orient=tk.HORIZONTAL
        #        ).pack(side=tk.TOP, fill=tk.X, padx=5)

        # # separator and note
        # ttk.Label(common_postit_tabs['common'].frame, 
        #             text='-'*10 +' 常用 '+'-'*10,
                    
        #             compound=tk.LEFT, 
        #         ).pack(side=tk.TOP, padx=5, pady=8)

        # EnclosedPostit(tab_name='common',
        #                enclosed_head='print(', 
        #                enclosed_tail=')', 
        #                code_display=None,
        #                note='印出',
        #                postfix_enter=False,
        #                long_note=False,
        # ).pack(side=tk.TOP, anchor='w', padx=8, pady=8)

        # dropdown list postit
        temp_code_list = []
        temp_code_list.append(CodeNTuple(
                menu_display="'字串'",
                code="'字串'",
                code_display="'字串'",
                note='字串(文字)',
                long_note=True ))
        DropdownPostit(tab_name='common', code_list = temp_code_list,
            postfix_enter=False).pack(side=tk.TOP, anchor='w', padx=2, pady=8)


        temp_code_list = []
        temp_code_list.append(CodeNTuple(
                menu_display='輸入 input',
                code="變數 = input('請輸入: ')",
                code_display="變數 = input('請輸入: ')",
                note='輸入',
                long_note=False ))
        DropdownPostit(tab_name='common', code_list = temp_code_list,
            postfix_enter=False).pack(side=tk.TOP, anchor='w', padx=2, pady=8)


        # BasePostit(tab_name='common',
        #                    code='"Hello World!"',
        #                    code_display='"Hello World!"',
        #                    note="你好世界(字串)",
        #                    postfix_enter=False,
        #                    long_note=True,
        # ).pack(side=tk.TOP, anchor='w', padx=2, pady=8)

        # dropdown list postit
        temp_code_list = []
        temp_code_list.append(CodeNTuple(
                menu_display='查詢屬性 dir()',
                code='dir()',
                code_display='dir()',
                note='查詢屬性',
                long_note=False ))
        temp_code_list.append(CodeNTuple(
                menu_display='查詢說明 help()',
                code='help()',
                code_display='help()',
                note='查詢說明',
                long_note=False ))
        temp_code_list.append(CodeNTuple(
                menu_display='查詢類型 type()',
                code='type()',
                code_display='type()',
                note='查詢類型',
                long_note=False ))
        DropdownPostit(tab_name='common', code_list = temp_code_list,
            postfix_enter=False).pack(side=tk.TOP, anchor='w', padx=2, pady=8)

        # dropdown list postit
        temp_code_list = []
        temp_code_list.append(CodeNTuple(
                menu_display='主要執行模組 __main__',
                code="if __name__=='__main__':\npass",
                code_display="if __name__ == '__main__':\n    pass",
                note='如果是主要模組:\n        成立區塊',
                long_note=True ))
        DropdownPostit(tab_name='common', code_list = temp_code_list,
            postfix_enter=False).pack(side=tk.TOP, anchor='w', padx=2, pady=8)


    def data_tab_init(self):

        # separator and note
        f = font.Font(size=11, weight=font.NORMAL, family='Consolas')
        ttk.Label(common_postit_tabs['data'].frame.interior, 
                    #text='='*6 +' 【 條件分支 】 '+'='*6,
                    text=' >> 數值類型',
                    font=f,    
                    compound=tk.LEFT, 
                ).pack(side=tk.TOP, padx=5, pady=8, anchor='w')

        # dropdown list postit
        temp_code_list = []
        temp_code_list.append(CodeNTuple(
                menu_display='整數 int',
                code='int()',
                code_display='int()',
                note='轉成整數類型',
                long_note=False ))

        DropdownPostit(tab_name='data', code_list = temp_code_list,
            postfix_enter=False).pack(side=tk.TOP, anchor='w', padx=2, pady=8)		


        # dropdown list postit
        temp_code_list = []
        temp_code_list.append(CodeNTuple(
                menu_display='浮點數 float',
                code='float()',
                code_display='float()',
                note='轉成浮點數類型',
                long_note=False ))
        DropdownPostit(tab_name='data', code_list = temp_code_list,
            postfix_enter=False).pack(side=tk.TOP, anchor='w', padx=2, pady=8)	


        # dropdown list postit
        temp_code_list = []
        temp_code_list.append(CodeNTuple(
                menu_display='布林值 bool',
                code='bool()',
                code_display='bool()',
                note='轉成布林值類型',
                long_note=False ))
        DropdownPostit(tab_name='data', code_list = temp_code_list,
            postfix_enter=False).pack(side=tk.TOP, anchor='w', padx=2, pady=8)


        ttk.Separator(common_postit_tabs['data'].frame.interior, orient=tk.HORIZONTAL
            ).pack(side=tk.TOP, fill=tk.X, padx=0, pady=10)
        f = font.Font(size=11, weight=font.NORMAL, family='Consolas')
        ttk.Label(common_postit_tabs['data'].frame.interior, 
                    #text='='*6 +' 【 條件分支 】 '+'='*6,
                    text=' >> 字串類型',
                    font=f,    
                    compound=tk.LEFT, 
                ).pack(side=tk.TOP, padx=5, pady=8, anchor='w')


        # dropdown list postit
        temp_code_list = []
        temp_code_list.append(CodeNTuple(
                menu_display='字串 str',
                code='str()',
                code_display='str()',
                note='轉成字串類型',
                long_note=False ))
        DropdownPostit(tab_name='data', code_list = temp_code_list,
            postfix_enter=False).pack(side=tk.TOP, anchor='w', padx=2, pady=8)

        temp_code_list = []
        temp_code_list.append(CodeNTuple(
                menu_display='字串 str 雙引號',
                code='名稱 = "小新"',
                code_display='名稱 = "小新"',
                note='建立str字串',
                long_note=False ))
        temp_code_list.append(CodeNTuple(
                menu_display='字串 str 單引號',
                code="名稱 = '小花'",
                code_display="名稱 = '小花'",
                note='建立str字串',
                long_note=False ))
        DropdownPostit(tab_name='data', code_list = temp_code_list,
            postfix_enter=False).pack(side=tk.TOP, anchor='w', padx=2, pady=8)

        # BasePostit(tab_name='common',
        #                    code="dir()",
        #                    code_display="dir()",
        #                    note="物件屬性",
        #                    postfix_enter=False,
        # ).pack(side=tk.TOP, anchor='w', padx=2, pady=8)

        ttk.Separator(common_postit_tabs['data'].frame.interior, orient=tk.HORIZONTAL
            ).pack(side=tk.TOP, fill=tk.X, padx=0, pady=10)
        f = font.Font(size=11, weight=font.NORMAL, family='Consolas')
        ttk.Label(common_postit_tabs['data'].frame.interior, 
                    #text='='*6 +' 【 條件分支 】 '+'='*6,
                    text=' >> 群集類型',
                    font=f,    
                    compound=tk.LEFT, 
                ).pack(side=tk.TOP, padx=5, pady=8, anchor='w')

        # dropdown list postit
        temp_code_list = []
        temp_code_list.append(CodeNTuple(
                menu_display='list清單 ',
                code="清單 = [3,1,2]",
                code_display="清單 = [10,20,30]",
                note='建立list清單',
                long_note=True ))
        temp_code_list.append(CodeNTuple(
                menu_display='list清單 (混合類型)',
                code="清單 = [100,'小新','小花']",
                code_display="清單 = [100,'小新','小花']",
                note='建立list清單',
                long_note=True ))
        DropdownPostit(tab_name='data', code_list = temp_code_list,
            postfix_enter=False).pack(side=tk.TOP, anchor='w', padx=2, pady=8)



    def builtin_tab_init(self):
        f = font.Font(size=11, weight=font.NORMAL, family='Consolas')
        ttk.Label(common_postit_tabs['builtin'].frame.interior, 
                    #text='='*6 +' 【 條件分支 】 '+'='*6,
                    text=' >> 內建函式',
                    font=f,    
                    compound=tk.LEFT, 
                ).pack(side=tk.TOP, padx=5, pady=8, anchor='w')  
        # dropdown list postit
        temp_code_list = []
        temp_code_list.append(CodeNTuple(
                menu_display='長度 len',
                code="len([0,1,2])",
                code_display='len([0,1,2])',
                note='長度',
                long_note=False))
        temp_code_list.append(CodeNTuple(
                menu_display='四捨六入五成雙 round',
                code='round(4.6)',
                code_display='round(4.6)',
                note='四捨六入五成雙',
                long_note=False))
        temp_code_list.append(CodeNTuple(
                menu_display='最大值 max',
                code='max(2, 3)',
                code_display='max(2, 3)',
                note='最大值',
                long_note=False))
        temp_code_list.append(CodeNTuple(
                menu_display='最小值 min',
                code='min(2, 3)',
                code_display='min(2, 3)',
                note='最小值',
                long_note=False))
        temp_code_list.append(CodeNTuple(
                menu_display='絕對值 abs',
                code='abs(-1)',
                code_display='abs(-1)',
                note='絕對值',
                long_note=False))
        DropdownPostit(tab_name='builtin', code_list = temp_code_list,
            postfix_enter=False).pack(side=tk.TOP, anchor='w', padx=2, pady=8)



        ttk.Separator(common_postit_tabs['builtin'].frame.interior, orient=tk.HORIZONTAL
            ).pack(side=tk.TOP, fill=tk.X, padx=0, pady=10)
        f = font.Font(size=11, weight=font.NORMAL, family='Consolas')
        ttk.Label(common_postit_tabs['builtin'].frame.interior, 
                    #text='='*6 +' 【 條件分支 】 '+'='*6,
                    text=' >> 隨機模組random',
                    font=f,    
                    compound=tk.LEFT, 
                ).pack(side=tk.TOP, padx=5, pady=8, anchor='w')        

        # dropdown list postit
        temp_code_list = []
        temp_code_list.append(CodeNTuple(
                menu_display='匯入隨機模組 random',
                code='import random as 隨機',
                code_display='import random as 隨機',
                note='匯入隨機模組 random',
                long_note=True))
        DropdownPostit(tab_name='builtin', code_list = temp_code_list,
            postfix_enter=False).pack(side=tk.TOP, anchor='w', padx=2, pady=8)

        temp_code_list = []
        temp_code_list.append(CodeNTuple(
                menu_display='隨機挑個整數(範圍內) random.randint',
                code='隨機.randint(1,10)',
                code_display='隨機.randint(1,10)',
                note='隨機挑個整數(範圍內)',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='隨機挑個項目 choice',
                code='隨機.choice([3,5,9])',
                code_display='隨機.choice([3,5,9])',
                note='隨機挑個項目',
                long_note=True))
        DropdownPostit(tab_name='builtin', code_list = temp_code_list,
            postfix_enter=False).pack(side=tk.TOP, anchor='w', padx=2, pady=8)


        ttk.Separator(common_postit_tabs['builtin'].frame.interior, orient=tk.HORIZONTAL
            ).pack(side=tk.TOP, fill=tk.X, padx=0, pady=10)
        f = font.Font(size=11, weight=font.NORMAL, family='Consolas')
        ttk.Label(common_postit_tabs['builtin'].frame.interior, 
                    #text='='*6 +' 【 條件分支 】 '+'='*6,
                    text=' >> 時間模組time',
                    font=f,    
                    compound=tk.LEFT, 
                ).pack(side=tk.TOP, padx=5, pady=8, anchor='w')

        # dropdown list postit
        temp_code_list = []
        temp_code_list.append(CodeNTuple(
                menu_display='匯入時間模組time',
                code='import time as 時間',
                code_display='import time as 時間',
                note='匯入時間模組time',
                long_note=True))
        # temp_code_list.append(CodeNTuple(
        #         menu_display='從時間模組匯入sleep',
        #         code='from time import sleep',
        #         code_display='from time import sleep',
        #         note='從時間模組匯入sleep',
        #         long_note=True))
        DropdownPostit(tab_name='builtin', code_list = temp_code_list,
            postfix_enter=False).pack(side=tk.TOP, anchor='w', padx=2, pady=8)

        temp_code_list = []
        temp_code_list.append(CodeNTuple(
                menu_display='時間(累計秒數) time',
                code='時間.time()',
                code_display='時間.time()',
                note='時間(累計秒數)',
                long_note=False))
        temp_code_list.append(CodeNTuple(
                menu_display='暫停幾秒(睡眠) sleep',
                code='時間.sleep(2)',
                code_display='時間.sleep(2)',
                note='暫停幾秒(睡眠)',
                long_note=False))
        DropdownPostit(tab_name='builtin', code_list = temp_code_list,
            postfix_enter=False).pack(side=tk.TOP, anchor='w', padx=2, pady=8)


        ttk.Separator(common_postit_tabs['builtin'].frame.interior, orient=tk.HORIZONTAL
            ).pack(side=tk.TOP, fill=tk.X, padx=0, pady=10)
        f = font.Font(size=11, weight=font.NORMAL, family='Consolas')
        ttk.Label(common_postit_tabs['builtin'].frame.interior, 
                    #text='='*6 +' 【 條件分支 】 '+'='*6,
                    text=' >> 數學模組math',
                    font=f,    
                    compound=tk.LEFT, 
                ).pack(side=tk.TOP, padx=5, pady=8, anchor='w')

        # dropdown list postit
        temp_code_list = []
        temp_code_list.append(CodeNTuple(
                menu_display='匯入數學模組math',
                code='import math as 數學',
                code_display='import math as 數學',
                note='匯入數學模組math',
                long_note=True))
        # temp_code_list.append(CodeNTuple(
        #         menu_display='從時間模組匯入sleep',
        #         code='from time import sleep',
        #         code_display='from time import sleep',
        #         note='從時間模組匯入sleep',
        #         long_note=True))
        DropdownPostit(tab_name='builtin', code_list = temp_code_list,
            postfix_enter=False).pack(side=tk.TOP, anchor='w', padx=2, pady=8)

        temp_code_list = []
        temp_code_list.append(CodeNTuple(
                menu_display='最大公因數 gcd',
                code='數學.gcd(8, 12)',
                code_display='數學.gcd(8, 12)',
                note='最大公因數',
                long_note=False))
        temp_code_list.append(CodeNTuple(
                menu_display='圓周率 pi',
                code='數學.pi',
                code_display='數學.pi',
                note='圓周率 pi',
                long_note=False))
        # temp_code_list.append(CodeNTuple(
        #         menu_display='最小公倍數 lcm',
        #         code='數學.lcm(8, 12)',
        #         code_display='數學.lcm(8, 12)',
        #         note='最小公倍數',
        #         long_note=False))
        temp_code_list.append(CodeNTuple(
                menu_display='開平方根 sqrt',
                code='數學.sqrt(9)',
                code_display='數學.sqrt(9)',
                note='開平方根',
                long_note=False))
        temp_code_list.append(CodeNTuple(
                menu_display='三角函數 sin',
                code='數學.sin(數學.pi / 2)',
                code_display='數學.sin(數學.pi / 2)',
                note='三角函數 sin',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='三角函數 cos',
                code='數學.cos(數學.pi / 2)',
                code_display='數學.cos(數學.pi / 2)',
                note='三角函數 cos',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='角度轉弧度 radians',
                code='數學.radians(180)',
                code_display='數學.radians(180)',
                note='角度轉弧度 radians',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='弧度轉角度 degrees',
                code='數學.degrees(數學.pi)',
                code_display='數學.degrees(數學.pi)',
                note='弧度轉角度 degrees',
                long_note=True))
        DropdownPostit(tab_name='builtin', code_list = temp_code_list,
            postfix_enter=False).pack(side=tk.TOP, anchor='w', padx=2, pady=8)


    def turtle4t_tab_init(self):
        ### turtle 4 t postit
        # # dropdown list postit
        # temp_code_list = []
        # temp_code_list.append(CodeNTuple(
        #         menu_display='',
        #         code='',
        #         code_display='',
        #         note='',
        #         long_note=True))
        # temp_code_list.append(CodeNTuple(
        #         menu_display='',
        #         code='',
        #         code_display='',
        #         note='',
        #         long_note=True ))
        # DropdownPostit(tab_name='turtle4t', code_list = temp_code_list,
        #     postfix_enter=False).pack(side=tk.TOP, anchor='w', padx=8, pady=8)

        # title and setup tool
        tab = common_postit_tabs['turtle4t']
        #example_vars = ['長','角度','邊','小海龜','Turtle','海龜模組'] 
        example_vars = ['長','角度','邊','動作','顏色','字型','寬','層','樹枝','縮減'] 
        tab.popup_init(example_vars)

        f = font.Font(size=11, weight=font.NORMAL, family='Consolas')
        label =ttk.Label(common_postit_tabs['turtle4t'].frame.interior, 
                text='【海龜繪圖】', 
                image= common_images['gear'],
                font=f,
                compound=tk.RIGHT,
                )                
        label.pack(side=tk.TOP, padx=5, pady=8, anchor='w')
        label.bind("<Button-1>", common_postit_tabs['turtle4t'].popup)

        # dropdown list postit
        temp_code_list = []
        temp_code_list.append(CodeNTuple(
                menu_display='from 海龜模組 import *',
                code='from 海龜模組 import *',
                code_display='from 海龜模組 import *',
                note='從turtle4t匯入全部',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='  from turtle4t import *',
                code='from turtle4t import *',
                code_display='from turtle4t import *',
                note='從海龜模組匯入全部',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='import 海龜模組 ',
                code='import 海龜模組',
                code_display='import 海龜模組',
                note='匯入turtle4t',
                long_note=True ))
        temp_code_list.append(CodeNTuple(
                menu_display='  import turtle4t ',
                code='import turtle4t',
                code_display='import turtle4t',
                note='匯入海龜模組',
                long_note=True ))
        DropdownPostit(tab_name='turtle4t', code_list = temp_code_list,
            postfix_enter=False).pack(side=tk.TOP, anchor='w', padx=2, pady=8)



        # BasePostit(tab_name='turtle4t',
        #                    code='from 海龜模組 import *',
        #                    code_display='from 海龜模組 import *',
        #                    note="從海龜模組匯入全部",
        #                    postfix_enter=False,
        #                    long_note=True,
        # ).pack(side=tk.TOP, anchor='w', padx=8, pady=8)



        ttk.Separator(common_postit_tabs['turtle4t'].frame.interior, orient=tk.HORIZONTAL
            ).pack(side=tk.TOP, fill=tk.X, padx=0, pady=10)
        f = font.Font(size=11, weight=font.NORMAL, family='Consolas')
        ttk.Label(common_postit_tabs['turtle4t'].frame.interior, 
                    #text='='*6 +' 【 條件分支 】 '+'='*6,
                    text=' >> 動作與位置',
                    font=f,    
                    compound=tk.LEFT, 
                ).pack(side=tk.TOP, padx=5, pady=8, anchor='w')

        # dropdown list postit
        temp_code_list = []
        temp_code_list.append(CodeNTuple(
                menu_display='向前',
                code='向前(50)',
                code_display='向前(50)',
                note='forward',
                long_note=False))
        temp_code_list.append(CodeNTuple(
                menu_display='  forward',
                code='forward(50)',
                code_display='forward(50)',
                note='向前',
                long_note=False))
        temp_code_list.append(CodeNTuple(
                menu_display='向後',
                code='向後(50)',
                code_display='向後(50)',
                note='back',
                long_note=False ))
        temp_code_list.append(CodeNTuple(
                menu_display='  back',
                code='back(50)',
                code_display='back(50)',
                note='向後',
                long_note=False ))
        DropdownPostit(tab_name='turtle4t', code_list = temp_code_list,
            postfix_enter=False).pack(side=tk.TOP, anchor='w', padx=2, pady=8)

        # dropdown list postit
        temp_code_list = []
        temp_code_list.append(CodeNTuple(
                menu_display='右轉',
                code='右轉(90)',
                code_display='右轉(90)',
                note='right',
                long_note=False ))
        temp_code_list.append(CodeNTuple(
                menu_display='  right',
                code='right(90)',
                code_display='right(90)',
                note='右轉',
                long_note=False))
        temp_code_list.append(CodeNTuple(
                menu_display='左轉',
                code='左轉(90)',
                code_display='左轉(90)',
                note='left',
                long_note=False ))
        temp_code_list.append(CodeNTuple(
                menu_display='  left',
                code='left(90)',
                code_display='left(90)',
                note='左轉',
                long_note=False ))
        DropdownPostit(tab_name='turtle4t', code_list = temp_code_list,
            postfix_enter=False).pack(side=tk.TOP, anchor='w', padx=2, pady=8)


        # dropdown list postit
        temp_code_list = []
        # temp_code_list.append(CodeNTuple(
        #         menu_display='回出發點',
        #         code='回出發點()',
        #         code_display='回出發點()',
        #         note='home',
        #         long_note=False ))
        # temp_code_list.append(CodeNTuple(
        #         menu_display='  home',
        #         code='home()',
        #         code_display='home()',
        #         note='回出發點',
        #         long_note=False ))
        temp_code_list.append(CodeNTuple(
                menu_display='走到座標',
                code='走到(0,0)',
                code_display='走到(0,0)',
                note='goto',
                long_note=False ))
        temp_code_list.append(CodeNTuple(
                menu_display='  goto',
                code='goto(0,0)',
                code_display='goto(0,0)',
                note='走到',
                long_note=False ))
        temp_code_list.append(CodeNTuple(
                menu_display='x設為',
                code='x設為(0)',
                code_display='x設為(0)',
                note='setx',
                long_note=False ))
        temp_code_list.append(CodeNTuple(
                menu_display='  setx',
                code='setx(0)',
                code_display='setx(0)',
                note='x設為',
                long_note=False ))
        temp_code_list.append(CodeNTuple(
                menu_display='y設為',
                code='y設為(0)',
                code_display='y設為(0)',
                note='sety',
                long_note=False ))
        temp_code_list.append(CodeNTuple(
                menu_display='  sety',
                code='sety(0)',
                code_display='sety(0)',
                note='y設為',
                long_note=False ))
        temp_code_list.append(CodeNTuple(
                menu_display='位置',
                code='位置()',
                code_display='位置()',
                note='pos',
                long_note=False ))
        temp_code_list.append(CodeNTuple(
                menu_display='  pos',
                code='pos()',
                code_display='pos()',
                note='位置',
                long_note=False ))
        temp_code_list.append(CodeNTuple(
                menu_display='x座標',
                code='x座標()',
                code_display='x座標()',
                note='xcor',
                long_note=False ))
        temp_code_list.append(CodeNTuple(
                menu_display='  xcor',
                code='xcor()',
                code_display='xcor()',
                note='x座標',
                long_note=False ))
        temp_code_list.append(CodeNTuple(
                menu_display='y座標',
                code='y座標()',
                code_display='y座標()',
                note='ycor',
                long_note=False ))
        temp_code_list.append(CodeNTuple(
                menu_display='  ycor',
                code='ycor()',
                code_display='ycor()',
                note='y座標',
                long_note=False ))
        DropdownPostit(tab_name='turtle4t', code_list = temp_code_list,
            postfix_enter=False).pack(side=tk.TOP, anchor='w', padx=2, pady=8)




        #dropdown list postit
        temp_code_list = []
        temp_code_list.append(CodeNTuple(
                menu_display='方向',
                code='方向()',
                code_display='方向()',
                note='heading',
                long_note=False )) 
        temp_code_list.append(CodeNTuple(
                menu_display='  heading',
                code='heading()',
                code_display='heading()',
                note='方向',
                long_note=False ))
        temp_code_list.append(CodeNTuple(
                menu_display='設定方向',
                code='設定方向(0)',
                code_display='設定方向(0)',
                note='setheading',
                long_note=False ))    
        temp_code_list.append(CodeNTuple(
                menu_display='  setheading',
                code='setheading(0)',
                code_display='setheading(0)',
                note='設定方向',
                long_note=False ))
        DropdownPostit(tab_name='turtle4t', code_list = temp_code_list,
            postfix_enter=False).pack(side=tk.TOP, anchor='w', padx=2, pady=8)

        ttk.Separator(common_postit_tabs['turtle4t'].frame.interior, orient=tk.HORIZONTAL
            ).pack(side=tk.TOP, fill=tk.X, padx=0, pady=10)
        f = font.Font(size=11, weight=font.NORMAL, family='Consolas')
        ttk.Label(common_postit_tabs['turtle4t'].frame.interior, 
                    #text='='*6 +' 【 條件分支 】 '+'='*6,
                    text=' >> 畫筆與畫布',
                    font=f,    
                    compound=tk.LEFT, 
                ).pack(side=tk.TOP, padx=5, pady=8, anchor='w')


        # dropdown list postit
        temp_code_list = []

        temp_code_list.append(CodeNTuple(
                menu_display='停筆',
                code='停筆()',
                code_display='停筆()',
                note='penup',
                long_note=False ))    
        temp_code_list.append(CodeNTuple(
                menu_display='  penup',
                code='penup()',
                code_display='penup()',
                note='停筆',
                long_note=False ))
        temp_code_list.append(CodeNTuple(
                menu_display='下筆',
                code='下筆()',
                code_display='下筆()',
                note='pendown',
                long_note=False ))    
        temp_code_list.append(CodeNTuple(
                menu_display='  pendown',
                code='pendown()',
                code_display='pendown()',
                note='下筆',
                long_note=False ))

        # temp_code_list.append(CodeNTuple(
        #         menu_display='下筆嗎',
        #         code='下筆嗎()',
        #         code_display='下筆嗎()',
        #         note='isdown',
        #         long_note=False ))    
        # temp_code_list.append(CodeNTuple(
        #         menu_display='  isdown',
        #         code='isdown()',
        #         code_display='isdown()',
        #         note='下筆嗎',
        #         long_note=False ))

        temp_code_list.append(CodeNTuple(
                menu_display='隱藏海龜',
                code='隱藏海龜()',
                code_display='隱藏海龜()',
                note='hideturtle',
                long_note=False ))  
        temp_code_list.append(CodeNTuple(
                menu_display='  hideturtle',
                code='hideturtle()',
                code_display='hideturtle()',
                note='隱藏海龜',
                long_note=False ))
        temp_code_list.append(CodeNTuple(
                menu_display='顯示海龜',
                code='顯示海龜()',
                code_display='顯示海龜()',
                note='showturtle',
                long_note=False ))    
        temp_code_list.append(CodeNTuple(
                menu_display='  showturtle',
                code='showturtle()',
                code_display='showturtle()',
                note='顯示海龜',
                long_note=False ))
        DropdownPostit(tab_name='turtle4t', code_list = temp_code_list,
            postfix_enter=False).pack(side=tk.TOP, anchor='w', padx=2, pady=8)

        # dropdown list postit
        temp_code_list = []
        temp_code_list.append(CodeNTuple(
                menu_display='速度',
                code="速度(5)",
                code_display="速度(5)",
                note='speed  1~10 ',
                long_note=False )) 
        temp_code_list.append(CodeNTuple(
                menu_display='  speed',
                code="speed(5)",
                code_display="speed(5)",
                note='速度 1~10',
                long_note=False ))
        DropdownPostit(tab_name='turtle4t', code_list = temp_code_list,
            postfix_enter=False).pack(side=tk.TOP, anchor='w', padx=2, pady=8)

        # dropdown list postit
        temp_code_list = []
        temp_code_list.append(CodeNTuple(
                menu_display='畫布大小',
                code='畫布大小()',
                code_display='畫布大小()',
                note='screensize',
                long_note=False ))  
        temp_code_list.append(CodeNTuple(
                menu_display='  screensize',
                code='screensize()',
                code_display='screensize()',
                note='畫布大小',
                long_note=False ))  
        temp_code_list.append(CodeNTuple(
                menu_display='背景顏色',
                code="背景顏色('white')",
                code_display="背景顏色('white')",
                note='bgcolor',
                long_note=True ))
        temp_code_list.append(CodeNTuple(
                menu_display='  bgcolor',
                code="bgcolor('white')",
                code_display="bgcolor('white')",
                note='背景顏色',
                long_note=True ))

        DropdownPostit(tab_name='turtle4t', code_list = temp_code_list,
            postfix_enter=False).pack(side=tk.TOP, anchor='w', padx=2, pady=8)

        ttk.Separator(common_postit_tabs['turtle4t'].frame.interior, orient=tk.HORIZONTAL
            ).pack(side=tk.TOP, fill=tk.X, padx=0, pady=10)
        f = font.Font(size=11, weight=font.NORMAL, family='Consolas')
        ttk.Label(common_postit_tabs['turtle4t'].frame.interior, 
                    #text='='*6 +' 【 條件分支 】 '+'='*6,
                    text=' >> 筆跡與顏色',
                    font=f,    
                    compound=tk.LEFT, 
                ).pack(side=tk.TOP, padx=5, pady=8, anchor='w')


        # dropdown list postit
        temp_code_list = []
        temp_code_list.append(CodeNTuple(
                menu_display='畫筆顏色',
                code="畫筆顏色('black')",
                code_display="畫筆顏色('black')",
                note='pencolor',
                long_note=True ))    
        temp_code_list.append(CodeNTuple(
                menu_display='  pencolor',
                code="pencolor('black')",
                code_display="pencolor('black')",
                note='畫筆顏色',
                long_note=True ))
        temp_code_list.append(CodeNTuple(
                menu_display='填充顏色',
                code="填充顏色('orange')",
                code_display="填充顏色('orange')",
                note='fillcolor',
                long_note=True ))    
        temp_code_list.append(CodeNTuple(
                menu_display='  fillcolor',
                code="fillcolor('orange')",
                code_display="fillcolor('orange')",
                note='填充顏色',
                long_note=True ))

        temp_code_list.append(CodeNTuple(
                menu_display='開始填色',
                code='開始填色()',
                code_display='開始填色()',
                note='begin_fill',
                long_note=False ))    
        temp_code_list.append(CodeNTuple(
                menu_display='  begin_fill',
                code='begin_fill()',
                code_display='begin_fill()',
                note='開始填色',
                long_note=False ))
        temp_code_list.append(CodeNTuple(
                menu_display='停止填色',
                code='停止填色()',
                code_display='停止填色()',
                note='end_fill',
                long_note=False ))    
        temp_code_list.append(CodeNTuple(
                menu_display='  end_fill',
                code='end_fill()',
                code_display='end_fill()',
                note='停止填色',
                long_note=False ))


        temp_code_list.append(CodeNTuple(
                menu_display='畫筆尺寸',
                code='畫筆尺寸(1)',
                code_display='畫筆尺寸(1)',
                note='pensize',
                long_note=False ))    
        temp_code_list.append(CodeNTuple(
                menu_display='  pensize',
                code='pensize(1)',
                code_display='pensize(1)',
                note='畫筆尺寸',
                long_note=False ))
        DropdownPostit(tab_name='turtle4t', code_list = temp_code_list,
            postfix_enter=False).pack(side=tk.TOP, anchor='w', padx=2, pady=8)

        # dropdown list postit
        temp_code_list = []
        temp_code_list.append(CodeNTuple(
                menu_display="red 紅色",
                code="'red'",
                code_display="'red'",
                note='紅色',
                long_note=False ))    
        temp_code_list.append(CodeNTuple(
                menu_display="orange 橙色",
                code="'orange'",
                code_display="'orange'",
                note='橙色',
                long_note=False ))  
        temp_code_list.append(CodeNTuple(
                menu_display="yellow 黃色",
                code="'yellow'",
                code_display="'yellow'",
                note='黃色',
                long_note=False ))   
        temp_code_list.append(CodeNTuple(
                menu_display="green 綠色",
                code="'green'",
                code_display="'green'",
                note='綠色',
                long_note=False )) 
        temp_code_list.append(CodeNTuple(
                menu_display="blue 藍色",
                code="'blue'",
                code_display="'blue'",
                note='藍色',
                long_note=False )) 
        temp_code_list.append(CodeNTuple(
                menu_display="cyan 青色",
                code="'cyan'",
                code_display="'cyan'",
                note='青色',
                long_note=False )) 
        temp_code_list.append(CodeNTuple(
                menu_display="purple 紫色",
                code="'purple'",
                code_display="'purple'",
                note='紫色',
                long_note=False ))  
        temp_code_list.append(CodeNTuple(
                menu_display="black 黑色",
                code="'black'",
                code_display="'black'",
                note='黑色',
                long_note=False ))  
        temp_code_list.append(CodeNTuple(
                menu_display="gray 灰色",
                code="'gray'",
                code_display="'gray'",
                note='灰色',
                long_note=False )) 
        temp_code_list.append(CodeNTuple(
                menu_display="white 白色",
                code="'white'",
                code_display="'white'",
                note='白色',
                long_note=False )) 
        temp_code_list.append(CodeNTuple(
                menu_display="pink 粉紅色",
                code="'pink'",
                code_display="'pink'",
                note='粉紅色',
                long_note=False )) 
        temp_code_list.append(CodeNTuple(
                menu_display="brown 棕色",
                code="'brown'",
                code_display="'brown'",
                note='棕色',
                long_note=False )) 
        DropdownPostit(tab_name='turtle4t', code_list = temp_code_list,
            postfix_enter=False).pack(side=tk.TOP, anchor='w', padx=2, pady=8)


        # dropdown list postit
        temp_code_list = []
        temp_code_list.append(CodeNTuple(
                menu_display='顏色清單',
                code="清單 = ['orange','white']",
                code_display="清單 = ['orange','white']",
                note='顏色清單',
                long_note=True))
        DropdownPostit(tab_name='turtle4t', code_list = temp_code_list,
            postfix_enter=False).pack(side=tk.TOP, anchor='w', padx=2, pady=8)


        # dropdown list postit
        temp_code_list = []
        temp_code_list.append(CodeNTuple(
                menu_display='筆跡清除',
                code='筆跡清除()',
                code_display='筆跡清除()',
                note='clear',
                long_note=False ))    
        temp_code_list.append(CodeNTuple(
                menu_display='  clear',
                code='clear()',
                code_display='clear()',
                note='筆跡清除',
                long_note=False ))
        DropdownPostit(tab_name='turtle4t', code_list = temp_code_list,
            postfix_enter=False).pack(side=tk.TOP, anchor='w', padx=2, pady=8)

        ttk.Separator(common_postit_tabs['turtle4t'].frame.interior, orient=tk.HORIZONTAL
            ).pack(side=tk.TOP, fill=tk.X, padx=0, pady=10)
        f = font.Font(size=11, weight=font.NORMAL, family='Consolas')
        ttk.Label(common_postit_tabs['turtle4t'].frame.interior, 
                    #text='='*6 +' 【 條件分支 】 '+'='*6,
                    text=' >> 形狀與文字',
                    font=f,    
                    compound=tk.LEFT, 
                ).pack(side=tk.TOP, padx=5, pady=8, anchor='w')

        # dropdown list postit
        temp_code_list = []
        temp_code_list.append(CodeNTuple(
                menu_display='畫圓',
                code='畫圓(50)',
                code_display='畫圓(50)',
                note='circle',
                long_note=False ))
        temp_code_list.append(CodeNTuple(
                menu_display='  circle',
                code='circle(50)',
                code_display='circle(50)',
                note='畫圓',
                long_note=False ))
        temp_code_list.append(CodeNTuple(
                menu_display='畫點',
                code='畫點(50, "black")',
                code_display='畫點(50, "black")',
                note='dot',
                long_note=False ))
        temp_code_list.append(CodeNTuple(
                menu_display='  dot',
                code='dot(50, "black")',
                code_display='dot(50, "black")',
                note='畫點',
                long_note=False ))
        DropdownPostit(tab_name='turtle4t', code_list = temp_code_list,
             postfix_enter=False).pack(side=tk.TOP, anchor='w', padx=2, pady=8)


        # dropdown list postit
        temp_code_list = []
        temp_code_list.append(CodeNTuple(
                menu_display='寫字',
                code="寫字('內容', align='center', font=字型)",
                code_display="寫字('內容', align='center', font=字型)",
                note='write',
                long_note=False ))
        temp_code_list.append(CodeNTuple(
                menu_display='  write',
                code="write('內容', align='center', font=字型)",
                code_display="write('內容', align='center', font=字型)",
                note='寫字',
                long_note=False ))
        DropdownPostit(tab_name='turtle4t', code_list = temp_code_list,
             postfix_enter=False).pack(side=tk.TOP, anchor='w', padx=2, pady=8)

        # dropdown list postit
        temp_code_list = []
        temp_code_list.append(CodeNTuple(
                menu_display='字型',
                code="字型 = ('標楷體',12,'normal')",
                code_display="字型 = ('標楷體',12,'normal')",
                note='字型設定',
                long_note=False ))
        DropdownPostit(tab_name='turtle4t', code_list = temp_code_list,
             postfix_enter=False).pack(side=tk.TOP, anchor='w', padx=2, pady=8)

        ttk.Separator(common_postit_tabs['turtle4t'].frame.interior, orient=tk.HORIZONTAL
            ).pack(side=tk.TOP, fill=tk.X, padx=0, pady=10)
        f = font.Font(size=11, weight=font.NORMAL, family='Consolas')
        ttk.Label(common_postit_tabs['turtle4t'].frame.interior, 
                    #text='='*6 +' 【 條件分支 】 '+'='*6,
                    text=' >> 事件',
                    font=f,    
                    compound=tk.LEFT, 
                ).pack(side=tk.TOP, padx=5, pady=8, anchor='w')


        # dropdown list postit
        temp_code_list = []
        # temp_code_list.append(CodeNTuple(
        #         menu_display='滑鼠點擊時',
        #         code='滑鼠點擊時(功能函式)',
        #         code_display='滑鼠點擊時(功能函式)',
        #         note='onclick',
        #         long_note=True ))    
        # temp_code_list.append(CodeNTuple(
        #         menu_display='  onclick',
        #         code='onclick(func)',
        #         code_display='onclick(func)',
        #         note='滑鼠點擊時',
        #         long_note=True )) 
        temp_code_list.append(CodeNTuple(
                menu_display='滑鼠點擊螢幕時',
                code='滑鼠點擊螢幕時(功能函式)',
                code_display='滑鼠點擊螢幕時(功能函式)',
                note='onscreenclick',
                long_note=True )) 
        temp_code_list.append(CodeNTuple(
                menu_display='  onscreenclick',
                code='onscreenclick(func)',
                code_display='onscreenclick(func)',
                note='滑鼠點擊螢幕時',
                long_note=True ))
        temp_code_list.append(CodeNTuple(
                menu_display='自訂功能(滑鼠點擊時)',
                code='def 功能函式(x, y):\npass',
                code_display='def 功能函式(x, y):\n    pass',
                note='自訂功能(滑鼠點擊時)',
                long_note=True ))  
        temp_code_list.append(CodeNTuple(
                menu_display='  define mouse click function ',
                code='def func(x, y):\npass',
                code_display='def func(x, y):\n    pass',
                note='自訂功能(滑鼠點擊時)',
                long_note=True ))  
        DropdownPostit(tab_name='turtle4t', code_list = temp_code_list,
            postfix_enter=False).pack(side=tk.TOP, anchor='w', padx=2, pady=8)

        # dropdown list postit
        temp_code_list = []
        temp_code_list.append(CodeNTuple(
                menu_display='鍵盤按下時(任何鍵)',
                code="鍵盤按下時(功能函式)\n監聽()",
                code_display='鍵盤按下時(功能函式)\n監聽()',
                note='onkeypress(任何鍵)',
                long_note=True ))
        temp_code_list.append(CodeNTuple(
                menu_display='鍵盤按下時(指定鍵)',
                code="鍵盤按下時(功能函式, key='Up')\n監聽()",
                code_display="鍵盤按下時(功能函式, key='Up')\n監聽()",
                note='onkeypress(指定鍵)',
                long_note=True ))
        temp_code_list.append(CodeNTuple(
                menu_display='  onkeypress',
                code="onkeypress(func, key='Up')\nlisten()",
                code_display='onkeypress(func)\nlisten()',
                note='鍵盤按下時',
                long_note=True ))
        temp_code_list.append(CodeNTuple(
                menu_display='自訂功能(鍵盤按下時)',
                code='def 功能函式():\npass',
                code_display='def 功能函式():\n    pass',
                note='自訂功能(鍵盤按下時)',
                long_note=True ))  
        temp_code_list.append(CodeNTuple(
                menu_display='  define key press function ',
                code='def func():\npass',
                code_display='def func():\n    pass',
                note='自訂功能(鍵盤按下時)',
                long_note=True ))  
        DropdownPostit(tab_name='turtle4t', code_list = temp_code_list,
            postfix_enter=False).pack(side=tk.TOP, anchor='w', padx=2, pady=8)    


        # dropdown list postit
        temp_code_list = []
        temp_code_list.append(CodeNTuple(
                menu_display="數字鍵",
                code="'1'",
                code_display="'1'",
                note='數字鍵',
                long_note=False ))   
        temp_code_list.append(CodeNTuple(
                menu_display="字母鍵",
                code="'a'",
                code_display="'a'",
                note='字母鍵',
                long_note=False ))   
        temp_code_list.append(CodeNTuple(
                menu_display="空白鍵 space",
                code="'space'",
                code_display="'space'",
                note='空白鍵',
                long_note=False ))
        temp_code_list.append(CodeNTuple(
                menu_display="向上鍵 Up",
                code="'Up'",
                code_display="'Up'",
                note='向上鍵',
                long_note=False ))  
        temp_code_list.append(CodeNTuple(
                menu_display="向下鍵 Down",
                code="'Down'",
                code_display="'Down'",
                note='向下鍵',
                long_note=False ))  
        temp_code_list.append(CodeNTuple(
                menu_display="向右鍵 Right",
                code="'Right'",
                code_display="'Right'",
                note='向右鍵',
                long_note=False ))  
        temp_code_list.append(CodeNTuple(
                menu_display="向左鍵 Left",
                code="'Left'",
                code_display="'Left'",
                note='向左鍵',
                long_note=False )) 
        DropdownPostit(tab_name='turtle4t', code_list = temp_code_list,
            postfix_enter=False).pack(side=tk.TOP, anchor='w', padx=2, pady=8)



    def physics_tab_init(self):
        # title and setup tool
        tab = common_postit_tabs['physics']
        #example_vars = ['長','角度','邊','小海龜','Turtle','海龜模組'] 
        example_vars = ['x','y','物體','dx','dy','向量','按鍵'] 
        tab.popup_init(example_vars)

        f = font.Font(size=11, weight=font.NORMAL, family='Consolas')
        label =ttk.Label(common_postit_tabs['physics'].frame.interior, 
                text='【物理碰撞模擬】', 
                image= common_images['gear'],
                font=f,
                compound=tk.RIGHT,
                )                
        label.pack(side=tk.TOP, padx=5, pady=8, anchor='w')
        label.bind("<Button-1>", common_postit_tabs['physics'].popup)

        # dropdown list postit
        temp_code_list = []
        temp_code_list.append(CodeNTuple(
                menu_display='from 物理模組 import *',
                code='from 物理模組 import *',
                code_display='from 物理模組 import *',
                note='從物理模組匯入全部',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='from pie4t import *',
                code='from pie4t import *',
                code_display='from pie4t import *',
                note='從物理模組匯入全部',
                long_note=True))
        # temp_code_list.append(CodeNTuple(
        #         menu_display='import 物理模組 ',
        #         code='import 物理模組',
        #         code_display='import 物理模組',
        #         note='匯入pie4t',
        #         long_note=True ))
        # temp_code_list.append(CodeNTuple(
        #         menu_display='  import pie4t ',
        #         code='import pie4t',
        #         code_display='import pie4t',
        #         note='匯入物理模組',
        #         long_note=True ))
        DropdownPostit(tab_name='physics', code_list = temp_code_list,
            postfix_enter=False).pack(side=tk.TOP, anchor='w', padx=2, pady=8)


        ttk.Separator(common_postit_tabs['physics'].frame.interior, orient=tk.HORIZONTAL
            ).pack(side=tk.TOP, fill=tk.X, padx=0, pady=10)
        f = font.Font(size=11, weight=font.NORMAL, family='Consolas')
        ttk.Label(common_postit_tabs['physics'].frame.interior, 
                    #text='='*6 +' 【 條件分支 】 '+'='*6,
                    text=' >> 物理舞台',
                    font=f,    
                    compound=tk.LEFT, 
                ).pack(side=tk.TOP, padx=5, pady=8, anchor='w')

        # dropdown list postit
        temp_code_list = []
        # temp_code_list.append(CodeNTuple(
        #         menu_display='舞台',
        #         code='舞台 = 物理引擎()',
        #         code_display='舞台 = 物理引擎()',
        #         note='舞台',
        #         long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='舞台(設定尺寸)',
                code='舞台 = 物理引擎(400,600)',
                code_display='舞台 = 物理引擎(400, 600)',
                note='舞台(設定尺寸)',
                long_note=True))
      
        temp_code_list.append(CodeNTuple(
                menu_display='重力',
                code='舞台.重力 = [0, -800]',
                code_display='舞台.重力 = [0, -800]',
                note='gravity',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='慢動作(假)',
                code='舞台.慢動作 = False',
                code_display='舞台.慢動作 = False',
                note='慢動作(假)',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='慢動作(真)',
                code='舞台.慢動作 = True',
                code_display='舞台.慢動作 = True',
                note='慢動作(真)',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='慢動作(相反)',
                code='舞台.慢動作 = not 舞台.慢動作',
                code_display='舞台.慢動作 = not 舞台.慢動作',
                note='慢動作(相反)',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='模擬暫停(真)',
                code='舞台.模擬暫停 = True',
                code_display='舞台.模擬暫停 = True',
                note='模擬暫停(真)',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='模擬暫停(假)',
                code='舞台.模擬暫停 = False',
                code_display='舞台.模擬暫停 = False',
                note='模擬暫停(假)',
                long_note=True))
        DropdownPostit(tab_name='physics', code_list = temp_code_list,
            postfix_enter=False).pack(side=tk.TOP, anchor='w', padx=2, pady=8)




        # dropdown list postit
        temp_code_list = []
        temp_code_list.append(CodeNTuple(
                menu_display='模擬進行中',
                code='模擬進行中()',
                code_display='模擬進行中()',
                note='(加在程式的最後一行)',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='  simulate',
                code='simulate()',
                code_display='simulate()',
                note='模擬進行中',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='模擬主迴圈',
                code='模擬主迴圈()',
                code_display='模擬主迴圈()',
                note='(加在程式的最後一行)',
                long_note=True))
        # temp_code_list.append(CodeNTuple(
        #         menu_display='  mainloop',
        #         code='mainloop()',
        #         code_display='mainloop()',
        #         note='主迴圈',
        #         long_note=False))
        DropdownPostit(tab_name='physics', code_list = temp_code_list,
            postfix_enter=False).pack(side=tk.TOP, anchor='w', padx=2, pady=8)








        # dropdown list postit
        temp_code_list = []
        temp_code_list.append(CodeNTuple(
                menu_display='圓球隨機',
                code='新增圓球()',
                code_display='新增圓球()',
                note='圓球隨機',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='圓球隨機(設定變數)',
                code='物體 = 新增圓球()',
                code_display='物體 = 新增圓球()',
                note='圓球隨機(設定變數)',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='圓球(半徑)(設定變數)',
                code='物體 = 新增圓球(半徑=20)',
                code_display='物體 = 新增圓球(半徑=20)',
                note='圓球(半徑)(設定變數)',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='方塊隨機',
                code='新增方塊()',
                code_display='新增方塊()',
                note='方塊隨機',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='方塊隨機(設定變數)',
                code='物體 = 新增方塊()',
                code_display='物體 = 新增方塊()',
                note='方塊隨機(設定變數)',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='方塊(寬高)(設定變數)',
                code='物體 = 新增方塊(寬=30,高=20)',
                code_display='物體 = 新增方塊(寬=30,高=20)',
                note='方塊(寬高)(設定變數)',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='移除物體',
                code='移除(物體)',
                code_display='移除(物體)',
                note='remove',
                long_note=True))
        # temp_code_list.append(CodeNTuple(
        #         menu_display='  add_circle',
        #         code='add_circle()',
        #         code_display='add_circle()',
        #         note='新增圓球',
        #         long_note=False))
        DropdownPostit(tab_name='physics', code_list = temp_code_list,
            postfix_enter=False).pack(side=tk.TOP, anchor='w', padx=2, pady=8)



        # f = font.Font(size=11, weight=font.NORMAL, family='Consolas')
        # ttk.Label(common_postit_tabs['physics'].frame.interior, 
        #             #text='='*6 +' 【 條件分支 】 '+'='*6,
        #             text=' >> 互動事件',
        #             font=f,    
        #             compound=tk.LEFT, 
        #         ).pack(side=tk.TOP, padx=5, pady=8, anchor='w')
        ttk.Separator(common_postit_tabs['physics'].frame.interior, orient=tk.HORIZONTAL
            ).pack(side=tk.TOP, fill=tk.X, padx=0, pady=10)
        f = font.Font(size=11, weight=font.NORMAL, family='Consolas')
        ttk.Label(common_postit_tabs['physics'].frame.interior, 
                    #text='='*6 +' 【 條件分支 】 '+'='*6,
                    text=' >> 互動事件',
                    font=f,    
                    compound=tk.LEFT, 
                ).pack(side=tk.TOP, padx=5, pady=8, anchor='w')

        # dropdown list postit
        temp_code_list = []
        temp_code_list.append(CodeNTuple(
                menu_display='按下滑鼠時',
                code='def 按下滑鼠時(x, y):\npass\n',
                code_display='def 按下滑鼠時(x, y):\n    pass',
                note='on mouse click',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='拖曳滑鼠時',
                code='def 拖曳滑鼠時(x, y, dx, dy):\npass\n',
                code_display='def 拖曳滑鼠時(x,y,dx,dy):\n    pass',
                note='on mouse drag',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='放開滑鼠時',
                code='def 放開滑鼠時(x, y):\npass\n',
                code_display='def 放開滑鼠時(x, y):\n    pass',
                note='on mouse release',
                long_note=True))

        temp_code_list.append(CodeNTuple(
                menu_display='點擊物體時',
                code='def 點擊物體時(物體, x, y):\npass\n',
                code_display='def 點擊物體時(物體, x, y):\n    pass',
                note='on object click',
                long_note=True))
        # temp_code_list.append(CodeNTuple(
        #         menu_display='箭頭發射時',
        #         code='def 箭頭發射時(向量, 開始座標):\n___\n',
        #         code_display='def 箭頭發射時(向量, 開始座標):\n    ___',
        #         note='箭頭發射時',
        #         long_note=True))
        DropdownPostit(tab_name='physics', code_list = temp_code_list,
            postfix_enter=False).pack(side=tk.TOP, anchor='w', padx=2, pady=8)

        # dropdown list postit
        temp_code_list = []
        temp_code_list.append(CodeNTuple(
                menu_display='按下鍵盤時',
                code='def 按下鍵盤時(按鍵, x, y):\npass\n',
                code_display='def 按下鍵盤時(按鍵, x, y):\n    pass',
                note='on key press',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='放開鍵盤時',
                code='def 放開鍵盤時(按鍵, x, y):\npass\n',
                code_display='def 放開鍵盤時(按鍵, x, y):\n    pass',
                note='on key release',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='  是空白鍵?',
                code='if 按鍵 == key.SPACE :\npass',
                code_display='if 按鍵 == key.SPACE :\n    pass',
                note='是空白鍵?',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='  是Enter鍵?',
                code='if 按鍵 == key.ENTER :\npass',
                code_display='if 按鍵 == key.ENTER :\n    pass',
                note='是Enter鍵?',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='  是向上鍵?',
                code='if 按鍵 == key.UP :\npass',
                code_display='if 按鍵 == key.UP :\n    pass',
                note='是向上鍵?',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='  是向下鍵?',
                code='if 按鍵 == key.DOWN :\npass',
                code_display='if 按鍵 == key.DOWN :\n    pass',
                note='是向下鍵?',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='  是向右鍵?',
                code='if 按鍵 == key.RIGHT :\npass',
                code_display='if 按鍵 == key.RIGHT :\n    pass',
                note='是向右鍵?',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='  是向左鍵?',
                code='if 按鍵 == key.LEFT :\npass',
                code_display='if 按鍵 == key.LEFT :\n    pass',
                note='是向左鍵?',
                long_note=True))
        DropdownPostit(tab_name='physics', code_list = temp_code_list,
            postfix_enter=False).pack(side=tk.TOP, anchor='w', padx=2, pady=8)


        ttk.Separator(common_postit_tabs['physics'].frame.interior, orient=tk.HORIZONTAL
            ).pack(side=tk.TOP, fill=tk.X, padx=0, pady=10)
        f = font.Font(size=11, weight=font.NORMAL, family='Consolas')
        ttk.Label(common_postit_tabs['physics'].frame.interior, 
                    #text='='*6 +' 【 條件分支 】 '+'='*6,
                    text=' >> 物體的屬性與運動',
                    font=f,    
                    compound=tk.LEFT, 
                ).pack(side=tk.TOP, padx=5, pady=8, anchor='w')

        # dropdown list postit
        temp_code_list = []
        # temp_code_list.append(CodeNTuple(
        #         menu_display='質量',
        #         code='物體.質量',
        #         code_display='物體.質量',
        #         note='質量(取值)',
        #         long_note=False))
        temp_code_list.append(CodeNTuple(
                menu_display='彈性設定',
                code='物體.彈性 = 0.3',
                code_display='物體.彈性 = 0.3',
                note='設定彈性(須在0到1之間)',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='質量設定',
                code='物體.質量 = 100',
                code_display='物體.質量 = 100',
                note='設定質量(須大於0)',
                long_note=True))
        # temp_code_list.append(CodeNTuple(
        #         menu_display='密度',
        #         code='物體.密度',
        #         code_display='物體.密度',
        #         note='密度(取值)',
        #         long_note=False))
        temp_code_list.append(CodeNTuple(
                menu_display='密度設定',
                code='物體.密度 = 1',
                code_display='物體.密度 = 1',
                note='設定密度(須大於0)',
                long_note=True))
        # temp_code_list.append(CodeNTuple(
        #         menu_display='摩擦',
        #         code='物體.摩擦',
        #         code_display='物體.摩擦',
        #         note='摩擦(取值)',
        #         long_note=False))
        temp_code_list.append(CodeNTuple(
                menu_display='摩擦設定',
                code='物體.摩擦 = 0.5',
                code_display='物體.摩擦 = 0.5',
                note='設定摩擦(須大於0)',
                long_note=True))
        # temp_code_list.append(CodeNTuple(
        #         menu_display='彈性',
        #         code='物體.彈性',
        #         code_display='物體.彈性',
        #         note='彈性',
        #         long_note=False))


        temp_code_list.append(CodeNTuple(
                menu_display='物理反應(真)',
                code='物體.物理反應 = True',
                code_display='物體.物理反應 = True',
                note='物理反應(真)',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='物理反應(假)',
                code='物體.物理反應 = False',
                code_display='物體.物理反應 = False',
                note='物理反應(假)',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='物理反應(相反)',
                code='物體.物理反應 = not 物體.物理反應',
                code_display='物體.物理反應 = not 物體.物理反應',
                note='物理反應(相反)',
                long_note=True))

        # temp_code_list.append(CodeNTuple(
        #         menu_display='半徑(取值)(唯讀)',
        #         code='球.半徑',
        #         code_display='球.半徑',
        #         note='半徑(取值)(唯讀)',
        #         long_note=False))
        DropdownPostit(tab_name='physics', code_list = temp_code_list,
            postfix_enter=False).pack(side=tk.TOP, anchor='w', padx=2, pady=8)



        # dropdown list postit
        temp_code_list = []
        # temp_code_list.append(CodeNTuple(
        #         menu_display='位置',
        #         code='物體.位置',
        #         code_display='物體.位置',
        #         note='位置',
        #         long_note=False))
        temp_code_list.append(CodeNTuple(
                menu_display='  設定位置',
                code='物體.位置 = [300, 300]',
                code_display='物體.位置 = [300, 300]',
                note='設定位置',
                long_note=True))
        # temp_code_list.append(CodeNTuple(
        #         menu_display='速度',
        #         code='物體.速度',
        #         code_display='物體.速度',
        #         note='速度',
        #         long_note=False))
        temp_code_list.append(CodeNTuple(
                menu_display='  設定速度',
                code='物體.速度 = [300, 0]',
                code_display='物體.速度 = [300, 0]',
                note='設定速度',
                long_note=True))
        # temp_code_list.append(CodeNTuple(
        #         menu_display='角度',
        #         code='物體.角度',
        #         code_display='物體.角度',
        #         note='角度',
        #         long_note=False))
        temp_code_list.append(CodeNTuple(
                menu_display='  設定角度',
                code='物體.角度 = 0',
                code_display='物體.角度 = 0',
                note='設定角度',
                long_note=True))
        # temp_code_list.append(CodeNTuple(
        #         menu_display='角速度',
        #         code='物體.角速度',
        #         code_display='物體.角速度',
        #         note='角速度',
        #         long_note=False))
        temp_code_list.append(CodeNTuple(
                menu_display='  設定角速度',
                code='物體.角速度 = 100',
                code_display='物體.角速度 = 100',
                note='設定角速度',
                long_note=True))
        DropdownPostit(tab_name='physics', code_list = temp_code_list,
            postfix_enter=False).pack(side=tk.TOP, anchor='w', padx=2, pady=8)


        # dropdown list postit
        temp_code_list = []
        temp_code_list.append(CodeNTuple(
                menu_display='施加衝力',
                code='向量 = [0, 500]\n物體.施加衝力(向量)',
                code_display='向量 = [0, 500]\n物體.施加衝力(向量)',
                note='施加衝力',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='施加力量',
                code='向量 = [100000,0]\n物體.施加力量(向量)',
                code_display='向量 = [100000, 0]\n物體.施加力量(向量)',
                note='施加力量',
                long_note=True))

        DropdownPostit(tab_name='physics', code_list = temp_code_list,
            postfix_enter=False).pack(side=tk.TOP, anchor='w', padx=2, pady=8)


        # # dropdown list postit
        # temp_code_list = []
        # temp_code_list.append(CodeNTuple(
        #         menu_display='新增線段(兩點設值)',
        #         code='A點 = [100,100]\nB點 = [300,100]\n新增線段(A點, B點)\n',
        #         code_display='A點 = [100,100]\nB點 = [300,100]\n新增線段(A點, B點)',
        #         note='新增線段',
        #         long_note=False))
        # temp_code_list.append(CodeNTuple(
        #         menu_display='新增線段(寬)',
        #         code='新增線段(A點, B點, 寬=5)',
        #         code_display='新增線段(A點, B點, 寬=5)',
        #         note='新增線段',
        #         long_note=False))
        # DropdownPostit(tab_name='physics', code_list = temp_code_list,
        #     postfix_enter=False).pack(side=tk.TOP, anchor='w', padx=2, pady=8)

    
    def open_cubic6_texture(self):
        print('open cubic6 texture')


    def threed_tab_init(self):
        # title and setup tool
        tab = common_postit_tabs['threed']
        #example_vars = ['長','角度','邊','小海龜','Turtle','海龜模組'] 
        example_vars = ['x','y','z','物體','物體父' ,'物體母','座標','角度' ] 
        tab.popup_init(example_vars)

        f = font.Font(size=11, weight=font.NORMAL, family='Consolas')
        label =ttk.Label(common_postit_tabs['threed'].frame.interior, 
                text='【模擬3D】', 
                image= common_images['gear'],
                font=f,
                compound=tk.RIGHT,
                )                
        label.pack(side=tk.TOP, padx=5, pady=8, anchor='w')
        label.bind("<Button-1>", common_postit_tabs['threed'].popup)

        # dropdown list postit
        temp_code_list = []
        temp_code_list.append(CodeNTuple(
                menu_display='from 模擬3D模組 import *',
                code='from 模擬3D模組 import *',
                code_display='from 模擬3D模組 import *',
                note='從模擬3D模組匯入全部',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='from threed4t import *',
                code='from threed4t import *',
                code_display='from threed4t import *',
                note='從模擬3D模組匯入全部',
                long_note=True))
        # temp_code_list.append(CodeNTuple(
        #         menu_display='import 物理模組 ',
        #         code='import 物理模組',
        #         code_display='import 物理模組',
        #         note='匯入pie4t',
        #         long_note=True ))
        # temp_code_list.append(CodeNTuple(
        #         menu_display='  import pie4t ',
        #         code='import pie4t',
        #         code_display='import pie4t',
        #         note='匯入物理模組',
        #         long_note=True ))
        DropdownPostit(tab_name='threed', code_list = temp_code_list,
            postfix_enter=False).pack(side=tk.TOP, anchor='w', padx=2, pady=8)


        ttk.Separator(common_postit_tabs['threed'].frame.interior, orient=tk.HORIZONTAL
            ).pack(side=tk.TOP, fill=tk.X, padx=0, pady=10)
        f = font.Font(size=11, weight=font.NORMAL, family='Consolas')
        ttk.Label(common_postit_tabs['threed'].frame.interior, 
                    #text='='*6 +' 【 條件分支 】 '+'='*6,
                    text=' >> 3D舞台與主迴圈',
                    font=f,    
                    compound=tk.LEFT, 
                ).pack(side=tk.TOP, padx=5, pady=8, anchor='w')


        temp_code_list = []
        # temp_code_list.append(CodeNTuple(
        #         menu_display='舞台',
        #         code='舞台 = 物理引擎()',
        #         code_display='舞台 = 物理引擎()',
        #         note='舞台',
        #         long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='舞台(設定尺寸)',
                code='舞台 = 模擬3D引擎(400,600)',
                code_display='舞台 = 模擬3D引擎(400,600)',
                note='舞台(設定尺寸)',
                long_note=True))
        DropdownPostit(tab_name='threed', code_list = temp_code_list,
            postfix_enter=False).pack(side=tk.TOP, anchor='w', padx=2, pady=8)

        # dropdown list postit
        temp_code_list = []
        temp_code_list.append(CodeNTuple(
                menu_display='模擬進行中',
                code='模擬進行中()',
                code_display='模擬進行中()',
                note='(加在程式的最後一行)',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='  simulate',
                code='simulate()',
                code_display='simulate()',
                note='模擬進行中',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='模擬主迴圈',
                code='模擬主迴圈()',
                code_display='模擬主迴圈()',
                note='(加在程式的最後一行)',
                long_note=True))
        # temp_code_list.append(CodeNTuple(
        #         menu_display='  mainloop',
        #         code='mainloop()',
        #         code_display='mainloop()',
        #         note='主迴圈',
        #         long_note=False))
        DropdownPostit(tab_name='threed', code_list = temp_code_list,
            postfix_enter=False).pack(side=tk.TOP, anchor='w', padx=2, pady=8)

        ttk.Separator(common_postit_tabs['threed'].frame.interior, orient=tk.HORIZONTAL
            ).pack(side=tk.TOP, fill=tk.X, padx=0, pady=10)
        f = font.Font(size=11, weight=font.NORMAL, family='Consolas')
        ttk.Label(common_postit_tabs['threed'].frame.interior, 
                    #text='='*6 +' 【 條件分支 】 '+'='*6,
                    text=' >> 基本模型',
                    font=f,    
                    compound=tk.LEFT, 
                ).pack(side=tk.TOP, padx=5, pady=8, anchor='w')

        # dropdown list postit
        temp_code_list = []
        temp_code_list.append(CodeNTuple(
                menu_display='新增立方體',
                code='物體 = 新增立方體()',
                code_display='物體 = 新增立方體()',
                note='add_cube',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='新增球體',
                code='物體 = 新增球體()',
                code_display='物體 = 新增球體()',
                note='add_sphere',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='新增平面',
                code='物體 = 新增平面()',
                code_display='物體 = 新增平面()',
                note='add_quad',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='新增物體',
                code='物體 = 新增物體()',
                code_display='物體 = 新增物體()',
                note='新增物體(預設立方體)',
                long_note=True))
        DropdownPostit(tab_name='threed', code_list = temp_code_list,
            postfix_enter=False).pack(side=tk.TOP, anchor='w', padx=2, pady=8)


        # dropdown list postit
        temp_code_list = []
        temp_code_list.append(CodeNTuple(
                menu_display='設定顏色(紅)',
                code="物體.顏色 = color.red",
                code_display="物體.顏色 = color.red",
                note='設定顏色(紅)',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='        (綠)',
                code="物體.顏色 = color.green",
                code_display="物體.顏色 = color.green",
                note='設定顏色(綠)',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='        (藍)',
                code="物體.顏色 = color.blue",
                code_display="物體.顏色 = color.blue",
                note='設定顏色(藍)',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='        (黃)',
                code="物體.顏色 = color.yellow",
                code_display="物體.顏色 = color.yellow",
                note='設定顏色(黃)',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='        (橘)',
                code="物體.顏色 = color.orange",
                code_display="物體.顏色 = color.orange",
                note='設定顏色(橘)',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='        (rgba)',
                code="物體.顏色 = color.rgba(50,0,0,255)",
                code_display="物體.顏色 = color.rgba(50,0,0,255)",
                note='設定顏色(rgba)',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='        (隨機)',
                code="物體.顏色 = color.random_color()",
                code_display="物體.顏色 = color.random_color()",
                note='設定顏色(隨機)',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='設定顏色動畫(持續)',
                code="物體.顏色動畫([255,0,0,255], 持續=1)",
                code_display="物體.顏色動畫([255,0,0,255], 持續=1)",
                note='設定顏色動畫',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='設定顏色動畫(延遲與持續)',
                code="顏色 = 255,0,0,255\n物體.顏色動畫(顏色, 延遲=0, 持續=1)",
                code_display="顏色 = 255,0,0,255\n物體.顏色動畫(顏色, 延遲=0, 持續=1)",
                note='設定顏色動畫(延遲與持續)',
                long_note=True))
        DropdownPostit(tab_name='threed', code_list = temp_code_list,
            postfix_enter=False).pack(side=tk.TOP, anchor='w', padx=2, pady=8)

        # dropdown list postit
        temp_code_list = []
        temp_code_list.append(CodeNTuple(
                menu_display='設定模型',
                code="物體.模型 = ''",
                code_display="物體.模型 = ''",
                note='model',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='設定紋理',
                code="物體.紋理 = ''",
                code_display="物體.紋理 = ''",
                note='texture',
                long_note=True))
        DropdownPostit(tab_name='threed', code_list = temp_code_list,
            postfix_enter=False).pack(side=tk.TOP, anchor='w', padx=2, pady=8)


        ttk.Separator(common_postit_tabs['threed'].frame.interior, orient=tk.HORIZONTAL
            ).pack(side=tk.TOP, fill=tk.X, padx=0, pady=10)
        f = font.Font(size=11, weight=font.NORMAL, family='Consolas')
        ttk.Label(common_postit_tabs['threed'].frame.interior, 
                    #text='='*6 +' 【 條件分支 】 '+'='*6,
                    text=' >> 特定模型與紋理',
                    font=f,    
                    compound=tk.LEFT, 
                ).pack(side=tk.TOP, padx=5, pady=8, anchor='w')

        # dropdown list postit
        temp_code_list = []
        temp_code_list.append(CodeNTuple(
                menu_display='新增立方體6面',
                code='物體 = 新增立方體6面()',
                code_display='物體 = 新增立方體6面()',
                note='add_cubic6',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='新增球體內面',
                code='物體 = 新增球體內面()',
                code_display='物體 = 新增球體內面()',
                note='add_sphere_inward',
                long_note=True))
        DropdownPostit(tab_name='threed', code_list = temp_code_list,
            postfix_enter=False).pack(side=tk.TOP, anchor='w', padx=2, pady=8)

        f = font.Font(size=11, weight=font.NORMAL, family='Consolas')
        btn =tk.Button(common_postit_tabs['threed'].frame.interior, 
                text='開啟立方體6面紋理', 
                command=self.open_cubic6_texture, 
                #image= common_images['gear'],
                font=f,
                #compound=tk.RIGHT,
                )                
        btn.pack(side=tk.TOP, padx=5, pady=8, anchor='w')


        ttk.Separator(common_postit_tabs['threed'].frame.interior, orient=tk.HORIZONTAL
            ).pack(side=tk.TOP, fill=tk.X, padx=0, pady=10)
        f = font.Font(size=11, weight=font.NORMAL, family='Consolas')
        ttk.Label(common_postit_tabs['threed'].frame.interior, 
                    #text='='*6 +' 【 條件分支 】 '+'='*6,
                    text=' >> 3d物件設定與屬性',
                    font=f,    
                    compound=tk.LEFT, 
                ).pack(side=tk.TOP, padx=5, pady=8, anchor='w')

        # dropdown list postit
        temp_code_list = []
        temp_code_list.append(CodeNTuple(
                menu_display='設定中心點偏移',
                code="物體.中心點偏移 = 0,0,0",
                code_display="物體.中心點偏移 = 0,0,0",
                note='origin',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='設定上層物件',
                code="物體.上層物件 = ",
                code_display="物體.上層物件 = ",
                note='parent',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='設定有效狀態',
                code="物體.有效狀態 = True",
                code_display="物體.有效狀態 = True",
                note='enabled',
                long_note=True))
        DropdownPostit(tab_name='threed', code_list = temp_code_list,
            postfix_enter=False).pack(side=tk.TOP, anchor='w', padx=2, pady=8)







        temp_code_list = []
        temp_code_list.append(CodeNTuple(
                menu_display='設定位置x (右左)',
                code="物體.位置x = 0",
                code_display="物體.位置x = 0",
                note='設定x (右左)',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='設定位置y (上下)',
                code="物體.位置y = 0",
                code_display="物體.位置y = 0",
                note='設定位置y (上下)',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='設定位置z (前後)',
                code="物體.位置z = 0",
                code_display="物體.位置z = 0",
                note='設定位置z (前後)',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='設定位置(xyz同時)',
                code="物體.位置 = 0,0,0",
                code_display="物體.位置 = 0,0,0",
                note='設定位置(右左,上下,前後)',
                long_note=True))
        # temp_code_list.append(CodeNTuple(
        #         menu_display='設定全域位置x (右左)',
        #         code="物體.全域位置x = 0",
        #         code_display="物體.全域位置x = 0",
        #         note='設定全域位置x (右左)',
        #         long_note=True))
        # temp_code_list.append(CodeNTuple(
        #         menu_display='設定全域位置y (上下)',
        #         code="物體.全域位置y = 0",
        #         code_display="物體.全域位置y = 0",
        #         note='設定全域位置y (上下)',
        #         long_note=True))
        # temp_code_list.append(CodeNTuple(
        #         menu_display='設定全域位置z (前後)',
        #         code="物體.全域位置z = 0",
        #         code_display="物體.全域位置z = 0",
        #         note='設定全域位置z (前後)',
        #         long_note=True))       
        temp_code_list.append(CodeNTuple(
                menu_display='設定全域位置(xyz同時)',
                code="物體.全域位置 = 0,0,0",
                code_display="物體.全域位置 = 0,0,0",
                note='設定全域位置(右左,上下,前後)',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='設定位置動畫(持續)',
                code="物體.位置動畫([1,0,0], 持續=1)",
                code_display="物體.位置動畫([1,0,0], 持續=1)",
                note='設定位置動畫',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='設定位置動畫(延遲與持續)',
                code="座標 = 1,0,0\n物體.位置動畫(座標, 延遲=0, 持續=1)",
                code_display="座標 = 1,0,0\n物體.位置動畫(座標, 延遲=0, 持續=1)",
                note='設定位置動畫(延遲與持續)',
                long_note=True))
        DropdownPostit(tab_name='threed', code_list = temp_code_list,
            postfix_enter=False).pack(side=tk.TOP, anchor='w', padx=2, pady=8)




        temp_code_list = []
        temp_code_list.append(CodeNTuple(
                menu_display='設定縮放x ',
                code="物體.縮放x = 1",
                code_display="物體.縮放x = 1",
                note='設定縮放x ',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='設定縮放y ',
                code="物體.縮放y = 1",
                code_display="物體.縮放y = 1",
                note='設定縮放y ',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='設定縮放z ',
                code="物體.縮放z = 1",
                code_display="物體.縮放z = 1",
                note='設定縮放z ',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='設定縮放 (3軸同時)',
                code="物體.縮放 = 1, 1, 1",
                code_display="物體.縮放 = 1, 1, 1",
                note='設定縮放 (3軸同時)',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='設定全域縮放 (3軸同時)',
                code="物體.全域縮放 = 1, 1, 1",
                code_display="物體.全域縮放 = 1, 1, 1",
                note='設定全域縮放 (3軸同時)',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='設定縮放動畫(持續)',
                code="物體.縮放動畫([2,1,1], 持續=1)",
                code_display="物體.縮放動畫([2,1,1], 持續=1)",
                note='設定縮放動畫',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='設定縮放動畫(延遲與持續)',
                code="比例 = 2,1,1\n物體.縮放動畫(比例, 延遲=0, 持續=1)",
                code_display="比例 = 2,1,1\n物體.縮放動畫(比例, 延遲=0, 持續=1)",
                note='設定縮放動畫(延遲與持續)',
                long_note=True))
        DropdownPostit(tab_name='threed', code_list = temp_code_list,
            postfix_enter=False).pack(side=tk.TOP, anchor='w', padx=2, pady=8)


        temp_code_list = []
        temp_code_list.append(CodeNTuple(
                menu_display='設定旋轉x (x軸順逆時針)',
                code="物體.旋轉x = 0",
                code_display="物體.旋轉x = 0",
                note='設定旋轉x (x軸順逆時針)',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='設定旋轉y (y軸順逆時針)',
                code="物體.旋轉y = 0",
                code_display="物體.旋轉y = 0",
                note='設定旋轉y (y軸順逆時針)',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='設定旋轉z (z軸順逆時針)',
                code="物體.旋轉z = 0",
                code_display="物體.旋轉z = 0",
                note='設定旋轉z (z軸順逆時針)',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='設定旋轉 (3軸)',
                code="物體.旋轉 = 0, 0, 0",
                code_display="物體.旋轉 = 0, 0, 0",
                note='設定旋轉 (3軸)',
                long_note=True))
        # temp_code_list.append(CodeNTuple(
        #         menu_display='設定全域旋轉x (x軸順逆時針)',
        #         code="物體.全域旋轉x = 0",
        #         code_display="物體.全域旋轉x = 0",
        #         note='設定全域旋轉x (x軸順逆時針)',
        #         long_note=True))
        # temp_code_list.append(CodeNTuple(
        #         menu_display='設定全域旋轉y (y軸順逆時針)',
        #         code="物體.全域旋轉y = 0",
        #         code_display="物體.全域旋轉y = 0",
        #         note='設定全域旋轉y (y軸順逆時針)',
        #         long_note=True))
        # temp_code_list.append(CodeNTuple(
        #         menu_display='設定全域旋轉z (z軸順逆時針)',
        #         code="物體.全域旋轉z = 0",
        #         code_display="物體.全域旋轉z = 0",
        #         note='設定全域旋轉z (z軸順逆時針)',
        #         long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='設定全域旋轉 (3軸)',
                code="物體.全域旋轉 = 0, 0, 0",
                code_display="物體.全域旋轉 = 0, 0, 0",
                note='設定全域旋轉 (3軸)',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='設定旋轉動畫(持續)',
                code="物體.旋轉動畫([90,0,0], 持續=1)",
                code_display="物體.旋轉動畫([2,0,0], 持續=1)",
                note='設定旋轉動畫',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='設定旋轉動畫(延遲與持續)',
                code="角度 = 90,0,0\n物體.旋轉動畫(角度, 延遲=0, 持續=1)",
                code_display="角度 = 90,0,0\n物體.旋轉動畫(角度, 延遲=0, 持續=1)",
                note='設定旋轉動畫(延遲與持續)',
                long_note=True))
        DropdownPostit(tab_name='threed', code_list = temp_code_list,
            postfix_enter=False).pack(side=tk.TOP, anchor='w', padx=2, pady=8)


        ttk.Separator(common_postit_tabs['threed'].frame.interior, orient=tk.HORIZONTAL
            ).pack(side=tk.TOP, fill=tk.X, padx=0, pady=10)
        f = font.Font(size=11, weight=font.NORMAL, family='Consolas')
        ttk.Label(common_postit_tabs['threed'].frame.interior, 
                    #text='='*6 +' 【 條件分支 】 '+'='*6,
                    text=' >> 互動事件',
                    font=f,    
                    compound=tk.LEFT, 
                ).pack(side=tk.TOP, padx=5, pady=8, anchor='w')

        temp_code_list = []
        temp_code_list.append(CodeNTuple(
                menu_display='當按下時',
                code='def 當按下時(按鍵):\npass\n',
                code_display='def 當按下時(按鍵):\n    pass',
                note='on key press',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='當放開時',
                code='def 當放開時(按鍵):\npass\n',
                code_display='def 當放開時(按鍵):\n    pass',
                note='on key release',
                long_note=True))
        # temp_code_list.append(CodeNTuple(
        #         menu_display='按住鍵盤時',
        #         code='def 按住鍵盤時(按鍵):\npass\n',
        #         code_display='def 按住鍵盤時(按鍵):\n    pass',
        #         note='on key hold',
        #         long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='  是滑鼠左鍵?',
                code="if 按鍵 == 'left mouse down' :\npass",
                code_display="if 按鍵 == 'left mouse down' :\n    pass",
                note='是滑鼠左鍵?',
                long_note=True))

        temp_code_list.append(CodeNTuple(
                menu_display='  是空白鍵?',
                code="if 按鍵 == 'space' :\npass",
                code_display="if 按鍵 == 'space' :\n    pass",
                note='是空白鍵?',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='  是Enter鍵?',
                code="if 按鍵 == 'enter' :\npass",
                code_display="if 按鍵 == 'enter' :\n    pass",
                note='是Enter鍵?',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='  是向右鍵?',
                code="if 按鍵 == 'right arrow' :\npass",
                code_display="if 按鍵 == 'right arrow' :\n    pass",
                note='是向右鍵?',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='  是向左鍵?',
                code="if 按鍵 == 'left arrow' :\npass",
                code_display="if 按鍵 == 'left arrow' :\n    pass",
                note='是向左鍵?',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='  是向上鍵?',
                code="if 按鍵 == 'up arrow' :\npass",
                code_display="if 按鍵 == 'up arrow' :\n    pass",
                note='是向上鍵?',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='  是向下鍵?',
                code="if 按鍵 == 'down arrow' :\npass",
                code_display="if 按鍵 == 'down arrow' :\n    pass",
                note='是向下鍵?',
                long_note=True))
        DropdownPostit(tab_name='threed', code_list = temp_code_list,
            postfix_enter=False).pack(side=tk.TOP, anchor='w', padx=2, pady=8)


        temp_code_list = []
        temp_code_list.append(CodeNTuple(
                menu_display='當更新時',
                code='def 當更新時(時間差):\npass\n',
                code_display='def 當更新時(時間差):\n    pass',
                note='update',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='按住空白鍵？',
                code="if 按住的鍵['space']:\npass\n",
                code_display="if 按住的鍵['space']:\n    pass",
                note='按住空白鍵？',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='按住Enter鍵？',
                code="if 按住的鍵['enter']:\npass\n",
                code_display="if 按住的鍵['enter']:\n    pass",
                note='按住Enter鍵？',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='按住向右鍵？',
                code="if 按住的鍵['right arrow']:\npass\n",
                code_display="if 按住的鍵['right arrow']:\n    pass",
                note='按住向右鍵？',
                long_note=True))        
        temp_code_list.append(CodeNTuple(
                menu_display='按住向左鍵？',
                code="if 按住的鍵['left arrow']:\npass\n",
                code_display="if 按住的鍵['left arrow']:\n    pass",
                note='按住向左鍵？',
                long_note=True)) 
        temp_code_list.append(CodeNTuple(
                menu_display='按住向上鍵？',
                code="if 按住的鍵['up arrow']:\npass\n",
                code_display="if 按住的鍵['up arrow']:\n    pass",
                note='按住向上鍵？',
                long_note=True)) 
        temp_code_list.append(CodeNTuple(
                menu_display='按住向下鍵？',
                code="if 按住的鍵['down arrow']:\npass\n",
                code_display="if 按住的鍵['down arrow']:\n    pass",
                note='按住向下鍵？',
                long_note=True)) 
        DropdownPostit(tab_name='threed', code_list = temp_code_list,
            postfix_enter=False).pack(side=tk.TOP, anchor='w', padx=2, pady=8)


        temp_code_list = []
        temp_code_list.append(CodeNTuple(
                menu_display='滑鼠位置',
                code='滑鼠.位置',
                code_display='滑鼠.位置',
                note='mouse position',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='滑鼠碰觸物體',
                code='滑鼠.碰觸物體',
                code_display='滑鼠.碰觸物體',
                note='hovered entity',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='滑鼠碰觸點',
                code='滑鼠.碰觸點',
                code_display='滑鼠.碰觸點',
                note='hovered point',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='滑鼠按下左鍵',
                code='滑鼠.按下左鍵',
                code_display='滑鼠.按下左鍵',
                note='left mouse down',
                long_note=True))
        DropdownPostit(tab_name='threed', code_list = temp_code_list,
            postfix_enter=False).pack(side=tk.TOP, anchor='w', padx=2, pady=8)

    def auto_tab_init(self):
        # title and setup tool
        #tab = common_postit_tabs['auto']
        #example_vars = ['',] 
        #tab.popup_init(example_vars)

        f = font.Font(size=11, weight=font.NORMAL, family='Consolas')
        label =ttk.Label(common_postit_tabs['auto'].frame.interior, 
                text='【PyAutoGui模組】', 
                #image= common_images['gear'],
                font=f,
                compound=tk.RIGHT,
                )                
        label.pack(side=tk.TOP, padx=5, pady=8,anchor='w')
        #label.bind("<Button-1>", common_postit_tabs['auto'].popup)        



        # dropdown list postit
        temp_code_list = []
        temp_code_list.append(CodeNTuple(
                menu_display='匯入pyautogui模組',
                code='import pyautogui as 自動',
                code_display='import pyautogui as 自動',
                note='匯入pyautogui模組',
                long_note=True))
        DropdownPostit(tab_name='auto', code_list = temp_code_list,
            postfix_enter=False).pack(side=tk.TOP, anchor='w', padx=2, pady=8)


        # separator and note
        ttk.Separator(common_postit_tabs['auto'].frame.interior, orient=tk.HORIZONTAL
            ).pack(side=tk.TOP, fill=tk.X, padx=0, pady=10)
        f = font.Font(size=11, weight=font.NORMAL, family='Consolas')
        ttk.Label(common_postit_tabs['auto'].frame.interior, 
                    
                    text=' >> 設定與資訊',
                    font=f,   
                    compound=tk.LEFT, 
                ).pack(side=tk.TOP, padx=5, pady=8, anchor='w')


        # dropdown list postit
        temp_code_list = []
        temp_code_list.append(CodeNTuple(
                menu_display='螢幕大小 size',
                code='自動.size()',
                code_display='自動.size()',
                note='螢幕大小',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='查詢滑鼠位置 position',
                code='自動.position()',
                code_display='自動.position()',
                note='查詢滑鼠位置',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='在螢幕內嗎 onScreen',
                code='自動.onScreen(100, 100)',
                code_display='自動.onScreen(100, 100)',
                note='在螢幕內嗎',
                long_note=True))
        DropdownPostit(tab_name='auto', code_list = temp_code_list,
            postfix_enter=False).pack(side=tk.TOP, anchor='w', padx=2, pady=8)

        # dropdown list postit
        temp_code_list = []
        temp_code_list.append(CodeNTuple(
                menu_display='每次暫停(秒) PAUSE',
                code='自動.PAUSE = 1',
                code_display='自動.PAUSE = 1',
                note='每次暫停(秒)',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='失效安全  FAILSAFE',
                code='自動.FAILSAFE = True',
                code_display='自動.FAILSAFE = True',
                note='失效安全(移到螢幕左上角)',
                long_note=True))
        DropdownPostit(tab_name='auto', code_list = temp_code_list,
            postfix_enter=False).pack(side=tk.TOP, anchor='w', padx=2, pady=8)


        # separator and note
        ttk.Separator(common_postit_tabs['auto'].frame.interior, orient=tk.HORIZONTAL
            ).pack(side=tk.TOP, fill=tk.X, padx=0, pady=10)
        f = font.Font(size=11, weight=font.NORMAL, family='Consolas')
        ttk.Label(common_postit_tabs['auto'].frame.interior, 
                    
                    text=' >> 滑鼠操作',
                    font=f,   
                    compound=tk.LEFT, 
                ).pack(side=tk.TOP, padx=5, pady=8, anchor='w')

 
        # dropdown list postit
        temp_code_list = [] 
        temp_code_list.append(CodeNTuple(
                menu_display='移動滑鼠(到座標)',
                code='自動.moveTo(100, 100, 2)',
                code_display='自動.moveTo(100, 100, 1)',
                note='移動滑鼠(x座標, y座標, 幾秒)',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='移動滑鼠(距離)',
                code='自動.moveRel(0, 50, 1)',
                code_display='自動.moveRel(0, 50, 1)',
                note='移動滑鼠(x距離, y距離, 幾秒)',
                long_note=True))
        DropdownPostit(tab_name='auto', code_list = temp_code_list,
            postfix_enter=False).pack(side=tk.TOP, anchor='w', padx=2, pady=8)                

 
        # dropdown list postit
        temp_code_list = []
        temp_code_list.append(CodeNTuple(
                menu_display='點擊滑鼠(滑鼠按鍵)',
                code="自動.click(button='left')",
                code_display="自動.click(button='left')",
                note='點擊滑鼠(滑鼠按鍵)',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='拖曳滑鼠(到座標)',
                code='自動.dragTo(100, 100, 2)',
                code_display='自動.dragTo(100, 100, 2)',
                note='拖曳滑鼠(x座標, y座標, 幾秒)',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='拖曳滑鼠(距離)',
                code='自動.dragRel(0, 50, 1)',
                code_display='自動.dragRel(0, 50, 1)',
                note='拖曳滑鼠(x距離, y距離, 幾秒)',
                long_note=True))
        DropdownPostit(tab_name='auto', code_list = temp_code_list,
            postfix_enter=False).pack(side=tk.TOP, anchor='w', padx=2, pady=8)

        # separator and note
        ttk.Separator(common_postit_tabs['auto'].frame.interior, orient=tk.HORIZONTAL
            ).pack(side=tk.TOP, fill=tk.X, padx=0, pady=10)
        f = font.Font(size=11, weight=font.NORMAL, family='Consolas')
        ttk.Label(common_postit_tabs['auto'].frame.interior, 
                    
                    text=' >> 鍵盤操作',
                    font=f,   
                    compound=tk.LEFT, 
                ).pack(side=tk.TOP, padx=5, pady=8, anchor='w')

        # dropdown list postit
        temp_code_list = []
        temp_code_list.append(CodeNTuple(
                menu_display='按鍵 perss',
                code="自動.press('space')",
                code_display="自動.press('space')",
                note='按鍵',
                long_note=True))

        temp_code_list.append(CodeNTuple(
                menu_display='按著鍵 keyDown',
                code="自動.keyDown('space')",
                code_display="自動.keyDown('space')",
                note='按著鍵',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='放開鍵 keyUp',
                code="自動.keyUp('space')",
                code_display="自動.keyUp('space')",
                note='放開鍵',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='組合鍵 hotkey',
                code="自動.hotkey('ctrl','v')",
                code_display="自動.hotkey('ctrl','v')",
                note='組合鍵',
                long_note=True))
        DropdownPostit(tab_name='auto', code_list = temp_code_list,
            postfix_enter=False).pack(side=tk.TOP, anchor='w', padx=2, pady=8)

        # dropdown list postit
        temp_code_list = []
        temp_code_list.append(CodeNTuple(
                menu_display="空白鍵 space",
                code="'space'",
                code_display="'space'",
                note='空白鍵',
                long_note=False))
        temp_code_list.append(CodeNTuple(
                menu_display="輸入鍵 enter",
                code="'enter'",
                code_display="'enter'",
                note='空白鍵',
                long_note=False))
        temp_code_list.append(CodeNTuple(
                menu_display="控制鍵 ctrl",
                code="'ctrl'",
                code_display="'ctrl'",
                note='空白鍵',
                long_note=False))
        temp_code_list.append(CodeNTuple(
                menu_display="shift鍵 shift",
                code="'shift'",
                code_display="'shift'",
                note='shift鍵',
                long_note=False))
        temp_code_list.append(CodeNTuple(
                menu_display="字母鍵 a",
                code="'a'",
                code_display="'a'",
                note='空白鍵',
                long_note=False))
        temp_code_list.append(CodeNTuple(
                menu_display="向上鍵 up",
                code="'up'",
                code_display="'up'",
                note='向上鍵',
                long_note=False))
        temp_code_list.append(CodeNTuple(
                menu_display='鍵盤列表 KEYBOARD_KEYS',
                code='自動.KEYBOARD_KEYS',
                code_display='自動.KEYBOARD_KEYS',
                note='鍵盤列表',
                long_note=True))
        DropdownPostit(tab_name='auto', code_list = temp_code_list,
            postfix_enter=False).pack(side=tk.TOP, anchor='w', padx=2, pady=8)

        # separator and note
        ttk.Separator(common_postit_tabs['auto'].frame.interior, orient=tk.HORIZONTAL
            ).pack(side=tk.TOP, fill=tk.X, padx=0, pady=10)
        f = font.Font(size=11, weight=font.NORMAL, family='Consolas')
        label =ttk.Label(common_postit_tabs['auto'].frame.interior, 
                text='【pyperclip模組】', 
                #image= common_images['gear'],
                font=f,
                compound=tk.RIGHT,
                )                
        label.pack(side=tk.TOP, padx=5, pady=8,anchor='w')



        ttk.Label(common_postit_tabs['auto'].frame.interior, 
                    
                    text=' >> 剪貼簿',
                    font=f,   
                    compound=tk.LEFT, 
                ).pack(side=tk.TOP, padx=5, pady=8, anchor='w')

        # dropdown list postit
        temp_code_list = []
        temp_code_list.append(CodeNTuple(
                menu_display='匯入pyperclip模組',
                code='import pyperclip as 剪貼簿',
                code_display='import pyperclip as 剪貼簿',
                note='匯入pyperclip模組',
                long_note=True))
        DropdownPostit(tab_name='auto', code_list = temp_code_list,
            postfix_enter=False).pack(side=tk.TOP, anchor='w', padx=2, pady=8)


        # dropdown list postit
        temp_code_list = []
        temp_code_list.append(CodeNTuple(
                menu_display='字串複製到剪貼簿 copy',
                code='剪貼簿.copy("你好")',
                code_display='剪貼簿.copy("你好")',
                note='字串複製到剪貼簿',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='從剪貼簿傳回字串 paste',
                code='文字 = 剪貼簿.paste()',
                code_display='文字 = 剪貼簿.paste()',
                note='從剪貼簿傳回字串',
                long_note=True))
        DropdownPostit(tab_name='auto', code_list = temp_code_list,
            postfix_enter=False).pack(side=tk.TOP, anchor='w', padx=2, pady=8)


    def numpy_tab_init(self):
         # title and setup tool
        tab = common_postit_tabs['numpy']
        example_vars = ['陣列','行1','行2','列1','列2'] 
        tab.popup_init(example_vars)

        f = font.Font(size=11, weight=font.NORMAL, family='Consolas')
        label =ttk.Label(common_postit_tabs['numpy'].frame.interior, 
                text='【多維陣列numpy】', 
                image= common_images['gear'],
                font=f,
                compound=tk.RIGHT,
                )                
        label.pack(side=tk.TOP, padx=5, pady=8,anchor='w')
        label.bind("<Button-1>", common_postit_tabs['numpy'].popup)      

        # dropdown list postit
        temp_code_list = []
        temp_code_list.append(CodeNTuple(
                menu_display='匯入numpy模組',
                code='import numpy as 多維陣列',
                code_display='import numpy as 多維陣列',
                note='匯入numpy模組',
                long_note=True))
        DropdownPostit(tab_name='numpy', code_list = temp_code_list,
            postfix_enter=False).pack(side=tk.TOP, anchor='w', padx=2, pady=8)

        # separator and note
        ttk.Separator(common_postit_tabs['numpy'].frame.interior, orient=tk.HORIZONTAL
            ).pack(side=tk.TOP, fill=tk.X, padx=0, pady=10)
        f = font.Font(size=11, weight=font.NORMAL, family='Consolas')
        label =ttk.Label(common_postit_tabs['numpy'].frame.interior, 
                text=' >> 建立陣列', 
                #image= common_images['gear'],
                font=f,
                compound=tk.RIGHT,
                )                
        label.pack(side=tk.TOP, padx=5, pady=8,anchor='w')


        # dropdown list postit
        temp_code_list = []
        temp_code_list.append(CodeNTuple(
                menu_display='建立數列陣列 arange',
                code='陣列 = 多維陣列.arange(4)',
                code_display='陣列 = 多維陣列.arange(4)',
                note='建立數列陣列(同range)',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='建立陣列 array',
                code='陣列 = 多維陣列.array([1,2,3,4])',
                code_display='陣列 = 多維陣列.array([1,2,3,4])',
                note='建立陣列(清單)',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='建立均零陣列 array',
                code='陣列 = 多維陣列.zeros([2,2])',
                code_display='陣列 = 多維陣列.zeros([2,2])',
                note='建立均零陣列(形狀)',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='建立均一陣列 array',
                code='陣列 = 多維陣列.ones([2,2])',
                code_display='陣列 = 多維陣列.ones([2,2])',
                note='建立均一陣列(形狀)',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='建立隨機陣列 randint',
                code='陣列=多維陣列.random.randint(10,50,size=[5,5])',
                code_display='陣列=多維陣列.random.randint(10,50,size=[5,5])',
                note='建立隨機陣列(隨機範圍, 大小)',
                long_note=True))
        DropdownPostit(tab_name='numpy', code_list = temp_code_list,
            postfix_enter=False).pack(side=tk.TOP, anchor='w', padx=2, pady=8)

        # separator and note
        ttk.Separator(common_postit_tabs['numpy'].frame.interior, orient=tk.HORIZONTAL
            ).pack(side=tk.TOP, fill=tk.X, padx=0, pady=10)
        label =ttk.Label(common_postit_tabs['numpy'].frame.interior, 
                text=' >> 陣列屬性', 
                #image= common_images['gear'],
                font=f,
                compound=tk.RIGHT,
                )                
        label.pack(side=tk.TOP, padx=5, pady=8,anchor='w')

        # dropdown list postit
        temp_code_list = []
        temp_code_list.append(CodeNTuple(
                menu_display='維度 ndim',
                code='陣列.ndim',
                code_display='陣列.ndim',
                note='維度 ndim',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='形狀 shape',
                code='陣列.shape',
                code_display='陣列.shape',
                note='形狀 shape',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='資料類型 dtype',
                code='陣列.dtype',
                code_display='陣列.dtype',
                note='資料類型 dtype',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='資料數量 size',
                code='陣列.size',
                code_display='陣列.size',
                note='資料數量 size',
                long_note=True))
        DropdownPostit(tab_name='numpy', code_list = temp_code_list,
            postfix_enter=False).pack(side=tk.TOP, anchor='w', padx=2, pady=8)

        # separator and note
        ttk.Separator(common_postit_tabs['numpy'].frame.interior, orient=tk.HORIZONTAL
            ).pack(side=tk.TOP, fill=tk.X, padx=0, pady=10)
        label =ttk.Label(common_postit_tabs['numpy'].frame.interior, 
                text=' >> 陣列操作', 
                #image= common_images['gear'],
                font=f,
                compound=tk.RIGHT,
                )                
        label.pack(side=tk.TOP, padx=5, pady=8,anchor='w')

        # dropdown list postit
        temp_code_list = []
        temp_code_list.append(CodeNTuple(
                menu_display='改變陣列形狀 reshape',
                code='陣列 = 陣列.reshape([2,2])',
                code_display='陣列 = 陣列.reshape([2,2])',
                note='改變陣列形狀(形狀)',
                long_note=True))
        DropdownPostit(tab_name='numpy', code_list = temp_code_list,
            postfix_enter=False).pack(side=tk.TOP, anchor='w', padx=2, pady=8)

        # dropdown list postit
        temp_code_list = []
        temp_code_list.append(CodeNTuple(
                menu_display='唯一值(去除重複) unique',
                code='唯一值陣列 = 多維陣列.unique(陣列)',
                code_display='唯一值陣列 = 多維陣列.unique(陣列)',
                note='唯一值(去除重複)',
                long_note=True))
        DropdownPostit(tab_name='numpy', code_list = temp_code_list,
            postfix_enter=False).pack(side=tk.TOP, anchor='w', padx=2, pady=8)


        temp_code_list = []
        temp_code_list.append(CodeNTuple(
                menu_display='改變類型 8位元正整數',
                code="陣列 = 陣列.astype('uint8')",
                code_display="陣列 = 陣列.astype('uint8')",
                note='改變類型 8位元正整數',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='改變類型 16位元正整數',
                code="陣列 = 陣列.astype('uint16')",
                code_display="陣列 = 陣列.astype('uint16')",
                note='改變類型 16位元正整數',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='改變類型 16位元整數',
                code="陣列 = 陣列.astype('int16')",
                code_display="陣列 = 陣列.astype('int16')",
                note='改變類型 16位元整數',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='改變類型 32位元浮點數',
                code="陣列 = 陣列.astype('float32')",
                code_display="陣列 = 陣列.astype('float32')",
                note='改變類型 32位元浮點數',
                long_note=True))
        DropdownPostit(tab_name='numpy', code_list = temp_code_list,
            postfix_enter=False).pack(side=tk.TOP, anchor='w', padx=2, pady=8)

        # separator and note
        ttk.Separator(common_postit_tabs['numpy'].frame.interior, orient=tk.HORIZONTAL
            ).pack(side=tk.TOP, fill=tk.X, padx=0, pady=10)
        label =ttk.Label(common_postit_tabs['numpy'].frame.interior, 
                text=' >> 陣列切片', 
                #image= common_images['gear'],
                font=f,
                compound=tk.RIGHT,
                )                
        label.pack(side=tk.TOP, padx=5, pady=8,anchor='w')

        temp_code_list = []
        temp_code_list.append(CodeNTuple(
                menu_display='元素取值',
                code="陣列[0, 0]",
                code_display="陣列[0, 0]",
                note='元素取值 [直行,橫列]',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='        設值',
                code="陣列[0, 0] = 3",
                code_display="陣列[0, 0] = 3",
                note='元素設值 [直行,橫列]',
                long_note=True))

        DropdownPostit(tab_name='numpy', code_list = temp_code_list,
            postfix_enter=False).pack(side=tk.TOP, anchor='w', padx=2, pady=8)


        temp_code_list = []
        temp_code_list.append(CodeNTuple(
                menu_display='切片取值',
                code="陣列[0:2, 0:2]",
                code_display="陣列[0:2, 0:2]",
                note='切片取值 [行切片,列切片]',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='        設值',
                code="陣列[0:2, 0:2] = 5",
                code_display="陣列[0:2, 0:2] = 5",
                note='切片設值 [行切片,列切片]',
                long_note=True))
        DropdownPostit(tab_name='numpy', code_list = temp_code_list,
            postfix_enter=False).pack(side=tk.TOP, anchor='w', padx=2, pady=8)

    def cv_tab_init(self):
        # title and setup tool
        tab = common_postit_tabs['cv']
        example_vars = ['陣列','行1','行2','列1','列2'] 
        tab.popup_init(example_vars)

        f = font.Font(size=11, weight=font.NORMAL, family='Consolas')
        label =ttk.Label(common_postit_tabs['cv'].frame.interior, 
                text='【電腦視覺cv】', 
                image= common_images['gear'],
                font=f,
                compound=tk.RIGHT,
                )                
        label.pack(side=tk.TOP, padx=5, pady=8,anchor='w')
        label.bind("<Button-1>", common_postit_tabs['cv'].popup)   




        # dropdown list postit
        temp_code_list = []
        temp_code_list.append(CodeNTuple(
                menu_display='從電腦視覺模組匯入全部',
                code='from 電腦視覺模組 import *',
                code_display='from 電腦視覺模組 import *',
                note='從電腦視覺模組匯入全部',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='從cv4t匯入全部',
                code='from cv4t import *',
                code_display='from cv4t import *',
                note='從cv4t匯入全部',
                long_note=True))
        DropdownPostit(tab_name='cv', code_list = temp_code_list,
            postfix_enter=False).pack(side=tk.TOP, anchor='w', padx=2, pady=8)

        # separator and note
        ttk.Separator(common_postit_tabs['cv'].frame.interior, orient=tk.HORIZONTAL
            ).pack(side=tk.TOP, fill=tk.X, padx=0, pady=10)
        f = font.Font(size=11, weight=font.NORMAL, family='Consolas')
        ttk.Label(common_postit_tabs['cv'].frame.interior, 
                    
                    text=' >> 圖片讀取與儲存',
                    font=f,   
                    compound=tk.LEFT, 
                ).pack(side=tk.TOP, padx=5, pady=8, anchor='w')

        # dropdown list postit
        temp_code_list = []
        temp_code_list.append(CodeNTuple(
                menu_display='讀取圖片灰階',
                code="陣列 = 讀取圖片灰階('檔名.類型')",
                code_display="陣列 = 讀取圖片灰階('檔名.類型')",
                note='讀取圖片灰階(檔名字串)',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='讀取圖片彩色',
                code="陣列 = 讀取圖片彩色('檔名.類型')",
                code_display="陣列 = 讀取圖片彩色('檔名.類型')",
                note='讀取圖片彩色(檔名字串)',
                long_note=True))
        DropdownPostit(tab_name='cv', code_list = temp_code_list,
            postfix_enter=False).pack(side=tk.TOP, anchor='w', padx=2, pady=8)

        # dropdown list postit
        temp_code_list = []
        temp_code_list.append(CodeNTuple(
                menu_display='儲存圖片',
                code="儲存圖片('檔名.jpg',陣列)",
                code_display="儲存圖片('檔名.jpg',陣列)",
                note='儲存圖片(檔名字串, 陣列)',
                long_note=True))

        DropdownPostit(tab_name='cv', code_list = temp_code_list,
            postfix_enter=False).pack(side=tk.TOP, anchor='w', padx=2, pady=8)


        # separator and note
        ttk.Separator(common_postit_tabs['cv'].frame.interior, orient=tk.HORIZONTAL
            ).pack(side=tk.TOP, fill=tk.X, padx=0, pady=10)
        f = font.Font(size=11, weight=font.NORMAL, family='Consolas')
        ttk.Label(common_postit_tabs['cv'].frame.interior, 
                    
                    text=' >> 圖片顯示',
                    font=f,   
                    compound=tk.LEFT, 
                ).pack(side=tk.TOP, padx=5, pady=8, anchor='w')

        # dropdown list postit
        temp_code_list = []
        temp_code_list.append(CodeNTuple(
                menu_display='顯示圖片',
                code='顯示圖片(陣列)',
                code_display='顯示圖片(陣列)',
                note='顯示圖片(陣列)',
                long_note=False))
        temp_code_list.append(CodeNTuple(
                menu_display='顯示圖片 標題',
                code="顯示圖片(陣列, 標題='我的圖片')",
                code_display="顯示圖片(陣列, 標題='我的圖片')",
                note='顯示圖片(陣列, 標題)',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='顯示圖片 新視窗',
                code='顯示圖片(陣列, 新視窗=True)',
                code_display='顯示圖片(陣列, 新視窗=True)',
                note='顯示圖片(陣列, 新視窗)',
                long_note=True))
        DropdownPostit(tab_name='cv', code_list = temp_code_list,
            postfix_enter=False).pack(side=tk.TOP, anchor='w', padx=2, pady=8)

        # dropdown list postit
        temp_code_list = []
        temp_code_list.append(CodeNTuple(
                menu_display='關閉所有圖片',
                code='關閉所有圖片()',
                code_display='關閉所有圖片()',
                note='關閉所有圖片',
                long_note=False))
        DropdownPostit(tab_name='cv', code_list = temp_code_list,
            postfix_enter=False).pack(side=tk.TOP, anchor='w', padx=2, pady=8)


        # separator and note
        ttk.Separator(common_postit_tabs['cv'].frame.interior, orient=tk.HORIZONTAL
            ).pack(side=tk.TOP, fill=tk.X, padx=0, pady=10)
        f = font.Font(size=11, weight=font.NORMAL, family='Consolas')
        ttk.Label(common_postit_tabs['cv'].frame.interior, 
                    
                    text=' >> 圖片處理',
                    font=f,   
                    compound=tk.LEFT, 
                ).pack(side=tk.TOP, padx=5, pady=8, anchor='w')

        # dropdown list postit
        temp_code_list = []
        temp_code_list.append(CodeNTuple(
                menu_display='彩色轉灰階',
                code='陣列 = 彩色轉灰階(陣列)',
                code_display='陣列 = 彩色轉灰階(陣列)',
                note='彩色轉灰階',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='灰階轉彩色',
                code='陣列 = 灰階轉彩色(陣列)',
                code_display='陣列 = 灰階轉彩色(陣列)',
                note='灰階轉彩色',
                long_note=True))
        DropdownPostit(tab_name='cv', code_list = temp_code_list,
            postfix_enter=False).pack(side=tk.TOP, anchor='w', padx=2, pady=8)


        # dropdown list postit
        temp_code_list = []
        temp_code_list.append(CodeNTuple(
                menu_display='左右翻轉',
                code='陣列 = 左右翻轉(陣列)',
                code_display='陣列 = 左右翻轉(陣列)',
                note='左右翻轉',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='上下翻轉',
                code='陣列 = 上下翻轉(陣列)',
                code_display='陣列 =上下翻轉(陣列)',
                note='上下翻轉',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='上下左右翻轉',
                code='陣列 = 上下左右翻轉(陣列)',
                code_display='陣列 =上下左右翻轉(陣列)',
                note='上下翻轉左右',
                long_note=True))
        DropdownPostit(tab_name='cv', code_list = temp_code_list,
            postfix_enter=False).pack(side=tk.TOP, anchor='w', padx=2, pady=8)


        # separator and note
        ttk.Separator(common_postit_tabs['cv'].frame.interior, orient=tk.HORIZONTAL
            ).pack(side=tk.TOP, fill=tk.X, padx=0, pady=10)
        f = font.Font(size=11, weight=font.NORMAL, family='Consolas')
        ttk.Label(common_postit_tabs['cv'].frame.interior, 
                    
                    text=' >> 互動',
                    font=f,   
                    compound=tk.LEFT, 
                ).pack(side=tk.TOP, padx=5, pady=8, anchor='w')


        # dropdown list postit
        temp_code_list = []
        temp_code_list.append(CodeNTuple(
                menu_display='無限等待',
                code='等待按鍵()',
                code_display='等待按鍵()',
                note='無限等待',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='等待毫秒',
                code='等待按鍵(25)',
                code_display='等待按鍵(25)',
                note='等待毫秒',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='無限等待 傳回按鍵',
                code='按鍵 = 等待按鍵()',
                code_display='按鍵 = 等待按鍵()',
                note='無限等待 傳回按鍵',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='等待毫秒 傳回按鍵',
                code='按鍵 = 等待按鍵(25)',
                code_display='按鍵 = 等待按鍵(25)',
                note='等待毫秒 傳回按鍵',
                long_note=True))
        DropdownPostit(tab_name='cv', code_list = temp_code_list,
            postfix_enter=False).pack(side=tk.TOP, anchor='w', padx=2, pady=8)

        # dropdown list postit
        temp_code_list = []
        temp_code_list.append(CodeNTuple(
                menu_display='字母按鍵',
                code="'a'",
                code_display="'a'",
                note='字母按鍵',
                long_note=False))
        temp_code_list.append(CodeNTuple(
                menu_display='數字按鍵',
                code="'1'",
                code_display="'1'",
                note='數字按鍵',
                long_note=False))
        temp_code_list.append(CodeNTuple(
                menu_display='符號按鍵',
                code="'='",
                code_display="'='",
                note='符號按鍵',
                long_note=False))
        DropdownPostit(tab_name='cv', code_list = temp_code_list,
            postfix_enter=False).pack(side=tk.TOP, anchor='w', padx=2, pady=8)

        # separator and note
        ttk.Separator(common_postit_tabs['cv'].frame.interior, orient=tk.HORIZONTAL
            ).pack(side=tk.TOP, fill=tk.X, padx=0, pady=10)
        f = font.Font(size=11, weight=font.NORMAL, family='Consolas')
        ttk.Label(common_postit_tabs['cv'].frame.interior, 
                    
                    text=' >> 影像擷取',
                    font=f,   
                    compound=tk.LEFT, 
                ).pack(side=tk.TOP, padx=5, pady=8, anchor='w')


        # dropdown list postit
        temp_code_list = []
        temp_code_list.append(CodeNTuple(
                menu_display='開啟影像擷取',
                code='攝影機 = 開啟影像擷取()',
                code_display='攝影機 = 開啟影像擷取()',
                note='開啟影像擷取',
                long_note=False))
        temp_code_list.append(CodeNTuple(
                menu_display='擷取單張影像',
                code='陣列 = 擷取單張影像(攝影機)',
                code_display='陣列 = 擷取單張影像(攝影機)',
                note='擷取單張影像',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='關閉影像擷取',
                code='攝影機.release()',
                code_display='攝影機.release()',
                note='關閉影像擷取',
                long_note=False))
        DropdownPostit(tab_name='cv', code_list = temp_code_list,
            postfix_enter=False).pack(side=tk.TOP, anchor='w', padx=2, pady=8)


        # dropdown list postit
        temp_code_list = []
        temp_code_list.append(CodeNTuple(
                menu_display='擷取螢幕灰階',
                code='陣列 = 擷取螢幕灰階(0,200,0,200)',
                code_display='陣列 = 擷取螢幕灰階(0,200,0,200)',
                note='擷取螢幕灰階(行1,行2,列1,列2)',
                long_note=True))
        DropdownPostit(tab_name='cv', code_list = temp_code_list,
            postfix_enter=False).pack(side=tk.TOP, anchor='w', padx=2, pady=8)                

       # separator and note
        ttk.Separator(common_postit_tabs['cv'].frame.interior, orient=tk.HORIZONTAL
            ).pack(side=tk.TOP, fill=tk.X, padx=0, pady=10)
        f = font.Font(size=11, weight=font.NORMAL, family='Consolas')
        ttk.Label(common_postit_tabs['cv'].frame.interior, 
                    
                    text=' >> 圖片繪圖',
                    font=f,   
                    compound=tk.LEFT, 
                ).pack(side=tk.TOP, padx=5, pady=8, anchor='w')


        # dropdown list postit
        temp_code_list = []
        temp_code_list.append(CodeNTuple(
                menu_display='畫灰階矩形',
                code='陣列 = 畫灰階矩形(陣列,0,200,0,200)',
                code_display='陣列 = 畫灰階矩形(陣列,0,200,0,200)',
                note='畫灰階矩形(陣列,行1,行2,列1,列2)',
                long_note=True))
        DropdownPostit(tab_name='cv', code_list = temp_code_list,
            postfix_enter=False).pack(side=tk.TOP, anchor='w', padx=2, pady=8) 



    def speech_tab_init(self):
        # title and setup tool
        tab = common_postit_tabs['speech']
        example_vars = [''] 
        tab.popup_init(example_vars)

        f = font.Font(size=11, weight=font.NORMAL, family='Consolas')
        label =ttk.Label(common_postit_tabs['speech'].frame.interior, 
                text='【語音】', 
                image= common_images['gear'],
                font=f,
                compound=tk.RIGHT,
                )                
        label.pack(side=tk.TOP, padx=5, pady=8,anchor='w')
        label.bind("<Button-1>", common_postit_tabs['speech'].popup)   




        # dropdown list postit
        temp_code_list = []
        temp_code_list.append(CodeNTuple(
                menu_display='從語音模組匯入全部',
                code='from 語音模組 import *',
                code_display='from 語音模組 import *',
                note='從語音模組匯入全部',
                long_note=True))
        DropdownPostit(tab_name='speech', code_list = temp_code_list,
            postfix_enter=False).pack(side=tk.TOP, anchor='w', padx=2, pady=8)


       # separator and note
        ttk.Separator(common_postit_tabs['speech'].frame.interior, orient=tk.HORIZONTAL
            ).pack(side=tk.TOP, fill=tk.X, padx=0, pady=10)
        f = font.Font(size=11, weight=font.NORMAL, family='Consolas')
        ttk.Label(common_postit_tabs['speech'].frame.interior, 
                    
                    text=' >> 文字轉語音',
                    font=f,   
                    compound=tk.LEFT, 
                ).pack(side=tk.TOP, padx=5, pady=8, anchor='w')


        # dropdown list postit
        temp_code_list = []
        temp_code_list.append(CodeNTuple(
                menu_display='語音合成 並等待',
                code="語音合成('你好')",
                code_display="語音合成('你好')",
                note='語音播完再繼續程式',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='語音合成 不等待',
                code="語音合成('你好', 等待=False)",
                code_display="語音合成('你好', 等待=False)",
                note='語音未播完就繼續程式',
                long_note=True))
        DropdownPostit(tab_name='speech', code_list = temp_code_list,
            postfix_enter=False).pack(side=tk.TOP, anchor='w', padx=2, pady=8) 

        # dropdown list postit
        temp_code_list = []
        temp_code_list.append(CodeNTuple(
                menu_display='設定語音音量',
                code="設定語音音量(80)",
                code_display="設定語音音量(80)",
                note='音量範圍 0 ~ 100',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='設定語音速度',
                code="設定語音速度(1)",
                code_display="設定語音速度(1)",
                note='速度範圍 -10 ~ 10',
                long_note=True))
        DropdownPostit(tab_name='speech', code_list = temp_code_list,
            postfix_enter=False).pack(side=tk.TOP, anchor='w', padx=2, pady=8)

        # dropdown list postit
        temp_code_list = []
        temp_code_list.append(CodeNTuple(
                menu_display='語音說完了嗎',
                code="語音說完了嗎()",
                code_display="語音說完了嗎()",
                note='語音說完了嗎',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='語音說完了嗎 等待時間',
                code="語音說完了嗎(100)",
                code_display="語音說完了嗎(100)",
                note='等待0.1秒',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='等待語音說完',
                code="等待語音說完()",
                code_display="等待語音說完()",
                note='等待語音說完',
                long_note=True))
        DropdownPostit(tab_name='speech', code_list = temp_code_list,
            postfix_enter=False).pack(side=tk.TOP, anchor='w', padx=2, pady=8)


       # separator and note
        ttk.Separator(common_postit_tabs['speech'].frame.interior, orient=tk.HORIZONTAL
            ).pack(side=tk.TOP, fill=tk.X, padx=0, pady=10)
        f = font.Font(size=11, weight=font.NORMAL, family='Consolas')
        ttk.Label(common_postit_tabs['speech'].frame.interior, 
                    
                    text=' >> 語音辨識',
                    font=f,   
                    compound=tk.LEFT, 
                ).pack(side=tk.TOP, padx=5, pady=8, anchor='w')

        # dropdown list postit
        temp_code_list = []
        temp_code_list.append(CodeNTuple(
                menu_display='語音辨識google',
                code="語音辨識google()",
                code_display="語音辨識google()",
                note='google服務(需連網)',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='語音辨識google(次數)',
                code="語音辨識google(次數=15)",
                code_display="語音辨識google(次數=15)",
                note='google服務(需連網)',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display="語音辨識azure key",
                code="語音辨識azure(key='')",
                code_display="語音辨識azure(key='')",
                note='語音辨識azure 需註冊',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display="語音辨識azure key location",
                code="語音辨識azure(key='', location='westus')",
                code_display="語音辨識azure(key='', location='westus')",
                note='語音辨識azure 需註冊',
                long_note=True))
        DropdownPostit(tab_name='speech', code_list = temp_code_list,
            postfix_enter=False).pack(side=tk.TOP, anchor='w', padx=2, pady=8)


        # dropdown list postit
        temp_code_list = []
        temp_code_list.append(CodeNTuple(
                menu_display='辨識成功了嗎',
                code="辨識成功了嗎()",
                code_display="辨識成功了嗎()",
                note='辨識成功了嗎',
                long_note=True))
        DropdownPostit(tab_name='speech', code_list = temp_code_list,
            postfix_enter=False).pack(side=tk.TOP, anchor='w', padx=2, pady=8)

        # dropdown list postit
        temp_code_list = []
        temp_code_list.append(CodeNTuple(
                menu_display='取得辨識文字',
                code="文字 = 取得辨識文字()",
                code_display="文字 = 取得辨識文字()",
                note='取得辨識文字',
                long_note=True))
        DropdownPostit(tab_name='speech', code_list = temp_code_list,
            postfix_enter=False).pack(side=tk.TOP, anchor='w', padx=2, pady=8)

        # dropdown list postit
        temp_code_list = []
        temp_code_list.append(CodeNTuple(
                menu_display='暫停語音辨識',
                code="暫停語音辨識()",
                code_display="暫停語音辨識()",
                note='pause',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='繼續語音辨識',
                code="繼續語音辨識()",
                code_display="繼續語音辨識()",
                note='continue',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='語音辨識中嗎',
                code="語音辨識中嗎()",
                code_display="語音辨識中嗎()",
                note='recognition status',
                long_note=True))
        DropdownPostit(tab_name='speech', code_list = temp_code_list,
            postfix_enter=False).pack(side=tk.TOP, anchor='w', padx=2, pady=8)



    def flow_tab_init(self):
        ### flow tab

        # separator and note
        f = font.Font(size=11, weight=font.NORMAL, family='Consolas')
        ttk.Label(common_postit_tabs['flow'].frame.interior, 
                    #text='='*6 +' 【 條件分支 】 '+'='*6,
                    text=' >> 條件分支',
                    font=f,    
                    compound=tk.LEFT, 
                ).pack(side=tk.TOP, padx=5, pady=8, anchor='w')

        # dropdown list postit
        temp_code_list = []
        temp_code_list.append(CodeNTuple(
                                    menu_display='如果 if ',
                                    code='if 1 > 0: \npass',
                                    code_display='if 1 > 0:\n    pass',
                                    note='如果 條件:\n        成立區塊',
                                    long_note=False ))
        temp_code_list.append(CodeNTuple(
                                    menu_display='如果 不然(否則) if else ',
                                    code='if 1 > 0:\npass\nelse:\npass',
                                    code_display='if 1 > 0:\n    pass\nelse:\n'
                                    '    pass',
                                    note='如果 條件:\n        成立區塊\n不然(否則):\n        不成立區塊',
                                    long_note=False))
        
        temp_code_list.append(CodeNTuple(
            menu_display='不然如果  if elif else ',
            code='if 1 > 0:\npass\nelif 0 < 1:\npass\nelse:\npass',
            code_display='if 1 > 0:\n    pass\nelif 0 < 1:\n    pass\nelse:\n    pass',
            note='如果 條件:\n        成立區塊\n不然如果 條件:\n        成立區塊\n不然(否則):\n        都不成立區塊',
            long_note=False ))
        DropdownPostit(tab_name='flow', code_list = temp_code_list,
            postfix_enter=False).pack(side=tk.TOP, anchor='w', padx=2, pady=8)



        # separator and note
        # ttk.Separator(common_postit_tabs['flow'].frame, orient=tk.HORIZONTAL
        #     ).pack(side=tk.TOP, fill=tk.X, padx=5)
        # f = font.Font(size=11, weight=font.NORMAL, family='Consolas')
        # ttk.Label(common_postit_tabs['flow'].frame, 
        #             #text='='*6 +' 【 條 件 分 支 】 '+'='*6,
        #             text='【 條 件 】',
        #             font=f,    
        #             compound=tk.LEFT, 
        #         ).pack(side=tk.TOP, padx=5, pady=8, anchor='center')

        # temp_code_list = []
        # temp_code_list.append(CodeNTuple(
        #                             menu_display='大於  > ',
        #                             code='___ > ___',
        #                             code_display='___ > ___',
        #                             note='大於',
        #                             long_note=False ))
        # temp_code_list.append(CodeNTuple(
        #                             menu_display='大於等於  >= ',
        #                             code='___ >= ___',
        #                             code_display='___ >= ___',
        #                             note='大於等於',
        #                             long_note=False ))
        # temp_code_list.append(CodeNTuple(
        #                             menu_display='小於 <',
        #                             code='___ < ___',
        #                             code_display='___ < ___',
        #                             note='小於',
        #                             long_note=False ))
        # temp_code_list.append(CodeNTuple(
        #                             menu_display='小於等於 <=',
        #                             code='___ <= ___',
        #                             code_display='',
        #                             note='',
        #                             long_note=False ))
        # temp_code_list.append(CodeNTuple(
        #                             menu_display='',
        #                             code='',
        #                             code_display='',
        #                             note='',
        #                             long_note=False ))
        # temp_code_list.append(CodeNTuple(
        #                             menu_display='',
        #                             code='',
        #                             code_display='',
        #                             note='',
        #                             long_note=False ))
        # DropdownPostit(tab_name='flow', code_list = temp_code_list,
        #     postfix_enter=False).pack(side=tk.TOP, anchor='w', padx=2, pady=8)





        # separator and note
        ttk.Separator(common_postit_tabs['flow'].frame.interior, orient=tk.HORIZONTAL
            ).pack(side=tk.TOP, fill=tk.X, padx=0, pady=10)
        f = font.Font(size=11, weight=font.NORMAL, family='Consolas')
        ttk.Label(common_postit_tabs['flow'].frame.interior, 
                    #text='='*6 +' 【  迴  圈  】 '+'='*6,
                    text=' >> 迴圈',
                    font=f,   
                    compound=tk.LEFT, 
                ).pack(side=tk.TOP, padx=5, pady=8, anchor='w')

        # dropdown list postit  
        temp_code_list = []
        temp_code_list.append(CodeNTuple(
                                    menu_display='重複無限次 while True ',
                                    code='while True:\npass',
                                    code_display='while True:\n    pass',
                                    note='重複無限次:\n        迴圈區塊',
                                    long_note=False ))
        temp_code_list.append(CodeNTuple(
                                    menu_display='有條件重複 while ',
                                    code='while 1 > 0:\npass',
                                    code_display='while 1 > 0:\n    pass',
                                    note='當條件成立時:\n        迴圈區塊',
                                    long_note=False ))
        DropdownPostit(tab_name='flow', code_list = temp_code_list,
            postfix_enter=False).pack(side=tk.TOP, anchor='w', padx=2, pady=8)

        # BasePostit(tab_name='flow',
        #                    code='while 條件:\n___',
        #                    code_display='while 條件:\n    ___\n',
                                        
        #                    note="當…時\n\n重複___",
        #                    #long_note=True,
        #                    postfix_enter=False,
        # ).pack(side=tk.TOP, anchor='w', padx=2, pady=8)


        # dropdown list postit
        temp_code_list = []
        temp_code_list.append(CodeNTuple(
                menu_display='從數列 逐一取出(重複幾次)for in range  ',
                code='for 數 in range(10):\npass',
                code_display='for 數 in range(10):\n    pass',
                note='從數列 逐一取出(重複幾次):\n        迴圈區塊',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='從數列 逐一取出(開始 不含結束) for in range  ',
                code='for 數 in range(5, 10):\npass',
                code_display='for 數 in range(5, 10):\n    pass',
                note='從數列 逐一取出(開始 不含結束):\n        迴圈區塊',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='從數列 逐一取出(開始 不含結束 每次步進) for in range  ',
                code='for 數 in range(0, 10, 2):\npass',
                code_display='for 數 in range(0, 10, 2):\n    pass',
                note='從數列 逐一取出(開始 不含結束 每次步進):\n        迴圈區塊',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='從清單 逐一取出 for in   ',
                code='for 項目 in [1,4,5]:\npass',
                code_display='for 項目 in [1,4,5]:\n    pass',
                note='從清單 逐一取出:\n        迴圈區塊',
                long_note=True ))
        DropdownPostit(tab_name='flow', code_list = temp_code_list,
            postfix_enter=False).pack(side=tk.TOP, anchor='w', padx=2, pady=8)


        # dropdown list postit
        temp_code_list = []
        temp_code_list.append(CodeNTuple(
                menu_display='跳出一層迴圈 break',
                code='break',
                code_display='break',
                note='跳出一層迴圈',
                long_note=False))
        temp_code_list.append(CodeNTuple(
                menu_display='從迴圈開頭繼續 continue',
                code='continue',
                code_display='continue',
                note='從迴圈開頭繼續',
                long_note=False ))

        DropdownPostit(tab_name='flow', code_list = temp_code_list,
            postfix_enter=False).pack(side=tk.TOP, anchor='w', padx=2, pady=8)



        #separator and note
        ttk.Separator(common_postit_tabs['flow'].frame.interior, orient=tk.HORIZONTAL
            ).pack(side=tk.TOP, fill=tk.X, padx=5, pady=10)
        f = font.Font(size=11, weight=font.NORMAL, family='Consolas')
        ttk.Label(common_postit_tabs['flow'].frame.interior, 
                    #text='='*6 +' 【 條 件 分 支 】 '+'='*6,
                    text=' >> 自訂功能(函式)',
                    font=f,    
                    compound=tk.LEFT, 
                ).pack(side=tk.TOP, padx=5, pady=8, anchor='w')

        # dropdown list postit
        temp_code_list = []
        temp_code_list.append(CodeNTuple(
                menu_display='定義 新功能(自訂函式)',
                code='def 新功能(引數):\npass',
                code_display='def 新功能(引數):\n    pass',
                note='定義 新功能(引數):\n        函式區塊',
                long_note=True ))  
  
        # temp_code_list.append(CodeNTuple(
        #         menu_display='  define  function ',
        #         code='def func(p1, p2):\n___',
        #         code_display='def func(p1, p2):\n    ___',
        #         note='自訂功能函式',
        #         long_note=True ))
        # temp_code_list.append(CodeNTuple(
        #         menu_display='呼叫功能函式',
        #         code='功能函式(引數1, 引數2)',
        #         code_display='功能函式(引數1, 引數2)',
        #         note='呼叫功能函式',
        #         long_note=True ))    
        # temp_code_list.append(CodeNTuple(
        #         menu_display='  call function ',
        #         code='func(a1, a2):\n___',
        #         code_display='func(a1, a2):\n    ___',
        #         note='呼叫功能函式',
        #         long_note=True ))    
        DropdownPostit(tab_name='flow', code_list = temp_code_list,
            postfix_enter=False).pack(side=tk.TOP, anchor='w', padx=2, pady=8)

        # dropdown list postit
        temp_code_list = []
        temp_code_list.append(CodeNTuple(
                menu_display='呼叫 新功能(自訂函式)',
                code='新功能(5)',
                code_display='新功能(5)',
                note='呼叫 新功能(引數為5)',
                long_note=True ))
        DropdownPostit(tab_name='flow', code_list = temp_code_list,
            postfix_enter=False).pack(side=tk.TOP, anchor='w', padx=2, pady=8)

        # dropdown list postit
        temp_code_list = []
        temp_code_list.append(CodeNTuple(
                menu_display='功能函式返回(跳出) return',
                code='return',
                code_display='return',
                note='功能函式返回(跳出)',
                long_note=False))

        DropdownPostit(tab_name='flow', code_list = temp_code_list,
            postfix_enter=False).pack(side=tk.TOP, anchor='w', padx=2, pady=8)


        #separator and note
        ttk.Separator(common_postit_tabs['flow'].frame.interior, orient=tk.HORIZONTAL
            ).pack(side=tk.TOP, fill=tk.X, padx=5, pady=10)
        f = font.Font(size=11, weight=font.NORMAL, family='Consolas')
        ttk.Label(common_postit_tabs['flow'].frame.interior, 
                    #text='='*6 +' 【 條 件 分 支 】 '+'='*6,
                    text=' >> 例外(錯誤)處理',
                    font=f,    
                    compound=tk.LEFT, 
                ).pack(side=tk.TOP, padx=5, pady=8, anchor='w')

        # dropdown list postit
        temp_code_list = []
        temp_code_list.append(CodeNTuple(
                menu_display='捕捉例外(錯誤)',
                code='try:\npass\nexcept Exception:\npass',
                code_display='try:\n    pass\nexcept Exception:\n    pass',
                note='測試:\n        測試區塊\n例外發生:\n        錯誤處理區塊',
                long_note=True))
        DropdownPostit(tab_name='flow', code_list = temp_code_list,
            postfix_enter=False).pack(side=tk.TOP, anchor='w', padx=2, pady=8)



        #separator and note
        ttk.Separator(common_postit_tabs['flow'].frame.interior, orient=tk.HORIZONTAL
            ).pack(side=tk.TOP, fill=tk.X, padx=5, pady=10)
        f = font.Font(size=11, weight=font.NORMAL, family='Consolas')
        ttk.Label(common_postit_tabs['flow'].frame.interior, 
                    #text='='*6 +' 【 條 件 分 支 】 '+'='*6,
                    text=' >> 物件類別',
                    font=f,    
                    compound=tk.LEFT, 
                ).pack(side=tk.TOP, padx=5, pady=8, anchor='w')

        # dropdown list postit
        temp_code_list = []
        temp_code_list.append(CodeNTuple(
                menu_display='定義新類別',
                code='class 類別:\n屬性 = 1\ndef 方法(self):\npass',
                code_display='class 類別:\n    屬性 = 1\n    def 方法(self):\n    pass',
                note='定義新類別',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='繼承類別',
                code='class 子類別(父母類別):\n屬性 = 1\ndef 方法(self):\npass',
                code_display='class 子類別(父母類別):\n    屬性 = 1\n    def 方法(self):\n    pass',
                note='繼承類別',
                long_note=True))                
        DropdownPostit(tab_name='flow', code_list = temp_code_list,
            postfix_enter=False).pack(side=tk.TOP, anchor='w', padx=2, pady=8)


        #separator and note
        ttk.Separator(common_postit_tabs['flow'].frame.interior, orient=tk.HORIZONTAL
            ).pack(side=tk.TOP, fill=tk.X, padx=5, pady=10)
        f = font.Font(size=11, weight=font.NORMAL, family='Consolas')
        ttk.Label(common_postit_tabs['flow'].frame.interior, 
                    #text='='*6 +' 【 條 件 分 支 】 '+'='*6,
                    text=' >> 有限狀態機',
                    font=f,    
                    compound=tk.LEFT, 
                ).pack(side=tk.TOP, padx=5, pady=8, anchor='w')

        # dropdown list postit
        temp_code_list = []
        temp_code_list.append(CodeNTuple(
                menu_display='匯入狀態機模組',
                code='from transitions import Machine as 狀態機',
                code_display='from transitions import Machine as 狀態機',
                note='匯入狀態機模組',
                long_note=True))
        DropdownPostit(tab_name='flow', code_list = temp_code_list,
            postfix_enter=False).pack(side=tk.TOP, anchor='w', padx=2, pady=8)

        # dropdown list postit
        temp_code_list = []
        temp_code_list.append(CodeNTuple(
                menu_display='階段清單',
                code="階段清單 = ['開頭','關卡','結尾']",
                code_display="階段清單 = ['開頭','關卡','結尾']",
                note='階段清單',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='程式狀態類別',
                code="class 程式狀態(狀態機):\ndef on_enter_開頭(self):\nprint('進入 開頭階段')",
                code_display="class 程式狀態(狀態機)):\n    def on_enter_開頭(self):\n        print('進入 開頭')",
                note='繼承類別',
                long_note=True)) 
        temp_code_list.append(CodeNTuple(
                menu_display='程式狀態方法(離開)',
                code="    def on_exit_開頭(self):\nprint('離開 開頭階段')",
                code_display="def on_exit_開頭(self):\n    print('離開 開頭階段')",
                note='程式狀態方法(離開)',
                long_note=True))  
        temp_code_list.append(CodeNTuple(
                menu_display='主流程物件',
                code="主流程 = 程式狀態(states=階段清單, initial='開頭')",
                code_display="主流程 = 程式狀態(states=階段清單, initial='開頭')",
                note='主流程物件',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='依序轉換',
                code="主流程.add_ordered_transitions()",
                code_display="主流程.add_ordered_transitions()",
                note='依序轉換',
                long_note=True))    
        DropdownPostit(tab_name='flow', code_list = temp_code_list,
            postfix_enter=False).pack(side=tk.TOP, anchor='w', padx=2, pady=8)

        # dropdown list postit
        temp_code_list = []
        temp_code_list.append(CodeNTuple(
                menu_display='目前階段',
                code='主流程.state',
                code_display='主流程.state',
                note='目前階段',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='跳到階段',
                code='主流程.to_開頭()',
                code_display='主流程.to_開頭()',
                note='跳到階段',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='下一階段(依序)',
                code='主流程.next_state()',
                code_display='主流程.next_state()',
                note='下一階段(依序)',
                long_note=True))
        DropdownPostit(tab_name='flow', code_list = temp_code_list,
            postfix_enter=False).pack(side=tk.TOP, anchor='w', padx=2, pady=8)



#     def tab_symbol_add_row(self, col1, col2=None, col3=None, col4=None):
#         col1.grid(row=self.symbol_row_index, column=0, padx=5, pady=5)
#         if col2:
#             col2.grid(row=self.symbol_row_index, column=1, padx=5, pady=5)
#         if col3:
#             col3.grid(row=self.symbol_row_index, column=2, padx=5, pady=5)
#         if col4:
#             col4.grid(row=self.symbol_row_index, column=3, padx=5, pady=5)
#         self.symbol_row_index += 1

    def toolbar_init(self):

        # var toolbar
        #self.var_toolbar = ttk.Frame(self.interior)
        self.var_toolbar = ttk.Frame(self)
        self.var_toolbar.pack(side=tk.TOP, fill=tk.X)



        common.share_var_get_postit = VariableFetchToolPostit(
                self.var_toolbar, tool_name='variable_get')
        #common.share_var_assign_postit = VariableFetchToolPostit(
        #        self.var_toolbar, tool_name='variable_assign')
        common.share_vars_postit = VariableMenuPostit(self.var_toolbar)

        PilcrowToolPostit(self.var_toolbar).pack(side=tk.LEFT,padx=1, pady=3)
        CommentToolPostit(self.var_toolbar).pack(side=tk.LEFT,padx=1, pady=3)
        common.share_vars_postit.pack(side=tk.LEFT,padx=1, pady=3)
        VariableAddToolPostit(self.var_toolbar).pack(side=tk.LEFT,
                padx=1, pady=3)
        common.share_var_get_postit.pack(side=tk.LEFT,padx=1, pady=3)
        #common.share_var_assign_postit.pack(side=tk.LEFT,padx=2, pady=3)
        SymbolToolPostit(self.var_toolbar).pack(side=tk.LEFT,padx=8, pady=3)

        # edit_toolbar
        #self.edit_toolbar = ttk.Frame(self.interior)
        self.edit_toolbar = ttk.Frame(self)
        self.edit_toolbar.pack(side=tk.TOP, fill=tk.X)
                
        DedentToolPostit(self.edit_toolbar).pack(side=tk.LEFT,padx=3, pady=3)
        IndentToolPostit(self.edit_toolbar).pack(side=tk.LEFT,padx=3, pady=3)
        UndoToolPostit(self.edit_toolbar).pack(side=tk.LEFT,padx=3, pady=3)
        RedoToolPostit(self.edit_toolbar).pack(side=tk.LEFT,padx=3, pady=3)
        CutToolPostit(self.edit_toolbar).pack(side=tk.LEFT,padx=3, pady=3)
        CopyToolPostit(self.edit_toolbar).pack(side=tk.LEFT,padx=3, pady=3)
        PasteToolPostit(self.edit_toolbar).pack(side=tk.LEFT,padx=3, pady=3)
        BackspaceToolPostit(self.edit_toolbar).pack(side=tk.LEFT,padx=3, pady=3,
                    )
        EnterToolPostit(self.edit_toolbar).pack(side=tk.LEFT,padx=3, pady=3,
                    )

        

        







        






    def tab_menu_popup(self, event):
        #if self.tool_name != 'variable_get':
        if event:
            self.tab_menu.tk_popup(event.x_root, event.y_root)


    # def add_tab(self, name, label, tab_type):
    #     if name in common.postit_tabs:
    #         print('tab', name, ' already exists')
    #         return

    #     tab = PostitTab(name, label, tab_type)
    #     common.postit_tabs[name] = tab

    #     #tab.frame = ttk.Frame(self.notebook)        
    #     tab.frame = CustomVerticallyScrollableFrame(self.notebook)
    #     self.notebook.insert('end',tab.frame,
    #                       text = tab.label,
    #                       image = tab.image,
    #                       compound="top",
    #                     )
    #     # self.notebook.add(tab.frame,
    #     #                   text = tab.label,
    #     #                   image = tab.image,
    #     #                   compound="top",
    #     #                 )

    #     #tab.index = self.notebook.index('end')
        
    #     return tab

    # def remove_tab(self, name):
    #     if name in common.postit_tabs:
    #         self.notebook.forget(common.postit_tabs[name].frame)
    #         del common.postit_tabs[name]
    #         print('tab ', name, ' deleted')
    #     else:
    #         print('no tab ', name)

    def on_tab_click(self, event):
        """record focus widget"""
        
        self.last_focus = get_workbench().focus_get()

    def on_tab_changed(self, event):
        """restore last focus widget"""
        
        if self.last_focus:
            self.last_focus.focus_set()
            self.last_focus = None


class CustomVerticallyScrollableFrame(ttk.Frame):
    # http://tkinter.unpythonic.net/wiki/VerticalScrolledFrame

    def __init__(self, master):
        ttk.Frame.__init__(self, master)

        # set up scrolling with canvas
        vscrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL)
        self.canvas = tk.Canvas(self, bd=0, highlightthickness=0, yscrollcommand=vscrollbar.set)
        vscrollbar.config(command=self.canvas.yview)
        self.canvas.xview_moveto(0)
        self.canvas.yview_moveto(0)
        self.canvas.grid(row=0, column=0, sticky=tk.NSEW)
        vscrollbar.grid(row=0, column=1, sticky=tk.NSEW)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.interior = ttk.Frame(self.canvas)
        self.interior_id = self.canvas.create_window(0, 0, window=self.interior, anchor=tk.NW)
        self.bind("<Configure>", self._configure_interior, "+")
        self.bind("<Expose>", self._expose, "+")
        #self.bind_all("<MouseWheel>", self._on_mousewheel,"+")

    def _expose(self, event):
        self.update_idletasks()
        self.update_scrollbars()

    def _configure_interior(self, event):
        self.update_scrollbars()

    def update_scrollbars(self):
        # update the scrollbars to match the size of the inner frame
        size = (self.canvas.winfo_width(), self.interior.winfo_reqheight())
        self.canvas.config(scrollregion="0 0 %s %s" % size)
        if (
            self.interior.winfo_reqwidth() != self.canvas.winfo_width()
            and self.canvas.winfo_width() > 10
        ):
            # update the interior's width to fit canvas
            # print("CAWI", self.canvas.winfo_width())
            self.canvas.itemconfigure(self.interior_id, width=self.canvas.winfo_width())

    def _on_mousewheel(self, event):
        #if isinstance(event.widget, BasePostit):
        if 'customverticallyscrollableframe' in str(event.widget):
            #print(str(event.widget))
            
            
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")



class AboutDialog(CommonDialog):
    def __init__(self, master):
        super().__init__(master)

        main_frame = ttk.Frame(self)
        main_frame.grid(sticky=tk.NSEW, ipadx=15, ipady=15)
        main_frame.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)

        self.title('關於Py4t')
        self.resizable(height=tk.FALSE, width=tk.FALSE)
        self.protocol("WM_DELETE_WINDOW", self._ok)

        # bg_frame = ttk.Frame(self) # gives proper color in aqua
        # bg_frame.grid()

        heading_font = tk.font.nametofont("TkHeadingFont").copy()
        heading_font.configure(size=19, weight="bold")
        heading_label = ttk.Label(
            main_frame, text="Py4t " + get_version(), font=heading_font
        )
        heading_label.grid()

        url = "https://beardad1975.github.io/py4t/"
        url_font = tk.font.nametofont("TkDefaultFont").copy()
        url_font.configure(underline=1)
        url_label = ttk.Label(
            main_frame, text=url, style="Url.TLabel", cursor="hand2", font=url_font
        )
        url_label.grid()
        url_label.bind("<Button-1>", lambda _: webbrowser.open(url))

        # if platform.system() == "Linux":
        #     try:
        #         import distro  # distro don't need to be installed

        #         system_desc = distro.name(True)
        #     except ImportError:
        #         system_desc = "Linux"

        #     if "32" not in system_desc and "64" not in system_desc:
        #         system_desc += " " + self.get_os_word_size_guess()
        # else:
        #     system_desc = (
        #         platform.system() + " " + platform.release() + " " + self.get_os_word_size_guess()
        #     )

        # platform_label = ttk.Label(
        #     main_frame,
        #     justify=tk.CENTER,
        #     text=system_desc
        #     + "\n"
        #     + "Python "
        #     + get_python_version_string()
        #     + "Tk "
        #     + ui_utils.get_tk_version_str(),
        # )
        # platform_label.grid(pady=20)

        credits_label = ttk.Label(
            main_frame,
            text=
                "\nPy4t整合了多個套件\n"
                + "目的是要搭一座學習之橋\n"
                + "從Scratch到Python\n"
                + "教導青少年寫程式\n"  
            ,
            #style="Url.TLabel",
            #cursor="hand2",
            #font=url_font,
            justify="center",
        )
        credits_label.grid()
        # credits_label.bind(
        #     "<Button-1>",
        #     lambda _: webbrowser.open("https://github.com/thonny/thonny/blob/master/CREDITS.rst"),
        # )

        license_font = tk.font.nametofont("TkDefaultFont").copy()
        license_font.configure(size=7)
        license_label = ttk.Label(
            main_frame,
            text="Copyright (©) "
            + str(datetime.datetime.now().year)
            + " Wen Hung, Chang 張文宏\n"
            + "採MIT授權\n",
            justify=tk.CENTER,
            font=license_font,
        )
        license_label.grid(pady=20)

        ok_button = ttk.Button(main_frame, text="OK", command=self._ok, default="active")
        ok_button.grid(pady=(0, 15))
        ok_button.focus_set()

        self.bind("<Return>", self._ok, True)
        self.bind("<Escape>", self._ok, True)

    def _ok(self, event=None):
        self.destroy()

    def get_os_word_size_guess(self):
        if "32" in platform.machine() and "64" not in platform.machine():
            return "(32-bit)"
        elif "64" in platform.machine() and "32" not in platform.machine():
            return "(64-bit)"
        else:
            return ""

def get_version():
    try: 
        with open(Path(__file__).parent / "VERSION" , encoding="ASCII") as fp:
            return fp.read().strip()
    except Exception:
        return "0.0.0"


def load_plugin():
    """postit plugin start point"""

    get_workbench().add_view(PythonPostitView, '便利貼', 'nw')

    #get_workbench().add_command("aboutPy4t", "help", '關於Py4t', get_version, group=62)

    def open_about(*args):
        show_dialog(AboutDialog(get_workbench()))

    get_workbench().add_command("aboutPy4t", "help", '關於Py4t', open_about, group=62)

    #get_workbench().get_menu('postit','便利貼')




    #get_workbench().add_command("test", "便利貼", '測試', try_menu)
    #get_workbench().add_command("test2", "便利貼", '測試2', try_menu)

    #get_workbench().bind("BackendRestart", try_toplevel_response, True)

    #for test
    get_workbench().add_command(command_id="try_notebook",
                                    menu_name="tools",
                                    command_label="測試thonny",
                                    handler=try_notebook,
                                    default_sequence="<F2>"
                                    )

    # get_workbench().add_command(command_id="try_get_option",
    #                                 menu_name="tools",
    #                                 command_label="測試thonny",
    #                                 handler=try_get_option,
    #                                 default_sequence="<F4>"
    #                                 )


def try_notebook():
    tab_notebook = common.postit_view.all_modes['py4t'].tab_notebook        
    s = tab_notebook.select()
    print(type(s), s)

def try_toplevel_response(event):
    #backend_name = get_runner().get_backend_proxy().backend_name
    backend_name = get_workbench().get_option("run.backend_name")
    print('got BackendRestart event. backend: ', backend_name)


def try_hide_tab():
    common.postit_view.all_modes['bit'].notebook_frame.pack_forget()

def try_add_tab():
    common.postit_view.py4t_show_tab('library3rd', 'auto')
    common.postit_view.py4t_show_tab('library3rd', 'cv4t')
    common.postit_view.py4t_show_tab('library3rd', 'numpy')
    common.postit_view.py4t_show_tab('library3rd', 'speech4t')
    common.postit_view.py4t_show_tab('eventloop', 'threed4t')
    common.postit_view.py4t_show_tab('eventloop', 'turtle4t')
    common.postit_view.py4t_show_tab('eventloop', 'physics4t')

def try_set_option():
    builtin_list = ['common', 'flow']
    get_workbench().set_default('postit_tabs_view.builtin',builtin_list)
    get_workbench().set_option('postit_tabs_view.builtin', ['a','b'])

def try_get_option():
    builtin_list = ['common', 'flow']
    get_workbench().set_default('postit_tabs_view.builtin',builtin_list)
    r = get_workbench().get_option('postit_tabs_view.builtin')
    print(type(r), r)

