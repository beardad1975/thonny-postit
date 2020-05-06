import os 

import tkinter as tk
from tkinter import ttk
from pathlib import Path
from PIL import Image, ImageTk

from thonny import get_workbench, get_shell, get_runner
from thonny.codeview import CodeViewText
from thonny.ui_utils import VerticallyScrollableFrame
from thonny.common import ToplevelCommand

from .tools.enter_tool_postit import EnterToolPostit
from .tools.backspace_tool_postit import BackspaceToolPostit
from .tools.undo_tool_postit import UndoToolPostit, RedoToolPostit
from .tools.indenxt_tool_postit import IndentToolPostit, DedentToolPostit
from .tools.comment_tool_postit import CommentToolPostit
from .tools.pilcrow_tool_postit import PilcrowToolPostit
from .tools.variables_tool_postit import VariableMenuPostit

from .base_postit import BasePostit
#from .tool_postit import ToolPostit

from .enclosed_postit import EnclosedPostit
from .general_postit import GeneralPostit
from .property_postit import  PropertyPostit
from .symbol_postit import SymbolPostit
from .variable_postit import VariablePostit
from .if_postit import IfPostit
from .while_postit import WhilePostit
from .common import common_postit_tabs, common_vars_postit

### unicode return symbol \u23ce

#for test
from tkinter.messagebox import showinfo

class Pie4tView(VerticallyScrollableFrame):
    def __init__(self, master):
        super().__init__(master)

        pp = PropertyPostit(self.interior, 
                            object_name='物理舞台',
                            property_list=('重力x','重力y', '預設彈性'),
                            property_name='重力x',
                            property_value='20',
                            assign_flag=True,
                            #postfix_newline=False,
                            )
        pp.pack(side=tk.TOP, anchor='w', padx=5, pady=5)


class NameSymbolView(VerticallyScrollableFrame):
    def __init__(self, master):
        super().__init__(master)

        sp  = SymbolPostit(self.interior, '+')   
        sp.grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)

        sp  = SymbolPostit(self.interior, '-')   
        sp.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)

        sp  = SymbolPostit(self.interior, '*')   
        sp.grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)

        sp  = SymbolPostit(self.interior, '/')   
        sp.grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)

        sp  = SymbolPostit(self.interior, ',')   
        sp.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)

        sp  = SymbolPostit(self.interior, '=')   
        sp.grid(row=1, column=2, sticky=tk.W, padx=5, pady=5)

        vp = VariablePostit(self.interior)
        vp.grid(row=2, columnspan=3, sticky=tk.W,  padx=5, pady=5)


class PythonView(VerticallyScrollableFrame):
    def __init__(self, master):
        super().__init__(master)

        # p = Postit(self)
        # p.set_content('物理舞台.新增隨機方塊(\n\t位置x=7, \n\t位置y=5, \n\t密度=13,\n)')
        # p.set_help_label(' ... stage')
        # p.pack(side=tk.TOP, anchor='w', padx=5, pady=5)

        ip = IfPostit(self.interior)
        ip.pack(side=tk.TOP, anchor='w', padx=5, pady=5)
        wp = WhilePostit(self.interior)
        wp.pack(side=tk.TOP, anchor='w', padx=5, pady=5)



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
        self.init_toolbar()
        self.init_notebook()
        self.last_focus = None
        
        #to do  :self.module_postit_tabs = {}

        #add notebook tabs
        self.add_tab('basic', '基本','basic')
        self.add_tab('symbol', '符號','basic')
        self.add_tab('number', '數字','basic')
        self.add_tab('text', '文字','basic')
        self.add_tab('flow', '流程','basic')
        self.add_tab('pyautogui', '自動化\n模組','module')




        ##basic postit
        EnclosedPostit(tab_name='basic',
                       enclosed_head='print(', 
                       enclosed_tail=')', 
                       code_display=None,
                       note='印出',
                       postfix_enter=False
        ).pack(side=tk.TOP, anchor='w', padx=8, pady=8)

        BasePostit(tab_name='basic',
                           code='"Hello World!"',
                           code_display='"Hello World!"',
                           note="字串",
                           postfix_enter=False,
        ).pack(side=tk.TOP, anchor='w', padx=8, pady=8)

        BasePostit(tab_name='basic',
                           code='if _con__:\n_action_\nelse:\n_action_',
                           code_display='if else',
                           note="if else",
                           postfix_enter=False,
        ).pack(side=tk.TOP, anchor='w', padx=8, pady=8)

        BasePostit(tab_name='basic',
                           code="dir()",
                           code_display="dir()",
                           note="查詢屬性",
                           postfix_enter=True,
        ).pack(side=tk.TOP, anchor='w', padx=8, pady=8)

        EnclosedPostit(tab_name='basic',
                       enclosed_head='help(', 
                       enclosed_tail=')', 
                       code_display=None,
                       note='說明',
                       postfix_enter=False
        ).pack(side=tk.TOP, anchor='w', padx=8, pady=8)






        ###symbol postit
        BasePostit(tab_name='symbol',
                           code=" + ",
                           code_display="+",
                           note="加",
        ).pack(side=tk.TOP, anchor='w', padx=8, pady=8)

        BasePostit(tab_name='symbol',
                           code=" - ",
                           code_display="-",
                           note="減",
        ).pack(side=tk.TOP, anchor='w', padx=8, pady=8)

        BasePostit(tab_name='symbol',
                           code=" * ",
                           code_display="*",
                           note="乘",
        ).pack(side=tk.TOP, anchor='w', padx=8, pady=8)

        BasePostit(tab_name='symbol',
                           code=" / ",
                           code_display="/",
                           note="除",
        ).pack(side=tk.TOP, anchor='w', padx=8, pady=8)

        BasePostit(tab_name='pyautogui',
                           code="import pyautogui",
                           code_display="import pyautogui",
                           note="匯入模組功能",
        ).pack(side=tk.TOP, anchor='w', padx=8, pady=8)



        # EnclosedPostit(tab_name='symbol',
        #                enclosed_head='(', 
        #                enclosed_tail=')', 
        #                code_display=None,
        #                note='括號',
        #                postfix_enter=False
        # ).pack(side=tk.TOP, anchor='w', padx=8, pady=8)


        ###logic postit
        # ip = IfPostit(tab_name='logic')
        # ip.pack(side=tk.TOP, anchor='w', padx=8, pady=8)


        #notebook event
        self.notebook.bind('<<NotebookTabChanged>>',self.on_tab_changed)
        self.notebook.bind('<Button-1>',self.on_tab_click)
 
    def init_toolbar(self):
        self.var_toolbar = ttk.Frame(self.interior)
        self.var_toolbar.pack(side=tk.TOP, fill=tk.X)
        
        # keep reference in common
        common_vars_postit = VariableMenuPostit(self.var_toolbar)
        common_vars_postit.pack(side=tk.RIGHT,padx=3, pady=5)


        self.edit_toolbar = ttk.Frame(self.interior)
        self.edit_toolbar.pack(side=tk.TOP, fill=tk.X)
        
        
        EnterToolPostit(self.edit_toolbar).pack(side=tk.RIGHT,padx=3, pady=5)
        BackspaceToolPostit(self.edit_toolbar).pack(side=tk.RIGHT,padx=3, pady=5)
        RedoToolPostit(self.edit_toolbar).pack(side=tk.RIGHT,padx=3, pady=5)
        UndoToolPostit(self.edit_toolbar).pack(side=tk.RIGHT,padx=3, pady=5)
        IndentToolPostit(self.edit_toolbar).pack(side=tk.RIGHT,padx=3, pady=5)
        DedentToolPostit(self.edit_toolbar).pack(side=tk.RIGHT,padx=3, pady=5)
        CommentToolPostit(self.edit_toolbar).pack(side=tk.RIGHT,padx=3, pady=5)
        PilcrowToolPostit(self.edit_toolbar).pack(side=tk.RIGHT,padx=3, pady=5)




    def init_notebook(self):
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

    #showinfo("my command", get_workbench()._menus)
    # def replace(char, subchar):
    #     where = '1.0'; past_subchar = '1.0'
    #     while where:
    #         where = tainput.search(char, past_subchar, tk.END+'-1c')
    #         past_subchar= '{}+{}c'.format(where, len(subchar));
    #         past_char = '{}+{}c'.format(where, len(char));
    #         if where:
    #             tainput.delete(where, past_char)
    #             tainput.insert(where, subchar)
    #         else:
    #             return False

    #replace('\n', '¶\n')
    #replace(' ', '·')

    

    # get_runner().send_command(
    #     ToplevelCommand(
    #         "execute_source", source='dir()', tty_mode=True
    #     )
    # )

def load_plugin():
    """postit plugin start point"""

    #handle menu
    #get_workbench().get_menu("postit", "abc")


    #get_workbench().add_view(PythonView, '便貼python', 'se')
    #get_workbench().add_view(NameSymbolView, '便貼名稱符號', 'ne')
    #get_workbench().add_view(Pie4tView, '便貼pie4t', 'se')
    get_workbench().add_view(PythonPostitView, 'Python便利貼', 'nw')

    #for test
    get_workbench().add_command(command_id="try_thonny",
                                    menu_name="tools",
                                    command_label="測試thonny",
                                    handler=try_thonny,
                                    default_sequence="<F2>"
                                    )



    #     tk.Frame.__init__(self, master)
    #     # self.ent1 = tk.Entry(self)
    #     # self.ent1.pack()
    #     # self.ent2 = tk.Entry(self)
    #     # self.ent2.pack()
        
        
    #     self.post_button = tk.Button(self, text='新增隨機方塊(x, y)12345', command=self.post)
    #     #self.post_button.pack(anchor='w')
    #     self.post_button.pack(anchor='w',padx=5, pady=5)

    #     #right click menu
    #     self.popup_menu = tk.Menu(self, tearoff=0)
    #     self.popup_menu.add_command(label="修改", command=self.modify)
    #     self.post_button.bind("<Button-3>", self.popup) # Button-2 on Aqua

    # def popup(self, event):
    #     try:
    #         self.popup_menu.tk_popup(event.x_root, event.y_root)
    #     finally:
    #         self.popup_menu.grab_release()
    

    # def modify(self):
    #     print('modify')

    # def post(self):
    #     #shell = get_shell()
    #     #shell.submit_python_code(self.ent.get()+ '\n') 
    #     #shell.focus_set()
    #     editor = get_workbench().get_editor_notebook().get_current_editor()
    #     text = editor.get_text_widget()
        
    #     text.see('insert')
    #     #check selection

    #     if len(text.tag_ranges('sel')):
    #         #replace selection 
    #         text.direct_delete(tk.SEL_FIRST, tk.SEL_LAST)
    #         text.direct_insert("insert", self.post_button['text']) 
    #     else:
    #         #just insert
    #         text.direct_insert("insert", self.post_button['text'])





        #not work  -- text.event_generate("<Double-1>")
        # double click emulation
        #x = 0
        #y = 100
        # print(text.index('insert'))
        # (x, y ,_ , _) = text.bbox('insert')
        # for i in range(2):
        #    text.event_generate('<Button-1>', x=x, y=y)
        #    text.event_generate('<ButtonRelease-1>', x=x, y=y)

        # text.direct_delete(tk.SEL_FIRST, tk.SEL_LAST)
        # text.direct_insert("insert", self.ent2.get())
           
        #print(text.tag_ranges('sel'))
        
        #text.mark_set('insert', 'insert-2chars')        

        #print(text.get('insert-1chars','insert+1chars'))

        #text.tag_remove("sel", "1.0", "end")
        #text.tag_add("sel", "insert wordstart", "insert wordend")
        #for i in text.tag_ranges('sel'):
        #    print(text.index(i))
        #print()
        #ind = text.index('insert')
        #print(ind)
        #print(type(ind))

        #text.direct_delete(tk.SEL_FIRST, tk.SEL_LAST)
        #text.direct_insert("insert wordend", self.ent2.get())


