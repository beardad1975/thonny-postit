import os 

import tkinter as tk
from tkinter import ttk
from pathlib import Path
from PIL import Image, ImageTk

from thonny import get_workbench, get_shell, get_runner
from thonny.ui_utils import VerticallyScrollableFrame
from thonny.common import ToplevelCommand

from .base_postit import BasePostit
from .enclosed_postit import EnclosedPostit
from .dropdown_postit import DropdownPostit
from .common import common_postit_tabs, CodeNTuple
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
        {"filename":'color0.png', 'fill_color':'#4c97ff', 'font_color':'white'},
        {"filename":'color1.png', 'fill_color':'#9966ff', 'font_color':'white'},    
        {"filename":'color2.png', 'fill_color':'#d65cd6', 'font_color':'white'},
        {"filename":'color3.png', 'fill_color':'#ffd500', 'font_color':'black'},
        {"filename":'color4.png', 'fill_color':'#ffab19', 'font_color':'black'},
        {"filename":'color5.png', 'fill_color':'#4cbfe6', 'font_color':'black'},
        {"filename":'color6.png', 'fill_color':'#40bf4a', 'font_color':'white'},
        {"filename":'color7.png', 'fill_color':'#ff6680', 'font_color':'black'},
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
        abs_image_path = Path(__file__).parent / 'images' / color['filename']
        im = Image.open(abs_image_path)       
        self.image = ImageTk.PhotoImage(im) 
                
        
    @classmethod
    def pick_color(cls):
        c = cls.color_data[cls.color_circular_index]
        cls.color_circular_index += 1
        if cls.color_circular_index >= cls.color_num:
            cls.color_circular_index = 0
        return c




class PythonPostitView(VerticallyScrollableFrame):
    def __init__(self, master):
        super().__init__(master) 
        self.toolbar_init()
        self.notebook_init()
        self.last_focus = None
        self.symbol_row_index = 0

        #to do  :self.module_postit_tabs = {}

        #add notebook tabs
        self.add_tab('common', '常用','basic')
        self.add_tab('turtle4t', '海龜\n模組','basic')
        #self.add_tab('symbol', '符號','basic')
        self.add_tab('data', '資料\n類型','basic')
        self.add_tab('flow', '流程','basic')
        self.add_tab('function', '函式','basic')

        self.common_tab_init()
        self.turtle4t_tab_init()
        self.flow_tab_init()

        #notebook event
        self.notebook.bind('<<NotebookTabChanged>>',self.on_tab_changed)
        self.notebook.bind('<Button-1>',self.on_tab_click)

    def common_tab_init(self):
        ### common postit
        # dropdown list postit
        temp_code_list = []
        temp_code_list.append(CodeNTuple(code='111',
                                        code_display='1111',
                                        note='11111',
                                        long_note=False))
        temp_code_list.append(CodeNTuple(code='222',
                                        code_display='2222',
                                        note='22222',
                                        long_note=True ))
        temp_code_list.append(CodeNTuple(code='333',
                                        code_display='3333',
                                        note='33333',
                                        long_note=False ))
        DropdownPostit(tab_name='common', code_list = temp_code_list,
            postfix_enter=False).pack(side=tk.TOP, anchor='w', padx=8, pady=8)


        EnclosedPostit(tab_name='common',
                       enclosed_head='print(', 
                       enclosed_tail=')', 
                       code_display=None,
                       note='印出',
                       postfix_enter=False,
                       long_note=False,
        ).pack(side=tk.TOP, anchor='w', padx=8, pady=8)

        BasePostit(tab_name='common',
                           code='"Hello World!"',
                           code_display='"Hello World!"',
                           note="你好世界(字串)",
                           postfix_enter=False,
                           long_note=True,
        ).pack(side=tk.TOP, anchor='w', padx=8, pady=8)

        BasePostit(tab_name='common',
                           code="dir()",
                           code_display="dir()",
                           note="物件屬性",
                           postfix_enter=False,
        ).pack(side=tk.TOP, anchor='w', padx=8, pady=8)


    def turtle4t_tab_init(self):
                ### turtle 4 t postit

        BasePostit(tab_name='turtle4t',
                           code='from 海龜模組 import *',
                           code_display='from 海龜模組 import *',
                           note="從海龜模組匯入",
                           postfix_enter=False,
                           long_note=True,
        ).pack(side=tk.TOP, anchor='w', padx=8, pady=8)

        BasePostit(tab_name='turtle4t',
                           code='向前(50)',
                           code_display='向前(50)',
                           note="forward",
                           postfix_enter=False,
                           long_note=False,
        ).pack(side=tk.TOP, anchor='w', padx=8, pady=8)

        BasePostit(tab_name='turtle4t',
                           code='向後(50)',
                           code_display='向後(50)',
                           note="back",
                           postfix_enter=False,
                           long_note=False,
        ).pack(side=tk.TOP, anchor='w', padx=8, pady=8)

        BasePostit(tab_name='turtle4t',
                           code='右轉(90)',
                           code_display='右轉(90)',
                           note="right",
                           postfix_enter=False,
                           long_note=False,
        ).pack(side=tk.TOP, anchor='w', padx=8, pady=8)

        BasePostit(tab_name='turtle4t',
                           code='左轉(90)',
                           code_display='左轉(90)',
                           note="left",
                           postfix_enter=False,
                           long_note=False,
        ).pack(side=tk.TOP, anchor='w', padx=8, pady=8)

        BasePostit(tab_name='turtle4t',
                           code='位置()',
                           code_display='位置()',
                           note="position",
                           postfix_enter=False,
                           long_note=True,
        ).pack(side=tk.TOP, anchor='w', padx=8, pady=8)

    def flow_tab_init(self):
                # flow tab
        BasePostit(tab_name='flow',
                           code='if 條件:\n___\nelse:\n___',
                           code_display='if 條件:\n    ___\nelse:\n'
                                        '    ___',
                           note="如果\n\n其他",
                           #long_note=True,
                           postfix_enter=False,
        ).pack(side=tk.TOP, anchor='w', padx=8, pady=8)

        BasePostit(tab_name='flow',
                           code='if 條件 :\n__\nelif 條件:\n'
                                '__\nelse :\n__',
                           code_display='if 條件:\n    __\n'
                                        'elif 條件:\n    __\n'
                                        'else:\n    __',
                           note="如果\n\n不然如果\n\n其他",
                           #long_note=True,
                           postfix_enter=False,
        ).pack(side=tk.TOP, anchor='w', padx=8, pady=8)

        BasePostit(tab_name='flow',
                           code='while 條件:\n___',
                           code_display='while 條件:\n    ___\n',
                                        
                           note="當…時重複",
                           #long_note=True,
                           postfix_enter=False,
        ).pack(side=tk.TOP, anchor='w', padx=8, pady=8)

        BasePostit(tab_name='flow',
                           code='for i in range(10):\n___',
                           code_display='for i in range(10):\n    ___',
                                        
                           note="重複次數",
                           long_note=True,
                           postfix_enter=False,
        ).pack(side=tk.TOP, anchor='w', padx=8, pady=8)

        BasePostit(tab_name='flow',
                           code='for 項目 in 清單:\n___',
                           code_display='for 項目 in 清單:\n    ___',
                                        
                           note="取出項目",
                           long_note=True,
                           postfix_enter=False,
        ).pack(side=tk.TOP, anchor='w', padx=8, pady=8)

    def tab_symbol_add_row(self, col1, col2=None, col3=None, col4=None):
        col1.grid(row=self.symbol_row_index, column=0, padx=5, pady=5)
        if col2:
            col2.grid(row=self.symbol_row_index, column=1, padx=5, pady=5)
        if col3:
            col3.grid(row=self.symbol_row_index, column=2, padx=5, pady=5)
        if col4:
            col4.grid(row=self.symbol_row_index, column=3, padx=5, pady=5)
        self.symbol_row_index += 1

    def toolbar_init(self):

        # var toolbar
        self.var_toolbar = ttk.Frame(self.interior)
        self.var_toolbar.pack(side=tk.TOP, fill=tk.X)
        
        # keep reference in common

        common.share_var_get_postit = VariableFetchToolPostit(
                self.var_toolbar, tool_name='variable_get')
        common.share_var_get_postit.pack(side=tk.RIGHT,padx=2, pady=4)

        common.share_var_assign_postit = VariableFetchToolPostit(
                self.var_toolbar, tool_name='variable_assign')
        common.share_var_assign_postit.pack(side=tk.RIGHT,padx=2, pady=4)



        VariableAddToolPostit(self.var_toolbar).pack(side=tk.RIGHT,
                padx=3, pady=5)

        common.share_vars_postit = VariableMenuPostit(self.var_toolbar)
        common.share_vars_postit.pack(side=tk.RIGHT,padx=2, pady=5)

        CommentToolPostit(self.var_toolbar).pack(side=tk.RIGHT,padx=1, pady=4)
        PilcrowToolPostit(self.var_toolbar).pack(side=tk.RIGHT,padx=1, pady=4)
        

        # edit_toolbar
        self.edit_toolbar = ttk.Frame(self.interior)
        self.edit_toolbar.pack(side=tk.TOP, fill=tk.X)
                
        EnterToolPostit(self.edit_toolbar).pack(side=tk.RIGHT,padx=2, pady=4)
        SymbolToolPostit(self.edit_toolbar).pack(side=tk.RIGHT,padx=2, pady=4)
        BackspaceToolPostit(self.edit_toolbar).pack(side=tk.RIGHT,padx=2, pady=4)
        PasteToolPostit(self.edit_toolbar).pack(side=tk.RIGHT,padx=2, pady=4)
        CopyToolPostit(self.edit_toolbar).pack(side=tk.RIGHT,padx=2, pady=4)
        CutToolPostit(self.edit_toolbar).pack(side=tk.RIGHT,padx=2, pady=4)
        RedoToolPostit(self.edit_toolbar).pack(side=tk.RIGHT,padx=2, pady=4)
        UndoToolPostit(self.edit_toolbar).pack(side=tk.RIGHT,padx=2, pady=4)
        IndentToolPostit(self.edit_toolbar).pack(side=tk.RIGHT,padx=2, pady=4)
        DedentToolPostit(self.edit_toolbar).pack(side=tk.RIGHT,padx=2, pady=4)
        




    def notebook_init(self):
        style = ttk.Style(self.interior)
        style.configure('lefttab.TNotebook', tabposition='wn')
        self.notebook = ttk.Notebook(self.interior, style='lefttab.TNotebook')
        self.notebook.pack(side='top',fill="both", expand="true")

    def add_tab(self, name, label, tab_type):

        tab = PostitTab(name, label, tab_type)
        common_postit_tabs[name] = tab

        tab.frame = ttk.Frame(self.notebook)        
        self.notebook.add(tab.frame,
                          text = tab.label,
                          image = tab.image,
                          compound="top",
                        )

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



