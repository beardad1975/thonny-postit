import tkinter as tk
from tkinter import ttk

from thonny.codeview import CodeViewText
from thonny.shell import ShellText
from thonny import get_workbench, get_shell

from .base_postit import BaseCode, BasePost, BasePopup
from .common import common_images

class ToolWidget(ttk.Frame):

    def widget_init(self, master, tool_name):
        # don't need to handle tab
        self.tool_name = tool_name
        self.tool_image = common_images[tool_name]

        ttk.Frame.__init__(self, master)        
        self.postit_button = tk.Button(self,  
                                        relief='groove',
                                        borderwidth=0,
                                        
                                        #fg=self.tab.font_color, 
                                        #bg=self.tab.fill_color,
                                        #justify='left', 
                                        #font=f,
                                        compound='right',
                                        image=self.tool_image,
                                        padx=0,
                                        pady=0, 
                                        )
        self.postit_button.pack(side=tk.LEFT, anchor='w')
        

        #self.note_label = ttk.Label(self, text='' )
        #self.note_label.pack(side=tk.LEFT, anchor='w',padx=5)

class ToolCodeMixin:
    def code_init(self):
        # tk var
        self.var_postfix_enter = tk.BooleanVar()
        self.var_postfix_enter.set(False)

        self.code_display = '' 
        self.note = ''
        self.code = ''
            
            #self.update_postit_code()

    def update_postit_code(self):
        pass


class ToolPostMixin:

    def insert_into_editor(self, text_widget, selecting, dragging):
        if self.tool_name == 'backspace':
            # backspace once no matter selecting or not
            text_widget.event_generate("<BackSpace>")
        elif selecting :
            # need extro backspace on the others
            text_widget.event_generate("<BackSpace>")
            if self.tool_name == 'enter':
                text_widget.event_generate("<Return>")
        elif not selecting:
            # not selecting
            if self.tool_name == 'enter':
                text_widget.event_generate("<Return>")
        


    def insert_into_shell(self, text_widget, selecting, dragging):
        if text_widget.compare(tk.INSERT, '>' , 'input_start'): 
            # just bigger than, no equal than
            if self.tool_name == 'backspace':
            # backspace once no matter selecting or not
                text_widget.event_generate("<BackSpace>")
            elif selecting :
                # need extro backspace on the others
                text_widget.event_generate("<BackSpace>")
                if self.tool_name == 'enter':
                    text_widget.event_generate("<Return>")
            elif not selecting:
                # not selecting
                if self.tool_name == 'enter':
                    text_widget.event_generate("<Return>")
        else: # insert befor input_start
            if self.tool_name == 'enter':
                text_widget.event_generate("<Return>")
            elif self.tool_name == 'backspace':
                # do no backspace for safety
                pass

        #shell = get_shell()
        #s = ''
        #if self.tool_name == 'enter':
        #    origin_text = shell.text.get('input_start','end-1c')
        #    s = origin_text + '\n'
        #    shell.submit_python_code(s)
        #elif self.tool_name == 'backspace':
            # do nothing. Backspace already sent by upper level function
        #    pass
            #input_start_index = shell.text.index('input_start')
            #insert_index = shell.text.index('insert')
            #if shell.text.compare(insert_index, '>=' , input_start_index): 
            #    shell.text.delete('insert-1c')
                # insert after input_start
                #before_insert_text = shell.text.get('input_start','insert')
                #after_insert_text = shell.text.get('insert','end-1c')
                #s = before_insert_text[:-1] + after_insert_text
                #shell.submit_python_code(s)      




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