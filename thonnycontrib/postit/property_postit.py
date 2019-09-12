import tkinter as tk
from tkinter import ttk

from .postit import Postit

from .common import ENTER

class PropertyPostit(Postit):
    def __init__(self, master, object_name, property_list, 
                    property_name, property_value, assign_flag=False,
                    postfix_newline=False):
        super().__init__(master)

        self.code_elements = {}   # code_elements: dict data of code elements
        self.code_elements["object_name"] = object_name #str
        self.code_elements["property_list"] = property_list  # list
        self.code_elements["property_name"] = property_name #str
        self.code_elements["property_value"] = property_value #str
        self.code_elements["assign_flag"] = assign_flag  #boolean
        self.code_elements["postfix_newline"] = postfix_newline #boolean
        
        # self.data_object_name = object_name
        # self.data_property_list = property_list
        # self.data_property_name = property_name
        # self.data_property_value = property_value
        # self.data_assign_flag = assign_flag
        # self.data_postfix_newline = postfix_newline

        #keep default value
        self.default_code_elements = self.code_elements.copy()

        # self.default_object_name = object_name
        # self.default_property_list = property_list
        # self.default_property_name = property_name
        # self.default_property_value = property_value
        # self.default_assign_flag = assign_flag
        # self.default_postfix_newline = postfix_newline

        self.update()


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

    def assemble_code_display(self, code_dict):
        
        if code_dict["assign_flag"]:
            t = f'{code_dict["object_name"]}.{code_dict["property_name"]} = {code_dict["property_value"]} '
        else:
            t = f'{code_dict["object_name"]}.{code_dict["property_name"]} '
        
        if code_dict["postfix_newline"]:
            t += ENTER

        return t

    def assemble_code(self, code_dict):
        if code_dict["assign_flag"]:
            t = f'{code_dict["object_name"]}.{code_dict["property_name"]} = {code_dict["property_value"]} '
        else:
            t = f'{code_dict["object_name"]}.{code_dict["property_name"]} '
        
        if code_dict["postfix_newline"]:
            t += '\n'
        
        return t

    def update(self):   # update both code and code display
        self.set_code_display(self.assemble_code_display(self.code_elements))
        self.set_code(self.assemble_code(self.code_elements))

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
        self.var_property_name.set(self.postit.code_elements["property_name"])
        self.var_property_name.trace('w', lambda *args:self.update_code_preview())

        self.var_property_value = tk.StringVar()
        self.var_property_value.set(self.postit.code_elements['property_value'])
        self.var_property_value.trace('w', lambda *args:self.update_code_preview())

        self.var_assign_flag = tk.BooleanVar()
        self.var_assign_flag.set(self.postit.code_elements["assign_flag"])
        self.var_assign_flag.trace('w', lambda *args: self.update_assign_and_preview())
        
        self.var_postfix_newline = tk.BooleanVar()
        self.var_postfix_newline.set(self.postit.code_elements["postfix_newline"])
        self.var_postfix_newline.trace('w', lambda *args:self.update_code_preview())

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

        t = self.postit.code_elements["object_name"]+'.'
        self.object_name_label = ttk.Label(self.select_frame, text=t)
        self.object_name_label.pack(side='left')

        self.property_name_combo = ttk.Combobox(self.select_frame, width=10, \
                                                textvariable=self.var_property_name,
                                                values=self.postit.code_elements["property_list"])
        #i = self.postit.property_list.index(self.postit.property_name)
        #self.property_name_combo.current(i)
        self.property_name_combo.pack(side='left')
        #self.property_name_combo.bind("<<ComboboxSelected>>", lambda e:self.update_literal())


        self.assign_label = ttk.Label(self.select_frame, text=' = ')
        #self.assign_label.pack(side='left')

        self.property_value_entry = ttk.Entry(self.select_frame, width=15, 
                textvariable=self.var_property_value)
        #self.property_value_entry.pack(side='left')

        #postfix newline frame
        self.newline_frame = ttk.Frame(self)
        self.newline_frame.pack(pady=self.pady, fill='y', anchor='e')

        #ttk.Label(self.newline_frame, text='在最後加上換行(Enter)').pack(side='right', 
        #                                anchor='e')

        self.postfix_newline_checkbutton = ttk.Checkbutton(self.newline_frame, 
                 text= '在最後加上換行(Enter)', variable=self.var_postfix_newline,
                 onvalue=True, offvalue=False)
        self.postfix_newline_checkbutton.pack(side='right',  anchor='e', padx=0, ipadx=0 )

        #code  preview frame
        self.code_preview_frame = ttk.LabelFrame(self, text='程式的寫法')
        self.code_preview_frame.pack(side='top',pady=self.pady, padx=self.padx, fill='both')

        
        self.code_preview_label = ttk.Label(self.code_preview_frame, text='')
        self.code_preview_label.pack(pady=self.pady, padx=self.padx)

        self.update_assign_and_preview() 

        #bottom frame ( buttons )
        self.bottom_frame = ttk.Frame(self)
        self.bottom_frame.pack(side='bottom', pady=self.pady, anchor='e', fill='x')

        ttk.Button(self.bottom_frame, width=12, text="讀取預設值", \
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

    def variable_to_dict(self) -> dict :   # let tkinter variable transform to dict
        dict_ = {}
        #origin data
        dict_["object_name"] = self.postit.code_elements["object_name"] #str
        dict_["property_list"] = self.postit.code_elements["property_list"]  # list

        #tk variables
        dict_["property_name"] = self.var_property_name.get() #str
        dict_["property_value"] = self.var_property_value.get() #str
        dict_["assign_flag"] = self.var_assign_flag.get()  #boolean
        dict_["postfix_newline"] = self.var_postfix_newline.get() #boolean  

        return dict_     


    def update_assign_and_preview(self):
        flag = self.var_assign_flag.get()
        if flag:
            self.assign_label.pack(side='left')
            self.property_value_entry.pack(side='left')
        else:
            self.assign_label.pack_forget()
            self.property_value_entry.pack_forget()

        self.update_code_preview()

    def update_code_preview(self):
        d = self.variable_to_dict()
        t = self.postit.assemble_code_display(d)
        self.code_preview_label.config(text=t)




    # def assemble_code_preview(self):
    #     object_name = self.postit.data_object_name
    #     property_name = self.var_property_name.get()
    #     property_value = self.var_property_value.get()

    #     if self.var_assign_flag.get():            
    #         t = f'{object_name}.{property_name} = {property_value} '
    #     else:
    #         t = f'{object_name}.{property_name} '

    #     if self.var_postfix_newline.get():
    #         t = t + ENTER
        
    #     return t

    def update_postit(self):
        self.postit.code_elements["property_name"] = self.var_property_name.get()
        self.postit.code_elements["assign_flag"] = self.var_assign_flag.get()
        if self.postit.code_elements["assign_flag"]:
            self.postit.code_elements["property_value"] = self.var_property_value.get()
        
        self.postit.code_elements["postfix_newline"] = self.var_postfix_newline.get()

        self.postit.update()

        self.destroy()

    def load_default(self):
        
        self.var_property_name.set(self.postit.default_code_elements["property_name"])
        self.var_property_value.set(self.postit.default_code_elements["property_value"])
        self.var_assign_flag.set(self.postit.default_code_elements["assign_flag"])
        self.var_postfix_newline.set(self.postit.default_code_elements["postfix_newline"])
        self.update_assign_and_preview()

        