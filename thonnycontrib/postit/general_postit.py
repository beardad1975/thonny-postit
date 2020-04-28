import tkinter as tk
from tkinter import ttk

from .postit import Postit


class GeneralPostit(Postit):
    def __init__(self, tab_name, code, code_display=None, note=None):
        super().__init__(tab_name)

        self.code = code
        self.code_display = code_display 
        self.note = note


        self.update()

        #add extra menu command
        
        #self.popup_menu.add_separator()
        #self.popup_menu.add_separator()
        #self.popup_menu.add_command(label="編輯便利貼", command=self.on_edit)

 



    def on_edit(self):
        self.edit_popup = GeneralEditWindow(self)

    def update(self):
        self.set_code(self.code)
        self.set_code_display(self.code_display)
        self.set_note(self.note)




class GeneralEditWindow(tk.Toplevel):
    def __init__(self, postit,  *args, **kwargs):
        tk.Toplevel.__init__(self, *args, **kwargs)

        self.title("編輯便利貼 - 符號 ")
        self.postit = postit

        self.pady = 10
        self.padx = 20

        self.var_symbol_code = tk.StringVar()
        self.var_symbol_code.set(self.postit.symbol.code)
        self.var_symbol_code.trace('w', lambda *args:self.update_code_preview())

        self.transient()
        self.grab_set()

        # tree view select frame
        self.select_frame = ttk.Frame(self)
        self.select_frame.pack(pady=self.pady)

        self.symbol_tree = ttk.Treeview(self.select_frame, selectmode='browse',
                                        height=6, show='headings', columns=('code','note'))
                                        
        self.symbol_tree.heading('code', text='符號')
        self.symbol_tree.heading('note', text='名稱')
        self.symbol_tree.column('code', anchor='center')
        self.symbol_tree.column('note', anchor='center')
        
        for nt in symbol_nt_dict.values():
            self.symbol_tree.insert('','end', nt.code, values=nt.code+' '+nt.note)
            #print(nt.code)

        self.symbol_tree.selection_set(self.var_symbol_code.get())

        self.symbol_tree.bind('<ButtonRelease-1>', self.treeview_click)

        #self.symbol_tree.pack(side='left')

        self.vbar = ttk.Scrollbar(self.select_frame,orient=tk.VERTICAL,command=self.symbol_tree.yview)
        self.symbol_tree.configure(yscrollcommand=self.vbar.set)

        self.symbol_tree.grid(row=0,column=0,sticky=tk.NSEW)
        self.vbar.grid(row=0,column=1,sticky=tk.NS)


        #code  preview frame
        self.code_preview_frame = ttk.LabelFrame(self, text='程式的寫法')
        self.code_preview_frame.pack(side='top',pady=self.pady, padx=self.padx, fill='both')

        
        self.code_preview_label = ttk.Label(self.code_preview_frame, text='')
        self.code_preview_label.pack(pady=self.pady, padx=self.padx)

        self.update_code_preview() 




        #bottom frame ( buttons )
        self.bottom_frame = ttk.Frame(self)
        self.bottom_frame.pack(side='bottom', pady=self.pady, anchor='e', fill='x')

        ttk.Button(self.bottom_frame, width=12, text="讀取預設值", \
                    command=lambda: self.load_default()).pack(side='left', padx=5)

        ttk.Button(self.bottom_frame, width=10, text="取消", \
                    command=lambda:self.destroy()).pack(side='right', padx=5)

        ttk.Button(self.bottom_frame, width=10, text="修改", 
                command=lambda : self.update_postit_and_exit(),
                ).pack(side='right', padx=5)

        #center popup  on screen
        popup_width = int(self.winfo_screenwidth()/3)
        popup_height = int(self.winfo_screenheight()/3)
        position_right =  int(self.winfo_screenwidth()*0.3)
        position_down = int(self.winfo_screenheight()*0.3) 

        self.geometry(f'{popup_width}x{popup_height}+{position_right}+{position_down}')

    def treeview_click(self, e):
        select_id = self.symbol_tree.selection()[0][0]
        if select_id != self.var_symbol_code.get():
            self.var_symbol_code.set(select_id)

    def update_code_preview(self):
        self.code_preview_label.config(text=self.var_symbol_code.get())

    def update_postit_and_exit(self):
        symbol_nt = symbol_nt_dict[self.var_symbol_code.get()]
        self.postit.symbol = symbol_nt
        self.postit.update()
        self.destroy()

    def load_default(self):
        self.var_symbol_code.set(self.postit.default_symbol.code)
        self.update_code_preview()
        self.symbol_tree.selection_set(self.var_symbol_code.get())