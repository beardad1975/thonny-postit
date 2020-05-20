import tkinter as tk
from tkinter import ttk

from thonny.codeview import CodeViewText
from thonny.shell import ShellText
from thonny import get_workbench, get_shell

from .tool_postit import ToolWidget, ToolCodeMixin
from ..base_postit import BaseCode, BasePost, BasePopup

class CopyToolPostMixin:
    def insert_into_editor(self, editor_text, 
                           pressing=False, dragging=False,
                           selecting=False, hovering=False):

            widget = get_workbench().focus_get()
            if widget:
                return widget.event_generate("<<Copy>>")

            return None

    def insert_into_shell(self, shell_text, 
                           pressing=False, dragging=False,
                           selecting=False, hovering=False):

            widget = get_workbench().focus_get()
            if widget:
                return widget.event_generate("<<Copy>>")

            return None            


class CopyToolPostit(ToolWidget,     
                 ToolCodeMixin, BaseCode,
                 CopyToolPostMixin, BasePost, 
                 #CommentToolPopup
                 ):
    """ composite and mixin approach postit"""
    def __init__(self, master):
        self.widget_init(master, 'copy')
        self.code_init()
        self.post_init()
        #self.popup_init()

class CutToolPostMixin:
    def insert_into_editor(self, editor_text, 
                           pressing=False, dragging=False,
                           selecting=False, hovering=False):

            widget = get_workbench().focus_get()
            if widget:
                return widget.event_generate("<<Cut>>")

            return None

    def insert_into_shell(self, shell_text, 
                           pressing=False, dragging=False,
                           selecting=False, hovering=False):

            widget = get_workbench().focus_get()
            if widget:
                return widget.event_generate("<<Cut>>")

            return None            


class CutToolPostit(ToolWidget,     
                 ToolCodeMixin, BaseCode,
                 CutToolPostMixin, BasePost, 
                 #CommentToolPopup
                 ):
    """ composite and mixin approach postit"""
    def __init__(self, master):
        self.widget_init(master, 'cut')
        self.code_init()
        self.post_init()
        #self.popup_init()


class PasteToolPostMixin:
    def insert_into_editor(self, editor_text, 
                           pressing=False, dragging=False,
                           selecting=False, hovering=False):

            widget = get_workbench().focus_get()
            if widget:
                return widget.event_generate("<<Paste>>")

            return None

    def insert_into_shell(self, shell_text, 
                           pressing=False, dragging=False,
                           selecting=False, hovering=False):

            widget = get_workbench().focus_get()
            if widget:
                return widget.event_generate("<<Paste>>")

            return None            


class PasteToolPostit(ToolWidget,     
                 ToolCodeMixin, BaseCode,
                 PasteToolPostMixin, BasePost, 
                 #CommentToolPopup
                 ):
    """ composite and mixin approach postit"""
    def __init__(self, master):
        self.widget_init(master, 'paste')
        self.code_init()
        self.post_init()
        #self.popup_init()
