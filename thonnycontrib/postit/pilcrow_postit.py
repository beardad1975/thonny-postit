import tkinter as tk
from tkinter import ttk

from thonny.codeview import CodeViewText
from thonny.shell import ShellText
from thonny import get_workbench, get_shell

from .base_postit import BaseCode, BasePost, BasePopup
from .tool_postit import ToolWidget, ToolCodeMixin
from .common import common_images


class PilcrowPostMixin:

    def insert_into_editor(self, text_widget, selecting, dragging):
        # get text_widget again for sure
        editor = get_workbench().get_editor_notebook().get_current_editor()
        code_text_widget = editor.get_text_widget()
        #code_text_widget.focus_set()
        y_scroll_pos = code_text_widget.yview()[0]
        x_scroll_pos = code_text_widget.xview()[0]

        #print("y view: ", code_text_widget.yview())
        #print('cursor  :', code_text_widget.cget('cursor'))
        #print('bg: ', self.postit_button.cget('bg'))

        if not self.show_pilcrow_mode:
            #  turning on  show_pilcrow_mode
            s = code_text_widget.get('1.0', 'end-1c')
            s = s.replace('\n', '¶\n')
            s = s.replace(' ', '·')
            code_text_widget.delete('1.0', 'end-1c')
            code_text_widget.insert('1.0', s)
                       
            code_text_widget.config(state=tk.DISABLED)
            code_text_widget.yview_moveto(y_scroll_pos)
            code_text_widget.xview_moveto(x_scroll_pos) 
            self.show_pilcrow_mode = True
            # highlight button
            self.postit_button.config(bg='orange')
            
            code_text_widget.config(cursor="left_side")
            #register event to failsafe back to read-write mode 
            code_text_widget.bind('<Button-1>', self.clickedWhenReadOnlyMode)
            #print("register failsafe event")


        else: # turning off  show_pilcrow_mode
            # unset read-only
            code_text_widget.config(state=tk.NORMAL)
            s = code_text_widget.get('1.0', 'end-1c')
            s = s.replace('¶\n', '\n')
            s = s.replace('·', ' ')
            code_text_widget.delete('1.0', 'end-1c')
            code_text_widget.insert('1.0', s)
            
            code_text_widget.yview_moveto(y_scroll_pos)
            code_text_widget.xview_moveto(x_scroll_pos)
            self.show_pilcrow_mode = False
            #restore button
            self.postit_button.config(bg='SystemButtonFace')
            
            code_text_widget.config(cursor="xterm")
            #unregister failsafe event   
            code_text_widget.unbind('<Button-1>')
            #print("cancel failsafe event")

    def insert_into_shell(self, text_widget, selecting, dragging):
        if not dragging:
            self.insert_into_editor(text_widget, selecting, dragging)

    def clickedWhenReadOnlyMode(self, event):
        self.insert_into_editor(event.widget, selecting=False, dragging=False)


class PilcrowPostit(ToolWidget, 
                 ToolCodeMixin, BaseCode,
                 PilcrowPostMixin, BasePost, 
                 BasePopup):
    """ composite and mixin approach postit"""
    def __init__(self, master):
        self.show_pilcrow_mode = False

        self.widget_init(master, 'pilcrow')
        self.code_init()
        self.post_init()
        #self.popup_init()