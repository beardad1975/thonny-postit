import tkinter as tk
from tkinter import ttk

from thonny.codeview import CodeViewText
from thonny.shell import ShellText
from thonny import get_workbench, get_shell

from .base_postit import BaseCode, BasePost, BasePopup
from .common import common_images

class ToolWidget(ttk.Frame):

    def widget_init(self, master, tool_name):
        self.tool_name = tool_name
        self.tool_image = common_images['enter']

        ttk.Frame.__init__(self, master)        
        self.postit_button = tk.Button(self,  
                                        relief='flat',
                                        borderwidth=0,
                                        
                                        #fg=self.tab.font_color, 
                                        #bg=self.tab.fill_color,
                                        #justify='left', 
                                        #font=f,
                                        compound='right',
                                        image=self.tool_image,
                                        padx=5,
                                        pady=5, 
                                        )
        self.postit_button.pack(side=tk.LEFT, anchor='w')
        

        self.note_label = ttk.Label(self, text='' )
        self.note_label.pack(side=tk.LEFT, anchor='w',padx=5)

class ToolCodeMixin:
    def code_init(self):
        # tk var
        self.var_postfix_enter = tk.BooleanVar()
        self.var_postfix_enter.set(False)

        self.code_display = '' 
        self.note = ''
        if self.tool_name == 'enter':
            self.code = '\n'
            
            #self.update_postit_code()

    def update_postit_code(self):
        pass


class ToolPostMixin:

    def insert_into_editor(self, content):
        editor = get_workbench().get_editor_notebook().get_current_editor()
        text = editor.get_text_widget()
        text.see('insert')

        if self.tool_name == 'enter':
            text.event_generate("<Return>")


    def insert_into_shell(self, content):
        shell = get_shell()
        s = ''
        if self.tool_name == 'enter':
            origin_text = shell.text.get('input_start','end-1c')
            s = origin_text + '\n'

        shell.submit_python_code(s)      




class ToolPostit(ToolWidget, 
                 ToolCodeMixin, BaseCode,
                 ToolPostMixin, BasePost, 
                 BasePopup):
    """ composite and mixin approach postit"""
    def __init__(self, master, tool_name):
        self.widget_init(master, tool_name)
        self.code_init()
        self.post_init()
        #self.popup_init()