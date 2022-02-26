from http.client import NotConnected
import tkinter as tk
from tkinter import ttk

from thonny.codeview import CodeViewText
from thonny.shell import ShellText
from thonny import get_workbench, get_shell

from ..base_postit import BaseCode, BasePost, BasePopup
from .tool_postit import ToolWidget, ToolCodeMixin, ToolPostMixin
from ..common import common_images


class PilcrowPostMixin:
    

    def insert_into_editor(self, editor_text, 
                            pressing=False, dragging=False,
                            selecting=False, hovering=False):
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

            # backup modified_flag
            self.last_modified_flag = code_text_widget.edit_modified()

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
            # and 6 secs timer, see which come first
            code_text_widget.bind('<Button-1>', self.clickedWhenReadOnlyMode)
            self.last_text_widget = code_text_widget
            # clean modified flag , then update toolbar
            
            #print('last modified flag: ', self.last_modified_flag)

            code_text_widget.edit_modified(False)
            get_workbench()._update_toolbar()

            # set 7 secs timer
            self.timer_id = self.after(7000, self.restorePilcrow)


        elif self.last_text_widget: # turning off  show_pilcrow_mode
            # unset read-only
            self.last_text_widget.config(state=tk.NORMAL)
            s = self.last_text_widget.get('1.0', 'end-1c')
            s = s.replace('¶\n', '\n')
            s = s.replace('·', ' ')
            self.last_text_widget.delete('1.0', 'end-1c')
            self.last_text_widget.insert('1.0', s)
            
            self.last_text_widget.yview_moveto(y_scroll_pos)
            self.last_text_widget.xview_moveto(x_scroll_pos)
            self.show_pilcrow_mode = False
            #restore button
            self.postit_button.config(bg='SystemButtonFace')
            
            self.last_text_widget.config(cursor="xterm")
            #unregister failsafe event   
            self.last_text_widget.unbind('<Button-1>')

            if self.timer_id is not None:
                self.after_cancel(self.timer_id)
                self.timer_id = None
                #print('timer cancelled')

            # restore last modified flag , then update toolbar
            self.last_text_widget.edit_modified(self.last_modified_flag)
            get_workbench()._update_toolbar()    
            
            self.last_text_widget = None

    def insert_into_shell(self, shell_text, 
                            pressing=False, dragging=False,
                            selecting=False, hovering=False):
        if not dragging:
            self.insert_into_editor(shell_text)

    def clickedWhenReadOnlyMode(self, event):
        self.insert_into_editor(event.widget, selecting=False, dragging=False)

    def restorePilcrow(self):
        self.timer_id = None
        #print('restore pilcrow')
        self.insert_into_editor(None, selecting=False, dragging=False)


class PilcrowToolPostit(ToolWidget, 
                 ToolCodeMixin, BaseCode,
                 PilcrowPostMixin, ToolPostMixin,BasePost, 
                 BasePopup):
    """ composite and mixin approach postit"""
    def __init__(self, master):
        self.show_pilcrow_mode = False
        self.timer_id = None
        self.last_modified_flag = None
        self.last_text_widget = None

        self.widget_init(master, 'pilcrow')
        self.code_init()
        self.post_init()
        #self.popup_init()