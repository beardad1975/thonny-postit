from tkinter import messagebox

from thonny import get_workbench, get_runner

from .postit import PostitWithCombobox
from .common import common_variable_set, VariableNameError

class VariablePostit(PostitWithCombobox):
    def __init__(self, master):
        super().__init__(master)

        self.last_focus = None  # record last focus (editor  or shell)

        self.set_code_display('便貼')
        #get_workbench().bind("get_globals_response", self._handle_get_globals_response, True)
        get_workbench().bind("ToplevelResponse", self._handle_toplevel_response, True)

        self.postit_combo.bind('<<ComboboxSelected>>', self.on_combo_select)
        self.postit_combo.bind('<Button-1>',self.on_combo_click)

    def on_combo_click(self, event):    
        workbench = get_workbench()
        self.last_focus = workbench.focus_get()
        

    def on_combo_select(self, event):
        if self.last_focus is not '':
            self.last_focus.focus_set()
        self.selection_clear()

    def post(self):
        text = self.postit_combo.get()

        #add new variable if needed
        try:
            if text not in common_variable_set:
                common_variable_set.add(text)
                self.postit_combo['values'] = sorted(common_variable_set)
 
            if text is not '':
                self.code = text + ' '
                super().post()
 
        except VariableNameError:
            self.invalid_variable_name_diag(text)

    def invalid_variable_name_diag(self, text):
        content = '你輸入的 ' +text + ' 不是一個合格的變數名稱\n\n'
        content += '【說明】1.變數名稱可以用的字是文字,底線(_)或數字\n'
        content += '　　　　2.變數名稱的開頭第1個字不可以用數字'

        messagebox.showwarning('變數名稱錯誤', content)

    #def _handle_get_globals_response(self, event):
    #    print(event["globals"], event["module_name"])

    def _handle_toplevel_response(self, event):
        if "globals" in event:
            common_variable_set.runtime_update(event['globals'].keys())
            self.update()
        #else:
            # MicroPython
        #    get_runner().send_command(InlineCommand("get_globals", module_name="__main__"))

    def update(self):   # update both code and code display
        self.postit_combo['values'] = sorted(list(common_variable_set))
        