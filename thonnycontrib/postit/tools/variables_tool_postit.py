import tkinter as tk
from tkinter import ttk
from collections import Counter

from thonny.codeview import CodeViewText
from thonny.shell import ShellText
from thonny import get_workbench, get_shell

from .tool_postit import ToolWidget, ToolCodeMixin
from ..base_postit import BaseCode, BasePost, BasePopup

from ..common import common_vars_postit
                       



class VariableMenuPostit(ttk.Frame):
    """ composite and mixin approach postit"""
    def __init__(self, master):
        # just combobox. don't need to handle tab and image
        self.last_focus = ''
        
        self.vars_counter = Counter()
        self.vars_counter['變數x'] = 1
        self.vars_counter['變數y'] = 1
        self.vars_counter['名字'] = 1
        self.vars_counter['位置'] = 1

        self.vars_limit = 30
        self.tk_var = tk.StringVar()

        ttk.Frame.__init__(self, master)        
        self.vars_combobox = ttk.Combobox(self, width=12, state="readonly",
                justify=tk.CENTER,textvariable=self.tk_var,takefocus=0,
                values=self.get_most_common())
        self.vars_combobox.pack(side=tk.LEFT, anchor='w')

        self.vars_combobox.current(0)

        self.vars_combobox.bind('<<ComboboxSelected>>', self.on_combo_select)
        self.vars_combobox.bind('<<Selection>>', self.on_select)
        self.vars_combobox.bind('<Button-1>',self.on_combo_click)

    def get_most_common(self):
        most_common_vars = self.vars_counter.most_common(self.vars_limit)
        # skip count, just name list
        return [v for v, _ in most_common_vars]
        
    def on_select(self):
        print('here')

    def on_combo_select(self, event):
        if self.last_focus is not '':
            self.last_focus.focus_set()
            
        self.selection_clear()

    def on_combo_click(self, event):
        print('click')    
        workbench = get_workbench()
        self.last_focus = workbench.focus_get()
        #self.selection_clear()
        






