import tkinter as tk

from tkinter import ttk

from thonny import get_workbench, get_shell
from thonny.codeview import CodeViewText
from thonny.ui_utils import VerticallyScrollableFrame

from .property_postit import  PropertyPostit
from .symbol_postit import SymbolPostit
from .variable_postit import VariablePostit
from .if_postit import IfPostit
### unicode return symbol \u23ce


class Pie4tView(VerticallyScrollableFrame):
    def __init__(self, master):
        super().__init__(master)

        pp = PropertyPostit(self.interior, 
                            object_name='物理舞台',
                            property_list=('重力x','重力y', '預設彈性'),
                            property_name='重力x',
                            property_value='20',
                            assign_flag=True,
                            #postfix_newline=False,
                            )
        pp.pack(side=tk.TOP, anchor='w', padx=5, pady=5)


class NameSymbolView(VerticallyScrollableFrame):
    def __init__(self, master):
        super().__init__(master)

        sp  = SymbolPostit(self.interior, '+')   
        sp.grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)

        sp  = SymbolPostit(self.interior, '-')   
        sp.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)

        sp  = SymbolPostit(self.interior, '*')   
        sp.grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)

        sp  = SymbolPostit(self.interior, '/')   
        sp.grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)

        sp  = SymbolPostit(self.interior, ',')   
        sp.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)

        sp  = SymbolPostit(self.interior, '=')   
        sp.grid(row=1, column=2, sticky=tk.W, padx=5, pady=5)

        vp = VariablePostit(self.interior)
        vp.grid(row=2, columnspan=3, sticky=tk.W,  padx=5, pady=5)


class PythonView(VerticallyScrollableFrame):
    def __init__(self, master):
        super().__init__(master)

        # p = Postit(self)
        # p.set_content('物理舞台.新增隨機方塊(\n\t位置x=7, \n\t位置y=5, \n\t密度=13,\n)')
        # p.set_help_label(' ... stage')
        # p.pack(side=tk.TOP, anchor='w', padx=5, pady=5)

        ip = IfPostit(self.interior)
        ip.pack(side=tk.TOP, anchor='w', padx=5, pady=5)








    #     tk.Frame.__init__(self, master)
    #     # self.ent1 = tk.Entry(self)
    #     # self.ent1.pack()
    #     # self.ent2 = tk.Entry(self)
    #     # self.ent2.pack()
        
        
    #     self.post_button = tk.Button(self, text='新增隨機方塊(x, y)12345', command=self.post)
    #     #self.post_button.pack(anchor='w')
    #     self.post_button.pack(anchor='w',padx=5, pady=5)

    #     #right click menu
    #     self.popup_menu = tk.Menu(self, tearoff=0)
    #     self.popup_menu.add_command(label="修改", command=self.modify)
    #     self.post_button.bind("<Button-3>", self.popup) # Button-2 on Aqua

    # def popup(self, event):
    #     try:
    #         self.popup_menu.tk_popup(event.x_root, event.y_root)
    #     finally:
    #         self.popup_menu.grab_release()
    

    # def modify(self):
    #     print('modify')

    # def post(self):
    #     #shell = get_shell()
    #     #shell.submit_python_code(self.ent.get()+ '\n') 
    #     #shell.focus_set()
    #     editor = get_workbench().get_editor_notebook().get_current_editor()
    #     text = editor.get_text_widget()
        
    #     text.see('insert')
    #     #check selection

    #     if len(text.tag_ranges('sel')):
    #         #replace selection 
    #         text.direct_delete(tk.SEL_FIRST, tk.SEL_LAST)
    #         text.direct_insert("insert", self.post_button['text']) 
    #     else:
    #         #just insert
    #         text.direct_insert("insert", self.post_button['text'])





        #not work  -- text.event_generate("<Double-1>")
        # double click emulation
        #x = 0
        #y = 100
        # print(text.index('insert'))
        # (x, y ,_ , _) = text.bbox('insert')
        # for i in range(2):
        #    text.event_generate('<Button-1>', x=x, y=y)
        #    text.event_generate('<ButtonRelease-1>', x=x, y=y)

        # text.direct_delete(tk.SEL_FIRST, tk.SEL_LAST)
        # text.direct_insert("insert", self.ent2.get())
           
        #print(text.tag_ranges('sel'))
        
        #text.mark_set('insert', 'insert-2chars')        

        #print(text.get('insert-1chars','insert+1chars'))

        #text.tag_remove("sel", "1.0", "end")
        #text.tag_add("sel", "insert wordstart", "insert wordend")
        #for i in text.tag_ranges('sel'):
        #    print(text.index(i))
        #print()
        #ind = text.index('insert')
        #print(ind)
        #print(type(ind))

        #text.direct_delete(tk.SEL_FIRST, tk.SEL_LAST)
        #text.direct_insert("insert wordend", self.ent2.get())

def load_plugin():
    get_workbench().add_view(PythonView, '便貼python', 'se')
    get_workbench().add_view(NameSymbolView, '便貼名稱符號', 'ne')
    get_workbench().add_view(Pie4tView, '便貼pie4t', 'se')
