import tkinter as tk

from .postit import Postit
from .common import if_statement


class IfPostit(Postit):
    def __init__(self, tab_name):
        super().__init__(tab_name)

        self.update()



        #right click menu
        self.popup_menu = tk.Menu(self, tearoff=0, postcommand=self.update_menu)
        #   entry 0
        self.popup_menu.add_command(label="預設：貼上",command=self.post)
        #   entry 1
        self.popup_menu.add_separator()
        #   entry 2
        self.popup_menu.add_command(label="增加elif區塊",command=self.add_elif)
        #   entry 3
        self.popup_menu.add_command(label="減少elif區塊",command=self.subtract_elif)
        #   entry 4
        self.popup_menu.add_separator()
        #   entry 5
        self.var_else_flag = tk.BooleanVar()
        self.var_else_flag.set(False)
        self.popup_menu.add_checkbutton(label="else區塊",onvalue=True, offvalue=False,\
                                        variable=self.var_else_flag, command=self.toggle_else)
        
        self.postit_button.bind("<Button-3>", self.popup)

    def add_elif(self):
        if_statement.add_elif()
        self.update()
    
    def subtract_elif(self):
        if_statement.subtract_elif()
        self.update()


    def update_menu(self):
        if if_statement.elif_num > 0:
            self.popup_menu.entryconfig(3, label="減少elif區塊",state=tk.NORMAL)
        else:
            self.popup_menu.entryconfig(3, label="減少elif區塊",state=tk.DISABLED) 
        
        # handle else check status
        self.var_else_flag.set(if_statement.else_flag)


    def toggle_else(self):
        if_statement.else_flag = not if_statement.else_flag
        self.update()



    def update(self):   # update both code and code display
        text = repr(if_statement)
        
        tmp = text
        if tmp[-1] == '\n':
            #remove \n in the end of text
            tmp = tmp[:-1]
        display_text = tmp.replace('\n', '\n    ')

        #handle space before elif else
        display_text = display_text.replace('    elif','elif')
        display_text = display_text.replace('    else','else')
        

        self.set_code(text)
        self.set_code_display(display_text)
        self.set_note('如果')
        