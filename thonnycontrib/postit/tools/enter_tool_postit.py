import tkinter as tk
from tkinter import ttk

from thonny.codeview import CodeViewText
from thonny.shell import ShellText
from thonny import get_workbench, get_shell

from .tool_postit import ToolWidget, ToolCodeMixin
from ..base_postit import BaseCode, BasePost, BasePopup


# class EnterToolPostMixin:
#     def insert_into_editor(self, editor_text, 
#                            pressing=False, dragging=False,
#                            selecting=False, hovering=False):
#         if pressing and not selecting:
#             pass
#         elif pressing and selecting:
#             pass
#         elif dragging and not hovering:
#             pass
#         elif dragging and hovering:
#             pass

#     def insert_into_shell(self, shell_text, 
#                            pressing=False, dragging=False,
#                            selecting=False, hovering=False):
#         if pressing and not selecting:
#             pass
#         elif pressing and selecting:
#             pass
#         elif dragging and not hovering:
#             pass
#         elif dragging and hovering:
#             pass


class EnterToolPostMixin:
    def insert_into_editor(self, editor_text, 
                           pressing=False, dragging=False,
                           selecting=False, hovering=False):
        if pressing and not selecting:
            editor_text.event_generate("<Return>")
        
        elif pressing and selecting:
            editor_text.event_generate("<BackSpace>")
            editor_text.event_generate("<Return>")

        elif dragging and not hovering:
            if editor_text.tag_ranges(tk.SEL):
                editor_text.tag_remove(tk.SEL, tk.SEL_FIRST, tk.SEL_LAST)
            editor_text.event_generate("<Return>")

        elif dragging and hovering:
            editor_text.event_generate("<BackSpace>")
            editor_text.event_generate("<Return>")

    def insert_into_shell(self, shell_text, 
                           pressing=False, dragging=False,
                           selecting=False, hovering=False):
        if pressing and not selecting:
            shell_text.event_generate("<Return>")

        elif pressing and selecting:
            shell_text.tag_remove(tk.SEL, tk.SEL_FIRST, tk.SEL_LAST)
            #shell_text.event_generate("<BackSpace>")
            shell_text.event_generate("<Return>")

        elif dragging and not hovering:
            if shell_text.tag_ranges(tk.SEL):
                shell_text.tag_remove(tk.SEL, tk.SEL_FIRST, tk.SEL_LAST)
            shell_text.event_generate("<Return>")

        elif dragging and hovering:
            shell_text.tag_remove(tk.SEL, tk.SEL_FIRST, tk.SEL_LAST)
            #shell_text.event_generate("<BackSpace>")
            shell_text.event_generate("<Return>")

class EnterToolPostit(ToolWidget, 
                 ToolCodeMixin, BaseCode,
                 EnterToolPostMixin, BasePost, 
                 BasePopup):
    """ composite and mixin approach postit"""
    def __init__(self, master):
        self.widget_init(master, 'enter')
        self.code_init()
        self.post_init()
        #self.popup_init()