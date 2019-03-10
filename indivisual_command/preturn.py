

import lldb
import os
import shlex
import optparse

def __lldb_init_module(debugger, internal_dict):
    debugger.HandleCommand(
    'command script add -f preturn.handle_command preturn')

def handle_command(debugger, command, result, internal_dict):
    target = debugger.GetSelectedTarget()
    thread = target.GetProcess().GetThreadAtIndex(0)
    process = target.GetProcess()
    debugger.SetAsync(False)
    thread.StepOut()
    expression = 'expression -lobjc -O -- {0} = {1};'.format(getRegisterString(target), command)
    debugger.HandleCommand(expression)
    debugger.SetAsync(True)
    process.Continue()
    return False

    
def getRegisterString(target):
    triple_name = target.GetTriple()
    if "x86_64" in triple_name:
        return "$rax"
    elif "i386" in triple_name:
        return "$eax"
    elif "arm64" in triple_name:
        return "$x0"
    elif "arm" in triple_name:
        return "$r0"
    raise Exception('Unknown hardware. Womp womp')
