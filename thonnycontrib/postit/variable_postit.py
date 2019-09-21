import tkinter as tk
from tkinter import messagebox

from thonny import get_workbench, get_runner

from .postit import PostitWithCombobox
from .common import common_variable_set, VariableNotValidError, VariableShouldNotKeywordError

class VariablePostit(PostitWithCombobox):
    def __init__(self, master):
        super().__init__(master)

        self.last_focus = None  # record last focus (editor  or shell)

        self.update()
        #get_workbench().bind("get_globals_response", self._handle_get_globals_response, True)
        get_workbench().bind("ToplevelResponse", self._handle_toplevel_response, True)

        self.postit_combo.bind('<<ComboboxSelected>>', self.on_combo_select)
        self.postit_combo.bind('<Button-1>',self.on_combo_click)

        #right click menu
        self.popup_menu = tk.Menu(self, tearoff=0)
        self.popup_menu.add_command(label="貼上",command=self.post)
        self.popup_menu.add_separator()
        self.popup_menu.add_command(label="新增變數到清單(從文字編輯器的選取文字)", command=self.add_selection)
        self.popup_menu.add_separator()
        self.popup_menu.add_command(label="從清單中刪除變數(右邊的選取框)", command=self.remove_combo_item)
        self.popup_menu.add_command(label="刪除清單中的所有變數", command=self.remove_all_combo_item)        

        self.postit_button.bind("<Button-3>", self.popup)


    def remove_all_combo_item(self):
        if messagebox.askyesno('刪除所有變數', '你確定要刪除清單中的所有變數嗎？'):
            common_variable_set.clear_all()
            self.update_combo()
            self.postit_combo.set('')            

    def remove_combo_item(self):

        item = self.postit_combo.get()

        #check empty item
        if not item :
            return

        #check if item in list
        if item not in common_variable_set:
            messagebox.showwarning('變數不在清單中', item + ' 這個變數並不在清單中')
            return

        if messagebox.askyesno('刪除變數', '你確定要從清單中刪除'+item+'嗎？'):
            common_variable_set.remove(item)
            self.update_combo()
            self.postit_combo.set('')
        else:
            return


    def add_selection(self):
        editor = get_workbench().get_editor_notebook().get_current_editor()
        text = editor.get_text_widget()

        #check selection
        if len(text.tag_ranges('sel')):
            selection = text.get(tk.SEL_FIRST, tk.SEL_LAST)
            #check if name valid
            try:
                common_variable_set.add(selection)
                self.update_combo()                
                i = self.postit_combo['values'].index(selection)
                self.postit_combo.current(i)

            except VariableNotValidError:
                self.invalid_variable_name_diag(selection)
            except VariableShouldNotKeywordError:
                self.should_not_keyword_diag(selection)
        else:
            messagebox.showwarning('無選取文字', '文字編輯器裡沒有選取文字')

    def update(self):
        self.set_code_display('變數')

    def on_combo_click(self, event):    
        workbench = get_workbench()
        self.last_focus = workbench.focus_get()
        

    def on_combo_select(self, event):
        if self.last_focus is not '':
            self.last_focus.focus_set()
        self.selection_clear()

    def post(self):
        item = self.postit_combo.get()

        #check empty 
        if not item:
            return

        #add new variable if needed
        try:
            if item not in common_variable_set:
                common_variable_set.add(item)
                self.postit_combo['values'] = sorted(common_variable_set)
 
            if item is not '':
                self.code = item 
                super().post()
 
        except VariableNotValidError:
            self.invalid_variable_name_diag(item)
        except VariableShouldNotKeywordError:
            self.should_not_keyword_diag(item)

    def invalid_variable_name_diag(self, t):
        content = '【 ' + t + ' 】 不是一個合格的變數名稱\n\n'
        content += '【說明】1.變數名稱可以用的字是文字,底線(_)或數字\n'
        content += '　　　　2.變數名稱的開頭第1個字不可以用數字'

        messagebox.showwarning('變數名稱錯誤', content)

    def should_not_keyword_diag(self, t):
        content = '【 ' + t + ' 】 是python的保留關鍵字\n'
        content += '不適合用來作為變數名稱\n'
        content += '請修改或是換一個名稱'

        messagebox.showwarning('變數名稱錯誤', content)

    #def _handle_get_globals_response(self, event):
    #    print(event["globals"], event["module_name"])

    def _handle_toplevel_response(self, event):
        if "globals" in event:
            common_variable_set.runtime_update(event['globals'].keys())
            self.update_combo()
        #else:
            # MicroPython
        #    get_runner().send_command(InlineCommand("get_globals", module_name="__main__"))

    def update_combo(self):   # update both code and code display
        self.postit_combo['values'] = sorted(list(common_variable_set))
        