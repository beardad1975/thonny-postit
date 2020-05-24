import tkinter as tk
import tkinter.font as font
from tkinter import ttk

from thonny.codeview import CodeViewText
from thonny.shell import ShellText
from thonny import get_workbench, get_shell

from .base_postit import BaseWidget,BaseCode, BasePost, BasePopup
from .common import common_postit_tabs,common_images




class DropdownPostit(BaseWidget, 
                      BaseCode,
                      BasePost, 
                     BasePopup):
    """   """
    def __init__(self,  tab_name, code, code_display=None, note=None, 
                    postfix_enter=False, long_note=False):
        self.widget_init(tab_name, long_note)
        self.code_init(code, code_display, note, postfix_enter)
        self.post_init()
        self.popup_init()