

import lldb
import os
import re
import shlex
import optparse

def __lldb_init_module(debugger, internal_dict):
    debugger.HandleCommand(
    'command script add -f vinfo.handle_command vinfo')

def handle_command(debugger, command, result, internal_dict):
    '''
    Documentation for how to use vinfo goes here 
    '''

    ### Debugger Info ###
    target = debugger.GetSelectedTarget()
    process = target.GetProcess()
    thread = process.GetSelectedThread()
    frame = thread.GetSelectedFrame()

    swift_options = lldb.SBExpressionOptions()
    swift_options.SetLanguage(lldb.eLanguageTypeSwift)

    objc_options = lldb.SBExpressionOptions()
    objc_options.SetLanguage(lldb.eLanguageTypeObjC)
    
    objc_options_o = lldb.SBExpressionOptions()
    objc_options_o.SetLanguage(lldb.eLanguageTypeObjC)
    objc_options_o.SetCoerceResultToId()

    ### Command Parse###
    address = re.match(r"^\(\(.+?\s?\)(.+)\)", command.strip()).groups()[0]
    class_exp = '[{0} class]'.format(address)

    class_name_result = lldb.SBCommandReturnObject()
    debugger.GetCommandInterpreter().HandleCommand("expression -o -l objc++  -- {0} ".format(class_exp), class_name_result)
    if class_name_result.GetError():
        raise AssertionError(class_name_result.GetError())
    elif not class_name_result.HasResult():
        raise AssertionError("")


    class_name = class_name_result.GetOutput().strip()
    class_name_splited = re.split(r'(\.)', class_name)
    print("type lookup " + class_name)
    if len(class_name_splited) == 3: # Swift
        exp_import = 'import {0}'.format(target.executable.basename)
        exp_swift = 'unsafeBitCast({0}, to: {1}.self)'.format(address, class_name)
        frame.EvaluateExpression(exp_import, swift_options)
        res = frame.EvaluateExpression(exp_swift, swift_options)
        print("Use in swift context")
        print(res.path)
    else: # Objective-C
        res = frame.EvaluateExpression("{0}".format(command), objc_options_o)
        print("Use in objc context")
        print(res.path)