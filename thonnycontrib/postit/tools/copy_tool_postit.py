import tkinter as tk
from tkinter import ttk

from thonny.codeview import CodeViewText
from thonny.shell import ShellText
from thonny import get_workbench, get_shell

from .tool_postit import ToolWidget, ToolCodeMixin
from ..base_postit import BaseCode, BasePost, BasePopup

class CopyToolPostMixin:
    def post_init(self):
        self.drag_window = None
        self.drag_button = None
        self.drag_hover_selection = False
        self.hover_text_backup = ''
        #self.mouse_dragging = False
        # drag and press event
        #self.postit_button.bind("<B1-Motion>", self.on_mouse_drag)
        self.postit_button.bind("<Button-1>", self.on_mouse_release)
        #self.postit_button.config(cursor='arrow')

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
    def post_init(self):
        self.drag_window = None
        self.drag_button = None
        self.drag_hover_selection = False
        self.hover_text_backup = ''
        #self.mouse_dragging = False
        # drag and press event
        #self.postit_button.bind("<B1-Motion>", self.on_mouse_drag)
        self.postit_button.bind("<Button-1>", self.on_mouse_release)
        #self.postit_button.config(cursor='arrow')

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
    def post_init(self):
        self.drag_window = None
        self.drag_button = None
        self.drag_hover_selection = False
        self.hover_text_backup = ''
        #self.mouse_dragging = False
        # drag and press event
        #self.postit_button.bind("<B1-Motion>", self.on_mouse_drag)
        self.postit_button.bind("<Button-1>", self.on_mouse_release)
        #self.postit_button.config(cursor='arrow')

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
