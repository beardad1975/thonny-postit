from thonny import get_workbench

from .postit import Postit

class VariablePostit(Postit):
    def __init__(self, master):
        super().__init__(master)

        self.set_code_display('test')
        #get_workbench().bind("get_globals_response", self._handle_get_globals_response, True)
        get_workbench().bind("ToplevelResponse", self._handle_toplevel_response, True)

    def post(self):
        print('haha...')

    #def _handle_get_globals_response(self, event):
    #    print(event["globals"], event["module_name"])

    def _handle_toplevel_response(self, event):
        if "globals" in event:
            print(event['globals'], "__main__")
        else:
            # MicroPython
            get_runner().send_command(InlineCommand("get_globals", module_name="__main__"))