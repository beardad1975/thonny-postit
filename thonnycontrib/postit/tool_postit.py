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
            text_widget.event_generate("<BackSpace>")
        elif self.tool_name == 'undo':
            text_widget.edit_undo()
        elif self.tool_name == 'redo':
            text_widget.edit_redo()
        elif self.tool_name == 'enter':
            if selecting :
                text_widget.event_generate("<BackSpace>")
                text_widget.event_generate("<Return>")
            else : # not selecting
                text_widget.event_generate("<Return>")
        elif self.tool_name == 'indent':
            text_widget.indent_region()
            #else: # not selecting
                # to first word of line
                #text_widget.mark_set(tk.INSERT, tk.INSERT +' lineend')
                #text_widget.event_generate("<Home>")
                # do indent . keep cursor front
                #text_widget.event_generate("<Tab>")
            #    text_widget.indent_region()
        elif self.tool_name == 'dedent':
            text_widget.dedent_region()
            # if selecting:
            #     text_widget.dedent_region()
            # else: # not selecting    
            #     origin_index = text_widget.index(tk.INSERT)
            #     # do unindent
            #     text_widget.event_generate("<Shift-Tab>")
            #     # keep cursor front
            #     text_widget.mark_set(tk.INSERT, origin_index +' lineend')
            #     text_widget.event_generate("<Home>")

    def insert_into_shell(self, text_widget, selecting, dragging):
        if text_widget.compare(tk.INSERT, '>=' , 'input_start'): 
            if self.tool_name == 'backspace' and text_widget.compare(tk.INSERT, '>' , 'input_start'):
                # just bigger than, no equal than because of backspace del left char
                text_widget.event_generate("<BackSpace>")
            elif self.tool_name == 'undo':
                text_widget.event_generate('<Up>')
            elif self.tool_name == 'redo':
                text_widget.event_generate('<Down>')
            elif self.tool_name == 'enter':
                if selecting:
                    text_widget.event_generate("<BackSpace>")
                    text_widget.event_generate("<Return>")
                else:# not selecting
                    text_widget.event_generate("<Return>")
            elif self.tool_name == 'indent':
                pass # when in shell
            elif self.tool_name == 'dedent':
                pass # when in shell

        else: # insert befor input_start
            if self.tool_name == 'enter':
                text_widget.event_generate("<Return>")
            elif self.tool_name == 'backspace':
                # do no backspace for safety
                pass
            elif self.tool_name == 'undo':
                text_widget.event_generate('<Up>')
            elif self.tool_name == 'redo':
                text_widget.event_generate('<Down>')

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