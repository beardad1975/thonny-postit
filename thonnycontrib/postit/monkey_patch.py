import tkinter as tk

from thonny import tktextext 
from thonny.ui_utils import EnhancedTextWithLogging
from thonny import get_workbench, get_shell, get_runner
import thonny.codeview
from thonny.codeview import PythonText

# monkey patching
# replace with  selection event custom handler
class CodeViewText(EnhancedTextWithLogging, PythonText):
    """Provides opportunities for monkey-patching by plugins"""

    def __init__(self, master=None, cnf={}, **kw):

        if "replace_tabs" not in kw:
            kw["replace_tabs"] = False

        super().__init__(
            master=master,
            tag_current_line=get_workbench().get_option("view.highlight_current_line"),
            cnf=cnf,
            **kw
        )
        # Allow binding to events of all CodeView texts
        self.bindtags(self.bindtags() + ("CodeViewText",))
        tktextext.fixwordbreaks(tk._default_root)
        
        # monkey patching 
        self.bind('<<Selection>>', self.on_monkey, True)

    def on_monkey(self, event):
        sel = self.get(tk.SEL_FIRST, tk.SEL_LAST)
        print('monkey :', sel, " ,  len :", len(sel))

    def on_secondary_click(self, event=None):
        super().on_secondary_click(event)
        self.mark_set("insert", "@%d,%d" % (event.x, event.y))

        menu = get_workbench().get_menu("edit")
        try:
            from thonny.plugins.debugger import get_current_debugger

            debugger = get_current_debugger()
            if debugger is not None:
                menu = debugger.get_editor_context_menu()
        except ImportError:
            pass

        menu.tk_popup(event.x_root, event.y_root)

thonny.codeview.CodeViewText = CodeViewText
print('  monkey patched :  CodeViewText')