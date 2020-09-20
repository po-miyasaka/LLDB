import lldb
import os
import re
import optparse
import shlex

def __lldb_init_module(debugger, internal_dict):
    debugger.HandleCommand('command script add -f cbd.handle_command cbd')

def handle_command(debugger, command, result, internal_dict):
    command_args = shlex.split(command, posix=False)
    parser = generateOptionParser()

    # template
    target = debugger.GetSelectedTarget()
    process = target.GetProcess()
    thread = process.GetSelectedThread()

    try:
        (options, args) = parser.parse_args(command_args)
    except:
        result.SetError(parser.usage)
        return

    count = thread.GetStopReasonDataCount()
    breaks = ""
    for i in range(0, count, 2):
        main = thread.GetStopReasonDataAtIndex(i)
        sub  = thread.GetStopReasonDataAtIndex(i + 1)
        print("index = {0} breakpoint = {1}.{2}".format(i, main, sub))        
        breaks = breaks + "{0}.{1} ".format(main, sub)

    if breaks.strip():
        res = lldb.SBCommandReturnObject()
        d_or_d = ""
        if options.delete:
            d_or_d = "delete"
        else:
            d_or_d = "disable"
        exp = "break {0} {1}".format(d_or_d, breaks)
        debugger.GetCommandInterpreter().HandleCommand(exp, res)
        print(exp)
        if res.GetError():  
            result.SetError(res.GetError()) 

    if options.conti:
        debugger.SetAsync(True)
        process.Continue()
    return True

def generateOptionParser():
  usage = "usage: %prog [options] breakpoint_query\n" +"Use 'cbd -h' for option desc"
  parser = optparse.OptionParser(usage=usage, prog='b') 
  parser.add_option("-d", "--delete", action="store_true", default=False, dest="delete", help="delete breakpoint")
  parser.add_option("-c", "--continue", action="store_true", default=True, dest="conti", help="continue after excution")
  return parser
