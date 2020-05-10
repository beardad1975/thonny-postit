import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from collections import Counter
from keyword import iskeyword

import thonny.codeview
from thonny.codeview import CodeViewText
from thonny.shell import ShellText
from thonny import get_workbench, get_shell
from thonny.plugins.notes import NotesText

from .tool_postit import ToolWidget, ToolCodeMixin
from ..base_postit import BaseCode, BasePost, BasePopup

from ..common import  common_default_vars, common_images
from .. import common                       



class VariableMenuWidget(ttk.Frame):
    """ composite and mixin approach postit"""
    def widget_init(self, master):
        # just combobox. don't need to handle tab and image
        self.last_focus = ''
        self.vars_counter = None


        self.vars_limit = 30
        self.tk_var = tk.StringVar()

        ttk.Frame.__init__(self, master)        
        self.vars_combobox = ttk.Combobox(self, width=14, state="readonly",
                justify=tk.CENTER,textvariable=self.tk_var,takefocus=0,
                values=[])
        self.restore_default_vars()

        self.vars_combobox.pack(side=tk.LEFT, anchor='w')

        self.vars_combobox.current(0)

        self.vars_combobox.bind('<<ComboboxSelected>>', self.on_combo_select)
        #self.vars_combobox.bind('<<Selection>>', self.on_select)
        self.vars_combobox.bind('<Button-1>',self.on_combo_click)

        get_workbench().bind("ToplevelResponse", self._handle_toplevel_response, True)



    def restore_default_vars(self):
        if self.vars_counter:
            del self.vars_counter   
        self.vars_counter = Counter(common_default_vars)
        self.update_vars_menu()

    def update_vars_menu(self):
        vars_list =[v for v,_ in self.vars_counter.most_common(self.vars_limit)]
        self.vars_combobox.config(values=vars_list)
        self.vars_combobox.current(0)



    def on_combo_select(self, event):
        if self.last_focus is not '':
            self.last_focus.focus_set()
            
        self.selection_clear()

    def on_combo_click(self, event):
  
        workbench = get_workbench()
        self.last_focus = workbench.focus_get()
        #self.selection_clear()
        
    def _handle_toplevel_response(self, event):
        #print('got toplevel event')
        if "globals" in event:
            #self.vars_counter.update(event['globals'].keys())
            # only add var the first time
            for key in event['globals'].keys():
                if key not in self.vars_counter:
                    self.vars_counter[key] = 1
            self.update_vars_menu()

class VariableMenuPostit(VariableMenuWidget, 
                    BasePopup
                 ):
    """ composite and mixin approach postit"""
    def __init__(self, master):
        self.widget_init(master)

        
        #self.code_init()
        #self.post_init()
        #self.popup_init()


        

class VariableAddToolPostit(ttk.Frame):
    """special postit"""
    def __init__(self, master):
        # don't need to handle tab
        self.tool_name = 'variable_add'
        self.tool_image = common_images[self.tool_name]
        self.select_text = ''

        ttk.Frame.__init__(self, master)        
        self.postit_button = tk.Button(self,  
                                        relief='groove',
                                        borderwidth=0,
                                        compound='right',
                                        image=self.tool_image,
                                        padx=0,
                                        pady=0,
                                        state='disable',
                                        command=self.on_mouse_click
                                        )
        self.postit_button.pack(side=tk.LEFT, anchor='w')
        
        # bind text select on code view , shell and notes 
        self.bind_all('<<Selection>>',self.on_text_select,True)

    def on_text_select(self, event):
        widget = event.widget
        if isinstance(widget,CodeViewText) or isinstance(widget,ShellText)\
                                    or isinstance(widget, NotesText):
                        
            # only select within a line
            self.select_text = widget.get(tk.SEL_FIRST,tk.SEL_LAST)
            if len(self.select_text) and '\n' not in self.select_text:
                #print(self.select_text)
                self.postit_button.config(state='normal')
            else:
                self.select_text = ''
                self.postit_button.config(state='disable')
                

    def on_mouse_click(self):
        #print("clicked")
        if not self.select_text.isidentifier():
            content = '【 ' + self.select_text + ' 】 不是一個合格的變數名稱\n\n'
            content += '【說明】1.變數名稱可以用的字是文字,底線(_)或數字\n'
            content += '　　　　2.變數名稱的開頭第1個字不可以用數字'
            messagebox.showwarning('變數名稱錯誤', content)
            return
        elif iskeyword(self.select_text):
            content = '【 ' + self.select_text + ' 】 是python的保留關鍵字\n'
            content += '不適合用來作為變數名稱\n'
            content += '請修改或是換一個名稱'
            messagebox.showwarning('變數名稱錯誤', content)
            return
        else: # var name ok
            vars_postit = common.share_vars_postit
            #print(vars_postit)
            vars_postit.vars_counter[self.select_text] += 1 
            vars_postit.update_vars_menu()
            vars_postit.tk_var.set(self.select_text)



class VariableGetToolPostMixin:
    def create_drag_window(self):
        self.drag_window = tk.Toplevel()
        # get var text
        font = self.postit_button.cget('font')
        text = common.share_vars_postit.tk_var.get() + ' '
        self.drag_button = tk.Button(self.drag_window, text=text, bg='#7af85a', 
                    font=font, fg='black', relief='solid', bd=0 )
        self.drag_button.pack()
        self.drag_window.overrideredirect(True)
        self.drag_window.attributes('-topmost', 'true')

    def content_insert(self, text_widget, content):
        vars_postit = common.share_vars_postit
        var = vars_postit.tk_var.get()
        var_content = var + ' '
        text_widget.insert(tk.INSERT, var_content)

        # add counter and  update menu according to most common
        vars_postit.vars_counter[var] += 1
        vars_postit.update_vars_menu()
        vars_postit.tk_var.set(var)



class VariableGetToolPostit(ToolWidget, 
                 ToolCodeMixin, BaseCode,
                 VariableGetToolPostMixin, BasePost, 
                 BasePopup):
    """ composite and mixin approach postit"""
    def __init__(self, master):
        self.widget_init(master, 'variable_get')
        self.code_init()
        self.post_init()
        #self.popup_init()



class VariableAssignToolPostMixin:
    def create_drag_window(self):
        self.drag_window = tk.Toplevel()
        # get var text
        font = self.postit_button.cget('font')
        text = common.share_vars_postit.tk_var.get() + ' = '
        self.drag_button = tk.Button(self.drag_window, text=text, bg='#7af85a', 
                    font=font, fg='black', relief='solid', bd=0 )
        self.drag_button.pack()
        self.drag_window.overrideredirect(True)
        self.drag_window.attributes('-topmost', 'true')

    def content_insert(self, text_widget, content):
        vars_postit = common.share_vars_postit
        var = vars_postit.tk_var.get()
        var_content = var + ' = '
        text_widget.insert(tk.INSERT, var_content)

        # add counter and  update menu according to most common
        vars_postit.vars_counter[var] += 1
        vars_postit.update_vars_menu()
        vars_postit.tk_var.set(var)
        #print(vars_postit.vars_counter)


class VariableAssignToolPostit(ToolWidget, 
                 ToolCodeMixin, BaseCode,
                 VariableAssignToolPostMixin, BasePost, 
                 BasePopup):
    """ composite and mixin approach postit"""
    def __init__(self, master):
        self.widget_init(master, 'variable_assign')
        self.code_init()
        self.post_init()
        #self.popup_init()


class VariableCommaToolPostMixin:
    def create_drag_window(self):
        self.drag_window = tk.Toplevel()
        # get var text
        font = self.postit_button.cget('font')
        text = common.share_vars_postit.tk_var.get() + ', '
        self.drag_button = tk.Button(self.drag_window, text=text, bg='#7af85a', 
                    font=font, fg='black', relief='solid', bd=0 )
        self.drag_button.pack()
        self.drag_window.overrideredirect(True)
        self.drag_window.attributes('-topmost', 'true')

    def content_insert(self, text_widget, content):
        vars_postit = common.share_vars_postit
        var = vars_postit.tk_var.get()
        var_content = var + ', '
        text_widget.insert(tk.INSERT, var_content)

        # add counter and  update menu according to most common
        vars_postit.vars_counter[var] += 1
        vars_postit.update_vars_menu()
        vars_postit.tk_var.set(var)


class VariableCommaToolPostit(ToolWidget, 
                 ToolCodeMixin, BaseCode,
                 VariableCommaToolPostMixin, BasePost, 
                 BasePopup):
    """ composite and mixin approach postit"""
    def __init__(self, master):
        self.widget_init(master, 'variable_comma')
        self.code_init()
        self.post_init()
        #self.popup_init()


class VariableDotToolPostMixin:
    def create_drag_window(self):
        self.drag_window = tk.Toplevel()
        # get var text
        font = self.postit_button.cget('font')
        text = common.share_vars_postit.tk_var.get() + '.'
        self.drag_button = tk.Button(self.drag_window, text=text, bg='#7af85a', 
                    font=font, fg='black', relief='solid', bd=0 )
        self.drag_button.pack()
        self.drag_window.overrideredirect(True)
        self.drag_window.attributes('-topmost', 'true')

    def content_insert(self, text_widget, content):
        vars_postit = common.share_vars_postit
        var = vars_postit.tk_var.get()
        var_content = var + '.'
        text_widget.insert(tk.INSERT, var_content)

        # add counter and  update menu according to most common
        vars_postit.vars_counter[var] += 1
        vars_postit.update_vars_menu()
        vars_postit.tk_var.set(var)


class VariableDotToolPostit(ToolWidget, 
                 ToolCodeMixin, BaseCode,
                 VariableDotToolPostMixin, BasePost, 
                 BasePopup):
    """ composite and mixin approach postit"""
    def __init__(self, master):
        self.widget_init(master, 'variable_dot')
        self.code_init()
        self.post_init()
        #self.popup_init()
