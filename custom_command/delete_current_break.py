import lldb
import os
import re

def __lldb_init_module(debugger, internal_dict):
    debugger.HandleCommand('command script add -f delete_current_break.handle_command delete_current_break')

def handle_command(debugger, command, result, internal_dict):
    debugger.SetAsync(False)
    # template
    target = debugger.GetSelectedTarget()
    process = target.GetProcess()
    thread = process.GetSelectedThread()

    count = thread.GetStopReasonDataCount()
    breaks = ""
    for i in range(0, count, 2):
        main = thread.GetStopReasonDataAtIndex(i)
        sub  = thread.GetStopReasonDataAtIndex(i + 1)
        print("index = {0} breakpoint = {1}.{2}".format(i, main, sub))        
        breaks = breaks + "{0}.{1} ".format(main, sub)

    res = lldb.SBCommandReturnObject()
    debugger.GetCommandInterpreter().HandleCommand("break delete {0}".format(breaks), res)


    if res.GetError():  
        result.SetError(res.GetError()) 

    result.AppendMessage("{}".format(res.GetOutput()))
    debugger.SetAsync(True)
    return True