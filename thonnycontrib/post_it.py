from thonny import get_workbench, get_shell
import tkinter as tk
from tkinter import ttk

class PostItView(ttk.Frame):
    def __init__(self, master):
        ttk.Frame.__init__(self, master)
        # self.ent1 = tk.Entry(self)
        # self.ent1.pack()
        # self.ent2 = tk.Entry(self)
        # self.ent2.pack()
        
        
        self.post_button = ttk.Button(self, text='新增隨機方塊()', command=self.post)
        self.post_button.pack(side=tk.TOP,anchor='w')


        #right click menu
        self.popup_menu = tk.Menu(self, tearoff=0)
        self.popup_menu.add_command(label="修改", command=self.modify)
        self.post_button.bind("<Button-3>", self.popup) # Button-2 on Aqua

    def popup(self, event):
        try:
            self.popup_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.popup_menu.grab_release()
    

    def modify(self):
        print('modify')

    def post(self):
        #shell = get_shell()
        #shell.submit_python_code(self.ent.get()+ '\n') 
        #shell.focus_set()
        editor = get_workbench().get_editor_notebook().get_current_editor()
        text = editor.get_text_widget()
        
        #check selection

        if len(text.tag_ranges('sel')):
            #replace selection 
            text.direct_delete(tk.SEL_FIRST, tk.SEL_LAST)
            text.direct_insert("insert", self.post_button['text']) 
        else:
            #just insert
            text.direct_insert("insert", self.post_button['text'])





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
    get_workbench().add_view(PostItView, '程式便利貼', 'ne')