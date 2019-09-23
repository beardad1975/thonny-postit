import tkinter as tk

from .postit import Postit
from .common import while_statement

class WhilePostit(Postit):
    def __init__(self, master):
        super().__init__(master)

        self.update()



        #right click menu
        self.popup_menu = tk.Menu(self, tearoff=0, postcommand=self.update_menu)
        #   entry 0
        self.popup_menu.add_command(label="預設：貼上",command=self.post)
        #   entry 1
        self.popup_menu.add_separator()
        #   entry 2
        self.var_break_flag = tk.BooleanVar()
        self.var_break_flag.set(False)
        self.popup_menu.add_checkbutton(label="使用break",onvalue=True, offvalue=False,\
                                        variable=self.var_break_flag, command=self.toggle_break)
        
        self.postit_button.bind("<Button-3>", self.popup)


    def update_menu(self):
 
        # handle else check status
        self.var_break_flag.set(while_statement.break_flag)


    def toggle_break(self):
        while_statement.break_flag = not while_statement.break_flag
        self.update()



    def update(self):   # update both code and code display
        text = repr(while_statement)
        
        tmp = text
        if tmp[-1] == '\n':
            #remove \n in the end of text
            tmp = tmp[:-1]
        display_text = tmp.replace('\n', '\n    ')

        #handle space before elif else
        #display_text = display_text.replace('    elif','elif')
        #display_text = display_text.replace('    else','else')
        

        self.set_code(text)
        self.set_code_display(display_text)
        self.set_note('while迴圈')
        