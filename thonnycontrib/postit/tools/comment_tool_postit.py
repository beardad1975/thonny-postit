import tkinter as tk
from tkinter import ttk

from thonny.codeview import CodeViewText
from thonny.shell import ShellText
from thonny import get_workbench, get_shell
from thonny.plugins.commenting_indenting import (
    _toggle_selection_comment, _cmd_toggle_selection_comment,
    _cmd_comment_selection, _cmd_uncomment_selection,
) 


from .tool_postit import ToolWidget, ToolCodeMixin
from ..base_postit import BaseCode, BasePost, BasePopup



class CommentToolPostMixin:
    def insert_into_editor(self, editor_text, 
                           pressing=False, dragging=False,
                           selecting=False, hovering=False):

        if pressing:
            _toggle_selection_comment(editor_text)

        elif dragging and not hovering:
            if editor_text.tag_ranges(tk.SEL):
                editor_text.tag_remove(tk.SEL, tk.SEL_FIRST, tk.SEL_LAST)
                _toggle_selection_comment(editor_text)
            else: # while dragging , no selection area
                _toggle_selection_comment(editor_text)


    def insert_into_shell(self, shell_text, 
                           pressing=False, dragging=False,
                           selecting=False, hovering=False):
            pass


class CommentToolPopup:
    def popup_init(self):
        self.popup_menu = tk.Menu(self, tearoff=0)

        self.popup_menu.add_command(
            label="切換註解", 
            command=_cmd_toggle_selection_comment)
        self.popup_menu.add_command(
            label="轉為註解", 
            command=_cmd_comment_selection)
        self.popup_menu.add_command(
            label="取消註解", 
            command= _cmd_uncomment_selection)

        self.postit_button.bind("<Button-3>", self.popup)

    def popup(self, event):
        try:
            self.popup_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.popup_menu.grab_release()

class CommentToolPostit(ToolWidget,     
                 ToolCodeMixin, BaseCode,
                 CommentToolPostMixin, BasePost, 
                 CommentToolPopup):
    """ composite and mixin approach postit"""
    def __init__(self, master):
        self.widget_init(master, 'comment')
        self.code_init()
        self.post_init()
        self.popup_init()

