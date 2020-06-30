import os 

import tkinter as tk
import tkinter.font as font
from tkinter import messagebox
from tkinter import ttk
from pathlib import Path
from PIL import Image, ImageTk

from thonny import get_workbench, get_shell, get_runner
from thonny.ui_utils import VerticallyScrollableFrame
from thonny.common import ToplevelCommand

from .base_postit import BasePostit
from .enclosed_postit import EnclosedPostit
from .dropdown_postit import DropdownPostit
from .common import (common_postit_tabs, CodeNTuple, common_images, 
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


class PostitTab:
    """postit tab info 
        attributes: name label tab_type fill_color 
                   outline_color image frame
    """

    color_data = [
        {"basic_filename":'color0.png', 'fill_color':'#4c97ff', 
                "pack_filename":'pack0.png', 'font_color':'white'},
        {"basic_filename":'color1.png', 'fill_color':'#9966ff', 
                "pack_filename":'pack1.png', 'font_color':'white'},    
        {"basic_filename":'color2.png', 'fill_color':'#d65cd6', 
                "pack_filename":'pack2.png', 'font_color':'white'},
        {"basic_filename":'color3.png', 'fill_color':'#ffd500', 
                "pack_filename":'pack3.png', 'font_color':'black'},
        {"basic_filename":'color4.png', 'fill_color':'#ffab19',
                "pack_filename":'pack4.png',  'font_color':'black'},
        {"basic_filename":'color5.png', 'fill_color':'#4cbfe6', 
                "pack_filename":'pack5.png', 'font_color':'black'},
        {"basic_filename":'color6.png', 'fill_color':'#40bf4a', 
                "pack_filename":'pack6.png', 'font_color':'black'},
        {"basic_filename":'color7.png', 'fill_color':'#ff6680', 
                "pack_filename":'pack7.png', 'font_color':'black'},
    ]
    color_num = len(color_data)
    color_circular_index = 0  

    def __init__(self, name, label, tab_type):
        self.name = name
        self.label = label
        self.tab_type = tab_type
        
        #pick a color
        color = self.pick_color()
        self.fill_color = color['fill_color']
        self.font_color = color['font_color']
        #load image
        abs_image_path =Path(__file__).parent/'images'/color[tab_type+'_filename']
        im = Image.open(abs_image_path)       
        self.image = ImageTk.PhotoImage(im) 

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

    @classmethod
    def pick_color(cls):
        c = cls.color_data[cls.color_circular_index]
        cls.color_circular_index += 1
        if cls.color_circular_index >= cls.color_num:
            cls.color_circular_index = 0
        return c




#class PythonPostitView(VerticallyScrollableFrame):
class PythonPostitView(ttk.Frame):
    def __init__(self, master):
        super().__init__(master) 
        self.toolbar_init()
        self.notebook_init()
        self.last_focus = None
        self.symbol_row_index = 0

        

        #add notebook tabs
        self.add_tab('common', ' 基本 ','basic')
        
        
        self.add_tab('data', ' 資料 ','basic')
        self.add_tab('flow', ' 流程 ','basic')
        self.add_tab('builtin', '程式庫','basic')
        self.add_tab('turtle4t', ' 海龜 ','pack')
        self.add_tab('physics', ' 物理 ','pack')
        self.add_tab('auto', ' 自動 ','pack')
        self.add_tab('pil', ' 影像 ','pack')


        self.common_tab_init()
        self.data_tab_init()
        self.flow_tab_init()
        self.builtin_tab_init()
        self.turtle4t_tab_init()
        self.physics_tab_init()
        self.auto_tab_init()
        self.pil_tab_init()

        #notebook event
        self.notebook.bind('<<NotebookTabChanged>>',self.on_tab_changed)
        self.notebook.bind('<Button-1>',self.on_tab_click)




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
                menu_display='"Hello World!"',
                code='"Hello World!"',
                code_display='"Hello World!"',
                note='你好世界(字串)',
                long_note=True ))
        DropdownPostit(tab_name='common', code_list = temp_code_list,
            postfix_enter=False).pack(side=tk.TOP, anchor='w', padx=2, pady=8)


        temp_code_list = []
        temp_code_list.append(CodeNTuple(
                menu_display='輸入 input',
                code="input('請輸入: ')",
                code_display="input('請輸入: ')",
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
                code="if __name__=='__main__':\n___",
                code_display="if __name__ == '__main__':\n    ___",
                note='主要執行模組',
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
        temp_code_list.append(CodeNTuple(
                menu_display='浮點數 float',
                code='float()',
                code_display='float()',
                note='轉成浮點數類型',
                long_note=False ))
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
                note='傳回字串類型',
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
                code="清單 = [10,20,30]",
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
                code='len()',
                code_display='len()',
                note='長度',
                long_note=False))
        temp_code_list.append(CodeNTuple(
                menu_display='四捨五入 round',
                code='round()',
                code_display='round()',
                note='四捨五入',
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
                menu_display='從隨機模組匯入randint',
                code='from random import randint',
                code_display='from random import randint',
                note='從隨機模組匯入randint',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='從隨機模組匯入choice',
                code='from random import choice',
                code_display='from random import choice',
                note='從隨機模組匯入choice',
                long_note=True))
        DropdownPostit(tab_name='builtin', code_list = temp_code_list,
            postfix_enter=True).pack(side=tk.TOP, anchor='w', padx=2, pady=8)

        temp_code_list = []
        temp_code_list.append(CodeNTuple(
                menu_display='隨機挑個整數 randint',
                code='randint(1,10)',
                code_display='randint(1,10)',
                note='隨機挑個整數',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='隨機挑個項目 choice',
                code='choice(清單)',
                code_display='choice(清單)',
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
                menu_display='從時間模組匯入time',
                code='from time import time',
                code_display='from time import time',
                note='從時間模組匯入time',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='從時間模組匯入sleep',
                code='from time import sleep',
                code_display='from time import sleep',
                note='從時間模組匯入sleep',
                long_note=True))
        DropdownPostit(tab_name='builtin', code_list = temp_code_list,
            postfix_enter=True).pack(side=tk.TOP, anchor='w', padx=2, pady=8)

        temp_code_list = []
        temp_code_list.append(CodeNTuple(
                menu_display='時間(累計秒數) time',
                code='time()',
                code_display='time()',
                note='時間(累計秒數)',
                long_note=False))
        temp_code_list.append(CodeNTuple(
                menu_display='暫停幾秒(睡眠) sleep',
                code='sleep(1)',
                code_display='sleep(1)',
                note='暫停幾秒(睡眠)',
                long_note=False))
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
            postfix_enter=True).pack(side=tk.TOP, anchor='w', padx=2, pady=8)



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
                menu_display='走到',
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
                code="字型 = ('標楷的',12,'normal')",
                code_display="字型 = ('標楷的',12,'normal')",
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
                code='def 功能函式(x, y):\n___',
                code_display='def 功能函式(x, y):\n    ___',
                note='自訂功能(滑鼠點擊時)',
                long_note=True ))  
        temp_code_list.append(CodeNTuple(
                menu_display='  define mouse click function ',
                code='def func(x, y):\n___',
                code_display='def func(x, y):\n    ___',
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
                code='def 功能函式():\n___',
                code_display='def 功能函式():\n    ___',
                note='自訂功能(鍵盤按下時)',
                long_note=True ))  
        temp_code_list.append(CodeNTuple(
                menu_display='  define key press function ',
                code='def func():\n___',
                code_display='def func():\n    ___',
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
        example_vars = ['物理舞台','球','中央座標','座標'] 
        tab.popup_init(example_vars)

        f = font.Font(size=11, weight=font.NORMAL, family='Consolas')
        label =ttk.Label(common_postit_tabs['physics'].frame.interior, 
                text='【遊戲物理引擎】', 
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
                menu_display='  from pie4t import *',
                code='from pie4t import *',
                code_display='from pie4t import *',
                note='從pie4t模組匯入全部',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='import 物理模組 ',
                code='import 物理模組',
                code_display='import 物理模組',
                note='匯入pie4t',
                long_note=True ))
        temp_code_list.append(CodeNTuple(
                menu_display='  import pie4t ',
                code='import pie4t',
                code_display='import pie4t',
                note='匯入物理模組',
                long_note=True ))
        DropdownPostit(tab_name='physics', code_list = temp_code_list,
            postfix_enter=True).pack(side=tk.TOP, anchor='w', padx=2, pady=8)



        # dropdown list postit
        temp_code_list = []
        temp_code_list.append(CodeNTuple(
                menu_display='物理舞台',
                code='物理舞台 = 物理引擎()',
                code_display='物理舞台 = 物理引擎()',
                note='物理舞台',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='物理舞台及寬高',
                code='物理舞台 = 物理引擎(600, 600)',
                code_display='物理舞台 = 物理引擎(600, 600)',
                note='物理舞台及設定寬高',
                long_note=True))
        DropdownPostit(tab_name='physics', code_list = temp_code_list,
            postfix_enter=False).pack(side=tk.TOP, anchor='w', padx=2, pady=8)

        # dropdown list postit
        temp_code_list = []
        temp_code_list.append(CodeNTuple(
                menu_display='物理舞台.重力',
                code='物理舞台.重力 = 0, -500',
                code_display='物理舞台.重力 = 0, -500',
                note='gravity',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='  stage.gravity',
                code='stage.gravity = 0, -900',
                code_display='stage.gravity = 0, -900',
                note='設定重力',
                long_note=True))
        DropdownPostit(tab_name='physics', code_list = temp_code_list,
            postfix_enter=False).pack(side=tk.TOP, anchor='w', padx=2, pady=8)


        # dropdown list postit
        temp_code_list = []
        # temp_code_list.append(CodeNTuple(
        #         menu_display='開始模擬',
        #         code='開始模擬()',
        #         code_display='開始模擬()',
        #         note='simulate',
        #         long_note=False))
        # temp_code_list.append(CodeNTuple(
        #         menu_display='  simulate',
        #         code='simulate()',
        #         code_display='simulate()',
        #         note='開始模擬',
        #         long_note=False))
        temp_code_list.append(CodeNTuple(
                menu_display='模擬主迴圈',
                code='模擬主迴圈()',
                code_display='模擬主迴圈()',
                note='mainloop',
                long_note=False))
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
                menu_display='新增圓球並設值',
                code='球 = 新增圓球(半徑=20)',
                code_display='球 = 新增圓球(半徑=20)',
                note='新增圓球並設值',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='新增圓球函式',
                code='新增圓球(半徑=20)',
                code_display='新增圓球(半徑=20)',
                note='add circle',
                long_note=True))
        # temp_code_list.append(CodeNTuple(
        #         menu_display='  add_circle',
        #         code='add_circle()',
        #         code_display='add_circle()',
        #         note='新增圓球',
        #         long_note=False))

        DropdownPostit(tab_name='physics', code_list = temp_code_list,
            postfix_enter=False).pack(side=tk.TOP, anchor='w', padx=2, pady=8)

        # dropdown list postit
        temp_code_list = []
        temp_code_list.append(CodeNTuple(
                menu_display='位置(取值)',
                code='球.位置',
                code_display='球.位置',
                note='位置(取值)',
                long_note=False))
        temp_code_list.append(CodeNTuple(
                menu_display=' 位置(設值)',
                code='球.位置 = (300, 500)',
                code_display='球.位置 = (300, 500)',
                note='位置(設值)',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='質量(取值)',
                code='球.質量',
                code_display='球.質量',
                note='質量(取值)',
                long_note=False))
        temp_code_list.append(CodeNTuple(
                menu_display=' 質量(設值)',
                code='球.質量 = 314',
                code_display='球.質量 = 314',
                note='質量(設值)(須大於0)',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='密度(取值)',
                code='球.密度',
                code_display='球.密度',
                note='密度(取值)',
                long_note=False))
        temp_code_list.append(CodeNTuple(
                menu_display=' 密度(設值)',
                code='球.密度 = 1',
                code_display='球.密度 = 1',
                note='密度(設值)(須大於0)',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='摩擦(取值)',
                code='球.摩擦',
                code_display='球.摩擦',
                note='摩擦(取值)',
                long_note=False))
        temp_code_list.append(CodeNTuple(
                menu_display=' 摩擦(設值)',
                code='球.摩擦 = 0.5',
                code_display='球.摩擦 = 0.5',
                note='摩擦(設值)(須大於0)',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='彈性(取值)',
                code='球.彈性',
                code_display='球.彈性',
                note='彈性(取值)',
                long_note=False))
        temp_code_list.append(CodeNTuple(
                menu_display=' 彈性(設值)',
                code='球.彈性 = 0.98',
                code_display='球.彈性 = 0.98',
                note='彈性(設值)(須在0到1之間)',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='半徑(取值)(唯讀)',
                code='球.半徑',
                code_display='球.半徑',
                note='半徑(取值)(唯讀)',
                long_note=False))
        DropdownPostit(tab_name='physics', code_list = temp_code_list,
            postfix_enter=False).pack(side=tk.TOP, anchor='w', padx=2, pady=8)


        # dropdown list postit
        temp_code_list = []
        temp_code_list.append(CodeNTuple(
                menu_display='按下滑鼠時',
                code='def 按下滑鼠時(x, y):\n___\n',
                code_display='def 按下滑鼠時(x, y):\n    ___',
                note='按下滑鼠時',
                long_note=True))
        DropdownPostit(tab_name='physics', code_list = temp_code_list,
            postfix_enter=False).pack(side=tk.TOP, anchor='w', padx=2, pady=8)

    def auto_tab_init(self):
        # title and setup tool
        #tab = common_postit_tabs['auto']
        #example_vars = ['',] 
        #tab.popup_init(example_vars)

        f = font.Font(size=11, weight=font.NORMAL, family='Consolas')
        label =ttk.Label(common_postit_tabs['auto'].frame.interior, 
                text='【自動化PyAutoGui】', 
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
                code='import pyautogui',
                code_display='import pyautogui',
                note='匯入pyautogui模組',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='匯入pyperclip模組',
                code='import pyperclip',
                code_display='import pyperclip',
                note='匯入pyperclip模組',
                long_note=True))
        DropdownPostit(tab_name='auto', code_list = temp_code_list,
            postfix_enter=True).pack(side=tk.TOP, anchor='w', padx=2, pady=8)


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
                menu_display='滑鼠位置 position',
                code='pyautogui.position()',
                code_display='pyautogui.position()',
                note='滑鼠位置',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='螢幕大小 size',
                code='pyautogui.size()',
                code_display='pyautogui.size()',
                note='螢幕大小',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='在螢幕內嗎 onScreen',
                code='pyautogui.onScreen(100, 100)',
                code_display='pyautogui.onScreen(100, 100)',
                note='在螢幕內嗎',
                long_note=True))
        DropdownPostit(tab_name='auto', code_list = temp_code_list,
            postfix_enter=False).pack(side=tk.TOP, anchor='w', padx=2, pady=8)

        # dropdown list postit
        temp_code_list = []
        temp_code_list.append(CodeNTuple(
                menu_display='每次暫停(秒) PAUSE',
                code='pyautogui.PAUSE = 1',
                code_display='pyautogui.PAUSE = 1',
                note='每次暫停(秒)',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='失效安全  FAILSAFE',
                code='pyautogui.FAILSAFE = True',
                code_display='pyautogui.FAILSAFE = True',
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
                menu_display='點擊滑鼠(滑鼠按鍵)',
                code='pyautogui.click(button="left")',
                code_display='pyautogui.click(button="left")',
                note='點擊滑鼠(滑鼠按鍵)',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='移動滑鼠(到座標在幾秒內)',
                code='pyautogui.moveTo(100, 100, 2)',
                code_display='pyautogui.moveTo(100, 100, 2)',
                note='移動滑鼠(到座標在幾秒內)',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='移動滑鼠(相對距離在幾秒內)',
                code='pyautogui.moveRel(0, 50, 1)',
                code_display='pyautogui.moveRel(0, 50, 1)',
                note='移動滑鼠(相對距離在幾秒內)',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='拖曳滑鼠(到座標在幾秒內)',
                code='pyautogui.dragTo(100, 100, 2)',
                code_display='pyautogui.dragTo(100, 100, 2)',
                note='拖曳滑鼠(到座標在幾秒內)',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='拖曳滑鼠(相對距離在幾秒內)',
                code='pyautogui.dragRel(0, 50, 1)',
                code_display='pyautogui.dragRel(0, 50, 1)',
                note='拖曳滑鼠(相對距離在幾秒內)',
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
                code='pyautogui.press("space")',
                code_display='pyautogui.press("space")',
                note='按鍵',
                long_note=True))

        temp_code_list.append(CodeNTuple(
                menu_display='按著鍵 keyDown',
                code='pyautogui.keyDown("space")',
                code_display='pyautogui.keyDown("space")',
                note='按著鍵',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='放開鍵 keyUp',
                code='pyautogui.keyUp("space")',
                code_display='pyautogui.keyUp("space")',
                note='放開鍵',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='組合鍵 hotkey',
                code='pyautogui.hotkey("ctrl","v")',
                code_display='pyautogui.hotkey("ctrl","v")',
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
                code='pyautogui.KEYBOARD_KEYS',
                code_display='pyautogui.KEYBOARD_KEYS',
                note='鍵盤列表',
                long_note=True))
        DropdownPostit(tab_name='auto', code_list = temp_code_list,
            postfix_enter=False).pack(side=tk.TOP, anchor='w', padx=2, pady=8)

        # separator and note
        ttk.Separator(common_postit_tabs['auto'].frame.interior, orient=tk.HORIZONTAL
            ).pack(side=tk.TOP, fill=tk.X, padx=0, pady=10)
        f = font.Font(size=11, weight=font.NORMAL, family='Consolas')
        ttk.Label(common_postit_tabs['auto'].frame.interior, 
                    
                    text=' >> 剪貼簿',
                    font=f,   
                    compound=tk.LEFT, 
                ).pack(side=tk.TOP, padx=5, pady=8, anchor='w')

        # dropdown list postit
        temp_code_list = []
        temp_code_list.append(CodeNTuple(
                menu_display='複製到剪貼簿 copy',
                code='pyperclip.copy("你好")',
                code_display='pyperclip.copy("你好")',
                note='複製到剪貼簿',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='從剪貼簿貼上 paste',
                code='pyperclip.paste("你好")',
                code_display='pyperclip.paste("你好")',
                note='從剪貼簿貼上',
                long_note=True))
        DropdownPostit(tab_name='auto', code_list = temp_code_list,
            postfix_enter=False).pack(side=tk.TOP, anchor='w', padx=2, pady=8)



    def pil_tab_init(self):
        # title and setup tool
        tab = common_postit_tabs['pil']
        example_vars = ['座標','圖片','區域','像素','寬高','檔案路徑','開始時間','經過時間',] 
        tab.popup_init(example_vars)

        f = font.Font(size=11, weight=font.NORMAL, family='Consolas')
        label =ttk.Label(common_postit_tabs['pil'].frame.interior, 
                text='【影像處理pillow】', 
                image= common_images['gear'],
                font=f,
                compound=tk.RIGHT,
                )                
        label.pack(side=tk.TOP, padx=5, pady=8,anchor='w')
        label.bind("<Button-1>", common_postit_tabs['pil'].popup)   




        # dropdown list postit
        temp_code_list = []
        temp_code_list.append(CodeNTuple(
                menu_display='從PIL匯入Image模組',
                code='from PIL import Image',
                code_display='from PIL import Image',
                note='從PIL模組匯入Image',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='從PIL匯入ImageGrab模組',
                code='from PIL import ImageGrab',
                code_display='from PIL import ImageGrab',
                note='從PIL模組匯入ImageGrab',
                long_note=True))
        DropdownPostit(tab_name='pil', code_list = temp_code_list,
            postfix_enter=True).pack(side=tk.TOP, anchor='w', padx=2, pady=8)

        # separator and note
        ttk.Separator(common_postit_tabs['pil'].frame.interior, orient=tk.HORIZONTAL
            ).pack(side=tk.TOP, fill=tk.X, padx=0, pady=10)
        f = font.Font(size=11, weight=font.NORMAL, family='Consolas')
        ttk.Label(common_postit_tabs['pil'].frame.interior, 
                    
                    text=' >> 建立影像物件',
                    font=f,   
                    compound=tk.LEFT, 
                ).pack(side=tk.TOP, padx=5, pady=8, anchor='w')

        # dropdown list postit
        temp_code_list = []
        temp_code_list.append(CodeNTuple(
                menu_display='Image.open 開啟影像',
                code="圖片 = Image.open('檔名')",
                code_display="圖片 = Image.open('檔名')",
                note='開啟影像(傳回影像)',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='ImageGrab.grab 截取螢幕',
                code='圖片 = ImageGrab.grab()',
                code_display='圖片 = ImageGrab.grab()',
                note='截取螢幕(傳回影像)',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='ImageGrab.grab 截取區域中螢幕',
                code='圖片 = ImageGrab.grab(區域)',
                code_display='圖片 = ImageGrab.grab(區域)',
                note='截取區域螢幕(傳回影像)',
                long_note=True))
        DropdownPostit(tab_name='pil', code_list = temp_code_list,
            postfix_enter=False).pack(side=tk.TOP, anchor='w', padx=2, pady=8)

        # separator and note
        ttk.Separator(common_postit_tabs['pil'].frame.interior, orient=tk.HORIZONTAL
            ).pack(side=tk.TOP, fill=tk.X, padx=0, pady=10)
        f = font.Font(size=11, weight=font.NORMAL, family='Consolas')
        ttk.Label(common_postit_tabs['pil'].frame.interior, 
                    
                    text=' >> 影像資訊',
                    font=f,   
                    compound=tk.LEFT, 
                ).pack(side=tk.TOP, padx=5, pady=8, anchor='w')

        # dropdown list postit
        temp_code_list = []
        temp_code_list.append(CodeNTuple(
                menu_display='影像格式 .format',
                code='圖片.format',
                code_display='圖片.format',
                note='影像格式',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='影像寬高 .size',
                code='圖片.size',
                code_display='圖片.size',
                note='影像寬高',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='影像模式 .mode',
                code='圖片.mode',
                code_display='圖片.mode',
                note='影像模式',
                long_note=True))
        DropdownPostit(tab_name='pil', code_list = temp_code_list,
            postfix_enter=False).pack(side=tk.TOP, anchor='w', padx=2, pady=8)

        # separator and note
        ttk.Separator(common_postit_tabs['pil'].frame.interior, orient=tk.HORIZONTAL
            ).pack(side=tk.TOP, fill=tk.X, padx=0, pady=10)
        f = font.Font(size=11, weight=font.NORMAL, family='Consolas')
        ttk.Label(common_postit_tabs['pil'].frame.interior, 
                    
                    text=' >> 影像操作',
                    font=f,   
                    compound=tk.LEFT, 
                ).pack(side=tk.TOP, padx=5, pady=8, anchor='w')

        # dropdown list postit
        temp_code_list = []
        temp_code_list.append(CodeNTuple(
                menu_display='顯示影像 .show',
                code='圖片.show()',
                code_display='圖片.show()',
                note='顯示影像',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='縮圖 .thumbnail',
                code='圖片.thumbnail(寬高)',
                code_display='圖片.thumbnail(寬高)',
                note='縮圖',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='影像存檔 .save',
                code='圖片.save(檔名)',
                code_display='圖片.save(檔名)',
                note='影像存檔',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='影像貼上 .paste',
                code='圖片.paste(圖片2, 座標)',
                code_display='圖片.paste(圖片2,座標)',
                note='影像貼上',
                long_note=True))
        DropdownPostit(tab_name='pil', code_list = temp_code_list,
            postfix_enter=False).pack(side=tk.TOP, anchor='w', padx=2, pady=8)


        # dropdown list postit
        temp_code_list = []
        temp_code_list.append(CodeNTuple(
                menu_display='取出部份影像 .crop',
                code='圖片2 = 圖片.crop(區域)',
                code_display='圖片2 = 圖片.crop(區域)',
                note='取出部份影像(傳回新影像)',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='改變影像大小 .resize',
                code='圖片2 = 圖片.resize(寬高)',
                code_display='圖片2 = 圖片.resize(寬高)',
                note='改變影像大小(傳回新影像)',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='旋轉影像 .rotate',
                code='圖片2 = 圖片.rotate(90)',
                code_display='圖片2 = 圖片.rotate(90)',
                note='旋轉影像(傳回新影像)',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='取出像素 .getpixel',
                code='像素 = 圖片.getpixel(座標)',
                code_display='像素 = 圖片.getpixel(座標)',
                note='取出像素',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='顏色清單 .getcolors',
                code='清單 = 圖片.getcolors()',
                code_display='清單 = 圖片.getcolors()',
                note='顏色清單(預設256色)',
                long_note=True)) 
        temp_code_list.append(CodeNTuple(
                menu_display='轉成全彩影像 .convert',
                code='圖片2 = 圖片.convert("RGB")',
                code_display='圖片2 = 圖片.convert("RGB")',
                note='轉成全彩影像(傳回新影像)',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='轉成灰階影像 .convert',
                code='圖片2 = 圖片.convert("L")',
                code_display='圖片2 = 圖片.convert("L")',
                note='轉成灰階影像(傳回新影像)',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='轉成黑白影像 .convert',
                code='圖片2 = 圖片.convert("1")',
                code_display='圖片2 = 圖片.convert("1")',
                note='轉成黑白影像(傳回新影像)',
                long_note=True))
        DropdownPostit(tab_name='pil', code_list = temp_code_list,
            postfix_enter=False).pack(side=tk.TOP, anchor='w', padx=2, pady=8)

        # separator and note
        ttk.Separator(common_postit_tabs['pil'].frame.interior, orient=tk.HORIZONTAL
            ).pack(side=tk.TOP, fill=tk.X, padx=0, pady=10)
        f = font.Font(size=11, weight=font.NORMAL, family='Consolas')
        ttk.Label(common_postit_tabs['pil'].frame.interior, 
                    
                    text=' >> 常用變數',
                    font=f,   
                    compound=tk.LEFT, 
                ).pack(side=tk.TOP, padx=5, pady=8, anchor='w')

        # dropdown list postit
        temp_code_list = []
        temp_code_list.append(CodeNTuple(
                menu_display='設定區域',
                code='區域 = [0, 0, 100, 100]',
                code_display='區域 = [0, 0, 100, 100]',
                note='設定區域(左上及右下座標)',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='設定寬高',
                code='寬高 = [100, 100]',
                code_display='寬高 = [100, 100]',
                note='設定寬高',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='設定座標',
                code='座標 = (0, 0)',
                code_display='座標 = (0, 0)',
                note='設定座標',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='設定檔案路徑',
                code="檔案路徑 = r''",
                code_display="檔案路徑 = r' '",
                note='設定檔案路徑',
                long_note=True))
        DropdownPostit(tab_name='pil', code_list = temp_code_list,
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
                                    menu_display='如果 不然就(否則) if else ',
                                    code='if 條件:\n___\nelse:\n___',
                                    code_display='if 條件:\n    ___\nelse:\n'
                                    '    ___   ',
                                    note='如果…\n\n不然就(否則)',
                                    long_note=False))
        temp_code_list.append(CodeNTuple(
                                    menu_display='如果 if ',
                                    code='if 條件:\n___',
                                    code_display='if 條件:\n    ___',
                                    note='如果',
                                    long_note=False ))
        temp_code_list.append(CodeNTuple(
            menu_display='不然如果 (否則) if elif else ',
            code='if 條件:\n___\nelif 條件:\n___\nelse:\n___',
            code_display='if 條件:\n    ___\nelif 條件:\n    ___\nelse:\n    ___',
            note='如果\n\n不然如果\n\n不然就(否則)',
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
                                    code='while True:\n___',
                                    code_display='while True:\n    ___\n',
                                    note='重複無限次',
                                    long_note=False ))
        temp_code_list.append(CodeNTuple(
                                    menu_display='有條件重複 while ',
                                    code='while 條件:\n___',
                                    code_display='while 條件:\n    ___\n',
                                    note='當成立時\n\n重複',
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
                menu_display='重複(依次數) for in range  ',
                code='for 索引 in range(次數):\n___',
                code_display='for 索引 in range(次數):\n    ___',
                note='重複(依次數)',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='重複(從開始不含結束) for in range  ',
                code='for 索引 in range(開始, 結束):\n___',
                code_display='for 索引 in range(開始, 結束):\n    ___',
                note='重複(從開始不含結束)',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='重複(從開始步進不含結束) for in range  ',
                code='for 索引 in range(開始, 結束, 步進):\n___',
                code_display='for 索引 in range(開始, 結束, 步進):\n    ___',
                note='重複(從開始步進不含結束)',
                long_note=True))
        temp_code_list.append(CodeNTuple(
                menu_display='逐一取出項目 for in 清單  ',
                code='for 項目 in 清單:\n___',
                code_display='for 項目 in 清單:\n    ___',
                note='從清單中逐一取出項目',
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
                    text=' >> 例外(錯誤)處理',
                    font=f,    
                    compound=tk.LEFT, 
                ).pack(side=tk.TOP, padx=5, pady=8, anchor='w')

        # dropdown list postit
        temp_code_list = []
        temp_code_list.append(CodeNTuple(
                menu_display='捕捉例外(錯誤)',
                code='try:\n___\nexcept Exception:\n___',
                code_display='try:\n    ___\nexcept Exception:\n    ___',
                note='測試\n\n例外\n(錯誤)',
                long_note=False))

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
                menu_display='自訂功能函式',
                code='def 功能函式(參數1, 參數2):\n___',
                code_display='def 功能函式(參數1, 參數2):\n    ___',
                note='自訂功能函式',
                long_note=True ))  
        # temp_code_list.append(CodeNTuple(
        #         menu_display='  define  function ',
        #         code='def func(p1, p2):\n___',
        #         code_display='def func(p1, p2):\n    ___',
        #         note='自訂功能函式',
        #         long_note=True ))
        temp_code_list.append(CodeNTuple(
                menu_display='呼叫功能函式',
                code='功能函式(引數1, 引數2)',
                code_display='功能函式(引數1, 引數2)',
                note='呼叫功能函式',
                long_note=True ))    
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
                menu_display='功能函式返回(跳出) return',
                code='return',
                code_display='return',
                note='功能函式返回(跳出)',
                long_note=False))

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

        EnterToolPostit(self.edit_toolbar).pack(side=tk.RIGHT,padx=3, pady=3,
                    )

        BackspaceToolPostit(self.edit_toolbar).pack(side=tk.RIGHT,padx=3, pady=3,
                    )

        







        




    def notebook_init(self):
        #notebook_frame = VerticallyScrollableFrame(self)
        notebook_frame = ttk.Frame(self)
        notebook_frame.pack(side=tk.TOP, fill=tk.Y, expand=True)
        #style = ttk.Style(self.interior)
        #style = ttk.Style(notebook_frame.interior)
        style = ttk.Style(notebook_frame)
        style.configure('lefttab.TNotebook', tabposition='wn')
        #self.notebook = ttk.Notebook(self.interior, style='lefttab.TNotebook')
        #self.notebook = ttk.Notebook(notebook_frame.interior, style='lefttab.TNotebook')
        self.notebook = ttk.Notebook(notebook_frame, style='lefttab.TNotebook')
        self.notebook.pack(side='top',fill="both", expand="true")

    def add_tab(self, name, label, tab_type):

        tab = PostitTab(name, label, tab_type)
        common_postit_tabs[name] = tab

        #tab.frame = ttk.Frame(self.notebook)        
        tab.frame = VerticallyScrollableFrame(self.notebook)
        self.notebook.add(tab.frame,
                          text = tab.label,
                          image = tab.image,
                          compound="top",
                        )
        # self.notebook.add(tab.frame,
        #                   text = tab.label,
        #                   image = tab.image,
        #                   compound="top",
        #                 )

        tab.index = self.notebook.index('end')
        return tab

    def on_tab_click(self, event):
        """record focus widget"""
        self.last_focus = get_workbench().focus_get()

    def on_tab_changed(self, event):
        """restore last focus widget"""
        if self.last_focus:
            self.last_focus.focus_set()
            self.last_focus = None
        

def try_thonny():
    pass
    
    editor = get_workbench().get_editor_notebook().get_current_editor()
    text_widget = editor.get_text_widget()
  
    s = text_widget.get('1.0', 'end-1c')
    s = s.replace('\n', '¶\n')
    s = s.replace(' ', '·')
    text_widget.delete('1.0', 'end-1c')
    text_widget.insert('1.0', s)
    text_widget.config(state=tk.DISABLED)



def load_plugin():
    """postit plugin start point"""

    get_workbench().add_view(PythonPostitView, 'Python便利貼', 'nw')

    #for test
    # get_workbench().add_command(command_id="try_thonny",
    #                                 menu_name="tools",
    #                                 command_label="測試thonny",
    #                                 handler=try_thonny,
    #                                 default_sequence="<F2>"
    #                                 )



