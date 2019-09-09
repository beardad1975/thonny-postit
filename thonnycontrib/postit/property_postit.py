import tkinter as tk
from tkinter import ttk

from .postit import Postit


class PropertyPostit(Postit):
    def __init__(self, master, object_name, property_list, 
                    property_name, property_value, assign_flag):
        super().__init__(master)
        self.data_object_name = object_name
        self.data_property_list = property_list
        self.data_property_name = property_name
        self.data_property_value = property_value
        self.data_assign_flag = assign_flag
        
        #record default value
        self.default_object_name = object_name
        self.default_property_list = property_list
        self.default_property_name = property_name
        self.default_property_value = property_value
        self.default_assign_flag = assign_flag

        self.set_button_content(self.assemble_content())
        ###print(self.assemble_content())

        #right click menu
        self.popup_menu = tk.Menu(self, tearoff=0)
        self.popup_menu.add_command(label="編輯", command=self.on_edit)
        self.postit_button.bind("<Button-3>", self.popup)

        #dnd
        #self.postit_button.bind("<ButtonPress-1>", self.on_dnd_start)
        self.postit_button.bind("<B1-Motion>", self.on_mouse_drag)
        self.postit_button.bind("<ButtonRelease-1>", self.on_mouse_release)
        self.postit_button.configure(cursor="arrow")


    def on_edit(self):
        self.modify_popup = PropertyModifyEdit(self)
        
        #self.popup_win.attributes('-toolwindow', 'true')
        #self.popup_win.deiconify()
        #self.popup_win.grab_set()

    def assemble_content(self):
        if self.data_assign_flag:
            t = f'{self.data_object_name}.{self.data_property_name} = {self.data_property_value} '
        else:
            t = f'{self.data_object_name}.{self.data_property_name} '
        
        #self.postit_button.config(text=t)
        return t
        

class PropertyModifyEdit(tk.Toplevel):
    def __init__(self, postit,  *args, **kwargs):
        tk.Toplevel.__init__(self, *args, **kwargs)
        self.title("修改 -- ")
        self.postit = postit

        self.pady = 10
        self.padx = 20

        #copy data from postit
        # self.var_object_name = tk.StringVar()
        # self.var_object_name.set(self.postit.object_name + '.')

        self.var_property_name = tk.StringVar()
        self.var_property_name.set(self.postit.data_property_name)
        self.var_property_name.trace('w', lambda *args:self.update_literal())

        self.var_property_value = tk.StringVar()
        self.var_property_value.set(self.postit.data_property_value)
        self.var_property_value.trace('w', lambda *args:self.update_literal())

        self.var_assign_flag = tk.BooleanVar()
        self.var_assign_flag.set(self.postit.data_assign_flag)
        self.var_assign_flag.trace('w', lambda *args: self.update_assign_and_literal())
        

        #self.geometry('500x300')
        self.transient()
        self.grab_set()

        #mode frame (assign or get)
        self.mode_frame = ttk.Frame(self)
        self.mode_frame.pack(pady=self.pady)

        ttk.Radiobutton(self.mode_frame, text='設定值', variable=self.var_assign_flag, \
            value=True).pack(side='left')
        ttk.Radiobutton(self.mode_frame, text='取出值', variable=self.var_assign_flag, \
            value=False).pack(side='left')

        #select and input data frame
        self.select_frame = ttk.Frame(self)
        self.select_frame.pack(pady=self.pady)

        self.object_name_label = ttk.Label(self.select_frame, text=self.postit.data_object_name+'.')
        self.object_name_label.pack(side='left')

        self.property_name_combo = ttk.Combobox(self.select_frame, width=10, \
                                                textvariable=self.var_property_name,
                                                values=self.postit.data_property_list)
        #i = self.postit.property_list.index(self.postit.property_name)
        #self.property_name_combo.current(i)
        self.property_name_combo.pack(side='left')
        #self.property_name_combo.bind("<<ComboboxSelected>>", lambda e:self.update_literal())


        self.assign_label = ttk.Label(self.select_frame, text=' = ')
        #self.assign_label.pack(side='left')

        self.property_value_entry = ttk.Entry(self.select_frame, width=15, textvariable=self.var_property_value)
        #self.property_value_entry.pack(side='left')


        #literal frame
        self.literal_frame = ttk.LabelFrame(self, text='程式的寫法')
        self.literal_frame.pack(side='top',pady=self.pady, padx=self.padx, fill='both')

        
        self.literal_label = ttk.Label(self.literal_frame, text='')
        self.literal_label.pack(pady=self.pady, padx=self.padx)

        self.update_assign_and_literal() # also do update_literal

        #bottom frame ( buttons )
        self.bottom_frame = ttk.Frame(self)
        self.bottom_frame.pack(side='bottom', pady=self.pady, anchor='e', fill='x')

        ttk.Button(self.bottom_frame, width=12, text="回復預設值", \
                    command=lambda: self.load_default()).pack(side='left', padx=5)

        ttk.Button(self.bottom_frame, width=10, text="取消", \
                    command=lambda:self.destroy()).pack(side='right', padx=5)

        ttk.Button(self.bottom_frame, width=10, text="修改", 
                command=lambda : self.update_postit(),
                ).pack(side='right', padx=5)


        #ttk.Button(self.bottom_frame, text="預設值", ).pack(side='right')
        
        

        #center popup  on screen
        # popup_width = self.winfo_reqwidth()
        # popup_height = self.winfo_reqheight()
        # position_right = int(self.winfo_screenwidth()/2 - popup_width/2)
        # position_down = int(self.winfo_screenheight()/2 - popup_height/2)
        popup_width = int(self.winfo_screenwidth()/3)
        popup_height = int(self.winfo_screenheight()/3)
        position_right =  int(self.winfo_screenwidth()*0.3)
        position_down = int(self.winfo_screenheight()*0.3) 

        self.geometry(f'{popup_width}x{popup_height}+{position_right}+{position_down}')


    def update_assign_and_literal(self):
        flag = self.var_assign_flag.get()
        if flag:
            self.assign_label.pack(side='left')
            self.property_value_entry.pack(side='left')
        else:
            self.assign_label.pack_forget()
            self.property_value_entry.pack_forget()

        self.update_literal()

    def update_literal(self):
        t = self.assemble_literal_content()
        self.literal_label.config(text=t)

    def assemble_literal_content(self):
        object_name = self.postit.data_object_name
        property_name = self.var_property_name.get()
        property_value = self.var_property_value.get()

        if self.var_assign_flag.get():            
            t = f'{object_name}.{property_name} = {property_value} '
        else:
            t = f'{object_name}.{property_name} '
        
        return t

    def update_postit(self):
        self.postit.data_property_name = self.var_property_name.get()
        self.postit.data_assign_flag = self.var_assign_flag.get()
        if self.postit.data_assign_flag:
            self.postit.data_property_value = self.var_property_value.get()

        self.postit.set_button_content(self.postit.assemble_content())
        self.destroy()

    def load_default(self):
        self.var_property_name.set(self.postit.default_property_name)
        self.var_property_value.set(self.postit.default_property_value)
        self.var_assign_flag.set(self.postit.default_assign_flag)
        self.update_assign_and_literal()

        