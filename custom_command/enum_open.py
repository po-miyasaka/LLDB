

import lldb
import os
import shlex
import optparse
import re

def __lldb_init_module(debugger, internal_dict):
    debugger.HandleCommand('command script add -f enum_open.handle_command enum_open')

def handle_command(debugger, command, result, internal_dict):


    # template
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



    command_args = re.split(r'\.', command)
    if len(command_args) > 0:
        enum = frame.EvaluateExpression(command)
    else:
        enum = frame.FindVariable(command)

    if "Swift.Optional" in enum.type.name:
        print("Please forceunwrap target value")
        return False



    variant_name = enum.value
    enum_types = enum.GetChildAtIndex(0).type.name
    att_count = enum.GetChildAtIndex(0).GetNumChildren()

    if att_count == 0:
        print(variant_name)
        return False
    elif att_count == 1:
        tmp = re.sub("\(|\)", "", enum_types)
        types = map(lambda t: remove_label(t), [tmp])
    else:
        tmp = re.sub("\(|\)", "", enum_types)
        types = map(lambda t: remove_label(t)  , re.split(r',', tmp))

    return_params = map(lambda (i, type): format_parameters(i), enumerate(types))
    params =        map(lambda param: add_let(param), return_params)
    parameters = ",".join(params)
    return_parameters = ",".join(return_params)


    exp = """
let h: (() -> Any?) = {{ 
    if case .{0}({1}) = {2} {{
         return ({3})
    }};
return nil
}};

return (h() as! {4})
"""\
        .format(variant_name, parameters,  command, return_parameters, enum_types)
    result = frame.EvaluateExpression(exp, swift_options)
    print(enum.type.name + "." + variant_name + result.type.name)
    print(result.path)


def format_parameters(i):
    r = "v" + str(i)
    return r

def add_let(str):
    r = "let " + str
    return r


def remove_label(str):
    if ':' in str:
        return re.split(r':', str)[1]
    else:
        return str
