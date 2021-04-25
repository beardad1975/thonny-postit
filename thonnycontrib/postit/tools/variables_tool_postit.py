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
    def widget_init(self, master, update_after_run=False):
        # just combobox. don't need to handle tab and image
        self.last_focus = ''
        self.vars_counter = None
        self.var_update_after_run = tk.BooleanVar()
        if update_after_run:
            self.var_update_after_run.set(True)
        else:
            self.var_update_after_run.set(False)

        self.vars_limit = 100
        self.tk_var = tk.StringVar()

        ttk.Frame.__init__(self, master)
        style = ttk.Style()
        style.configure("V.TLabel",  background="#fefefe", #background="#ffff55",
                )
        text_font = ('Consolas','11')  

        get_workbench().option_add('*TCombobox*Listbox.font', text_font)

        self.vars_combobox = ttk.Combobox(self, width=10, state="readonly", font=text_font,
                justify=tk.CENTER,textvariable=self.tk_var,takefocus=0,
                values=[],style="V.TLabel")
        self.restore_default_vars()

        self.vars_combobox.pack(side=tk.LEFT, anchor='w')

        #self.vars_combobox.current(0)

        self.vars_combobox.bind('<<ComboboxSelected>>', self.on_combo_select)
        #self.vars_combobox.bind('<<Selection>>', self.on_select)
        self.vars_combobox.bind('<Button-1>',self.on_combo_click)

        get_workbench().bind("ToplevelResponse", self._handle_toplevel_response, True)

    def empty_vars(self):
        self.vars_counter = Counter()
        self.update_vars_menu()

    def restore_default_vars(self):
        #if self.vars_counter:
        #    del self.vars_counter

        if common_default_vars:   
            self.vars_counter = Counter(common_default_vars)
            self.update_vars_menu()
        else:
            self.vars_counter = Counter()
            self.update_vars_menu()

    def update_vars_menu(self):
        if len(self.vars_counter):
            vars_list =[v for v,_ in self.vars_counter.most_common(self.vars_limit)]
            self.vars_combobox.config(values=vars_list)
            self.vars_combobox.current(0)
            #
            #print('here enable')
            common.enable_var_buttons()
        else:
            self.vars_combobox.config(values='')
            self.tk_var.set('')
            #
            common.disable_var_buttons()



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
        if self.var_update_after_run.get():
            if "globals" in event:
                #self.vars_counter.update(event['globals'].keys())
                # only add var the first time
                for key in event['globals'].keys():
                    if key not in self.vars_counter:
                        self.vars_counter[key] = 1
                self.update_vars_menu()

class VariableMenuPopup:
    def popup_init(self):
        self.popup_menu = tk.Menu(self, tearoff=0)

        self.popup_menu.add_command(
            label="刪除目前變數", command=self.delete_current)
        self.popup_menu.add_command(
            label="恢復預設變數", command=self.delete_all_restore_default)
        self.popup_menu.add_command(
            label="清空全部變數", command=self.delete_all)
        self.popup_menu.add_separator()
        self.popup_menu.add_checkbutton(label="【選項】執行後更新變數(全域)",
                onvalue=1, offvalue=0, 
                variable=self.var_update_after_run,
                )

        self.vars_combobox.bind("<Button-3>", self.popup)

    def popup(self, event):
        try:
            self.popup_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.popup_menu.grab_release()

    def delete_current(self):
        var = self.tk_var.get()
        if var:
            del self.vars_counter[var]
            self.update_vars_menu()

    def delete_all_restore_default(self):
        
        ans = messagebox.askyesno('刪除變數','刪除所有變數，並恢復預設值嗎？')
        #print(ans)
        if ans:
            #print('yes ')
            self.restore_default_vars()
        else: # no
            return

    def delete_all(self):
        if len(self.vars_counter):
            ans = messagebox.askyesno('清空全部變數','要清空全部變數嗎？')
            #print(ans)
            if ans:
                #print('yes ')
                self.empty_vars()
                
            else: # no
                return

class VariableMenuPostit(VariableMenuWidget, 
                    VariableMenuPopup
                 ):
    """ composite and mixin approach postit"""
    def __init__(self, master, update_after_run=False):
        self.widget_init(master, update_after_run)
        #self.code_init()
        #self.post_init()
        self.popup_init()


        

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

        #select_text and have .   like obj.attr
        without_dot_text = self.select_text.replace('.','')

        if not without_dot_text.isidentifier():
            content = '【 ' + self.select_text + ' 】 不是一個合格的變數名稱\n\n'
            content += '【說明】1.變數名稱可以用的字是文字,底線(_)或數字\n'
            content += '　　　　2.變數名稱的開頭第1個字不可以用數字'
            messagebox.showwarning('變數名稱錯誤', content)
            return
        # elif iskeyword(self.select_text):
        #     content = '【 ' + self.select_text + ' 】 是python的保留關鍵字\n'
        #     content += '不適合用來作為變數名稱\n'
        #     content += '請修改或是換一個名稱'
        #     messagebox.showwarning('變數名稱錯誤', content)
        #     return
        else: # var name ok
            vars_postit = common.share_vars_postit
            #print(vars_postit)
            vars_postit.vars_counter[self.select_text] += 1 
            vars_postit.update_vars_menu()
            vars_postit.tk_var.set(self.select_text)



class VariableFetchToolPostMixin:
    def on_mouse_drag(self, event):
        state = self.postit_button.cget('state')
        if  state in ('normal', 'active') :
            BasePost.on_mouse_drag(self, event)
        else: # state is disable . do nothing
            pass

    def on_mouse_release(self, event):
        state = self.postit_button.cget('state')
        if state in ('normal', 'active') :
            BasePost.on_mouse_release(self, event)
            #print('here')
        else: # state is disable . do nothing
            #print('else')
            #print(self.postit_button.cget('state'))
            pass

    def create_drag_window(self):
        
        self.drag_window = tk.Toplevel()
        # get var text
        font = self.postit_button.cget('font')

        if self.tool_name == 'variable_get':
            text = '    ' + common.share_vars_postit.tk_var.get() + ' '
        elif self.tool_name == 'variable_assign':
            text = '  ' + common.share_vars_postit.tk_var.get() + ' = '
        elif self.tool_name == 'variable_plus_assign':
            text = '  ' + common.share_vars_postit.tk_var.get() + ' += '
        elif self.tool_name == 'variable_minus_assign':
            text = '  ' + common.share_vars_postit.tk_var.get() + ' -= '
        elif self.tool_name == 'variable_comma':
            text = '  ' + common.share_vars_postit.tk_var.get() + ', '
        elif self.tool_name == 'variable_dot':
            text = '  ' + common.share_vars_postit.tk_var.get() + '.'
        elif self.tool_name == 'variable_parentheses':
            text = '  ' + common.share_vars_postit.tk_var.get() + '() '
        elif self.tool_name == 'variable_square':
            text = '  ' + common.share_vars_postit.tk_var.get() + '[] '
        else:
            text = '  '

        if self.tool_name == 'variable_get':
            color = '#ffff00'
        else:
            color = '#5acef8'

        self.drag_button = tk.Button(self.drag_window, text=text, bg=color, 
                    font=font, fg='black', relief='solid', bd=0 )
        self.drag_button.pack()
        self.drag_window.overrideredirect(True)
        self.drag_window.attributes('-topmost', 'true')

    def content_insert(self, text_widget, content):
        vars_postit = common.share_vars_postit
        var = vars_postit.tk_var.get()
        #var_content = var + ' '
        
        if self.tool_name == 'variable_get':
            var_content = var 
        elif self.tool_name == 'variable_assign':
            var_content = var + ' = '
        elif self.tool_name == 'variable_plus_assign':
            var_content = var + ' += '
        elif self.tool_name == 'variable_minus_assign':
            var_content = var + ' -= '
        elif self.tool_name == 'variable_comma':
            var_content = var + ', '
        elif self.tool_name == 'variable_dot':
            var_content = var + '.'
        elif self.tool_name == 'variable_parentheses':
            var_content = var  + '() '
        elif self.tool_name == 'variable_square':
            var_content = var + '[] '
        else:
            var_content = ''

        text_widget.insert(tk.INSERT, var_content)

        # adjust insert index
        if self.tool_name == 'variable_square':
            text_widget.mark_set(tk.INSERT, 'insert -2c')


        # add counter and  update menu according to most common
        vars_postit.vars_counter[var] += 1
        vars_postit.update_vars_menu()
        vars_postit.tk_var.set(var)


class VariableFetchToolPopup:
    def popup_init(self):
        return

        self.popup_menu = tk.Menu(self, tearoff=0)
        self.popup_menu.add_command(label="V    取出變數",
            command=lambda:self.switch_button('variable_get'))
        self.popup_menu.add_command(label="V =  變數設值",
            command=lambda:self.switch_button('variable_assign'))
        self.popup_menu.add_command(label="V +=  加後設值",
            command=lambda:self.switch_button('variable_plus_assign'))
        self.popup_menu.add_command(label="V -=  減後設值",
            command=lambda:self.switch_button('variable_minus_assign'))
        self.popup_menu.add_command(label="V ,   變數逗號",
            command=lambda:self.switch_button('variable_comma'))
        self.popup_menu.add_command(label="V .   變數句點",
            command=lambda:self.switch_button('variable_dot'))
        self.popup_menu.add_command(label="V ( ) 變數圓括號",
            command=lambda:self.switch_button('variable_parentheses'))
        self.popup_menu.add_command(label="V [ ] 變數方括號",
            command=lambda:self.switch_button('variable_square'))


        self.postit_button.bind("<Button-3>", self.popup)

    def popup(self, event):
        #if self.tool_name != 'variable_get':
        self.popup_menu.tk_popup(event.x_root, event.y_root)
        

    def switch_button(self, tool_name):
        self.tool_name = tool_name
        self.tool_image = common_images[tool_name]
        self.postit_button.config(image=self.tool_image)

        # insert at the same time
        workbench = get_workbench()
        focus_widget = workbench.focus_get()
        if isinstance(focus_widget, CodeViewText):
            # cursor in editor
            editor_text = focus_widget 
            if editor_text.tag_ranges(tk.SEL)  :
                # has selection
                self.insert_into_editor(editor_text, 
                                        pressing=True, selecting=True)
            else:# no selection
                self.insert_into_editor(editor_text, 
                                        pressing=True, selecting=False)
        elif isinstance(focus_widget, ShellText):
            # cusor in shell
            shell_text = focus_widget
            if shell_text.tag_ranges(tk.SEL):
                # has selection
                self.insert_into_shell(shell_text, 
                                        pressing=True, selecting=True)
            else:# no selection
                self.insert_into_shell(shell_text, 
                                        pressing=True, selecting=False) 



class VariableFetchToolPostit(ToolWidget, 
                 ToolCodeMixin, BaseCode,
                 VariableFetchToolPostMixin, BasePost, 
                 VariableFetchToolPopup):
    """  used by 4 tools.
    variable_get, variable_assign, variable_comma, variable_dot"""

    def __init__(self, master, tool_name):
        self.widget_init(master, tool_name)
        self.code_init()
        self.post_init()
        self.popup_init()



# class VariableAssignToolPostMixin:
#     def create_drag_window(self):
#         self.drag_window = tk.Toplevel()
#         # get var text
#         font = self.postit_button.cget('font')
#         text = common.share_vars_postit.tk_var.get() + ' = '
#         self.drag_button = tk.Button(self.drag_window, text=text, bg='#7af85a', 
#                     font=font, fg='black', relief='solid', bd=0 )
#         self.drag_button.pack()
#         self.drag_window.overrideredirect(True)
#         self.drag_window.attributes('-topmost', 'true')

#     def content_insert(self, text_widget, content):
#         vars_postit = common.share_vars_postit
#         var = vars_postit.tk_var.get()
#         var_content = var + ' = '
#         text_widget.insert(tk.INSERT, var_content)

#         # add counter and  update menu according to most common
#         vars_postit.vars_counter[var] += 1
#         vars_postit.update_vars_menu()
#         vars_postit.tk_var.set(var)
#         #print(vars_postit.vars_counter)


# class VariableAssignToolPostit(ToolWidget, 
#                  ToolCodeMixin, BaseCode,
#                  VariableAssignToolPostMixin, BasePost, 
#                  BasePopup):
#     """ composite and mixin approach postit"""
#     def __init__(self, master):
#         self.widget_init(master, 'variable_assign')
#         self.code_init()
#         self.post_init()
#         #self.popup_init()


# class VariableCommaToolPostMixin:
#     def create_drag_window(self):
#         self.drag_window = tk.Toplevel()
#         # get var text
#         font = self.postit_button.cget('font')
#         text = common.share_vars_postit.tk_var.get() + ', '
#         self.drag_button = tk.Button(self.drag_window, text=text, bg='#7af85a', 
#                     font=font, fg='black', relief='solid', bd=0 )
#         self.drag_button.pack()
#         self.drag_window.overrideredirect(True)
#         self.drag_window.attributes('-topmost', 'true')

#     def content_insert(self, text_widget, content):
#         vars_postit = common.share_vars_postit
#         var = vars_postit.tk_var.get()
#         var_content = var + ', '
#         text_widget.insert(tk.INSERT, var_content)

#         # add counter and  update menu according to most common
#         vars_postit.vars_counter[var] += 1
#         vars_postit.update_vars_menu()
#         vars_postit.tk_var.set(var)


# class VariableCommaToolPostit(ToolWidget, 
#                  ToolCodeMixin, BaseCode,
#                  VariableCommaToolPostMixin, BasePost, 
#                  BasePopup):
#     """ composite and mixin approach postit"""
#     def __init__(self, master):
#         self.widget_init(master, 'variable_comma')
#         self.code_init()
#         self.post_init()
#         #self.popup_init()


# class VariableDotToolPostMixin:
#     def create_drag_window(self):
#         self.drag_window = tk.Toplevel()
#         # get var text
#         font = self.postit_button.cget('font')
#         text = common.share_vars_postit.tk_var.get() + '.'
#         self.drag_button = tk.Button(self.drag_window, text=text, bg='#7af85a', 
#                     font=font, fg='black', relief='solid', bd=0 )
#         self.drag_button.pack()
#         self.drag_window.overrideredirect(True)
#         self.drag_window.attributes('-topmost', 'true')

#     def content_insert(self, text_widget, content):
#         vars_postit = common.share_vars_postit
#         var = vars_postit.tk_var.get()
#         var_content = var + '.'
#         text_widget.insert(tk.INSERT, var_content)

#         # add counter and  update menu according to most common
#         vars_postit.vars_counter[var] += 1
#         vars_postit.update_vars_menu()
#         vars_postit.tk_var.set(var)


# class VariableDotToolPostit(ToolWidget, 
#                  ToolCodeMixin, BaseCode,
#                  VariableDotToolPostMixin, BasePost, 
#                  BasePopup):
#     """ composite and mixin approach postit"""
#     def __init__(self, master):
#         self.widget_init(master, 'variable_dot')
#         self.code_init()
#         self.post_init()
#         #self.popup_init()
