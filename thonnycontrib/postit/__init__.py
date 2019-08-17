from thonny import get_workbench, get_shell
import tkinter as tk
import tkinter.font as font
from tkinter import ttk


#postit is  a frame with button and label
class Postit(tk.Frame):
    def __init__(self, *args, **kwargs):
        ttk.Frame.__init__(self, *args, **kwargs)

        bold = font.Font(size=10, weight=font.BOLD)
        #bold = font.Font(size=12)
        self.postit_button = tk.Button(self,  
                                        text='***' , 
                                        command=self.post, 
                                        fg='white', 
                                        bg='#4a6cd4',
                                        justify='left',
                                        font=bold,
                                        )
        self.postit_button.pack(side=tk.LEFT, anchor='w')

        self.help_label = ttk.Label(self, text='' )
        self.help_label.pack(side=tk.LEFT, anchor='w')

        #right click menu
        self.popup_menu = tk.Menu(self, tearoff=0)
        self.popup_menu.add_command(label="修改", command=self.modify)
        self.postit_button.bind("<Button-3>", self.popup)

    def set_content(self, text):
        
        #lines = text.split('\n')
        #max_width = 0
        #for line in lines:
        #    max_width = len(line) if len(line) > max_width else  max_width
        #width = int(max_width*1.2)

        self.postit_button.config(text=text)
        

    def set_help_label(self, help_text):
        self.help_label.config(text=help_text)

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
        
        text.see('insert')
        #check selection

        if len(text.tag_ranges('sel')):
            #replace selection 
            text.direct_delete(tk.SEL_FIRST, tk.SEL_LAST)
            text.direct_insert("insert", self.postit_button['text']) 


        else:
            #just insert
            #text.direct_insert("insert", self.postit_button['text'])
            lines = self.postit_button['text'].split('\n\t')
            for line in lines:
                text.direct_insert("insert",line)
                text.event_generate("<Return>")

            # text.direct_insert("insert",'abc:')
            # text.event_generate("<Return>")
            # text.direct_insert("insert",'def')



class PostitView(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        p = Postit(self)
        p.set_content('物理舞台.新增隨機方塊(\n\tx=7, \n\ty=5, \n\tposition_x=13, \n\tdensity=13,\n\t)')
        p.set_help_label(' ... stage')
        p.pack(side=tk.TOP, anchor='w', padx=5, pady=5)

        p = Postit(self)
        p.set_content('物理舞台.新增隨機方塊(x=7, y=5, position_x=13)')
        p.set_help_label(' ... stage')
        p.pack(side=tk.TOP, anchor='w', padx=5, pady=5)



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
    get_workbench().add_view(PostitView, '程式便利貼', 'ne')