

import lldb
import os
import shlex
import optparse
import re

def __lldb_init_module(debugger, internal_dict):
    debugger.HandleCommand(
    'command script add -f enum_open.handle_command enum_open')

def handle_command(debugger, command, result, internal_dict):
    '''
    Documentation for how to use enum_open goes here 
    '''

    command_args = shlex.split(command, posix=False)
    parser = generateOptionParser()
    try:
        (options, args) = parser.parse_args(command_args)
    except:
        result.SetError(parser.usage)
        return

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
    enum_name = command
    print ("name:")
    print (enum_name)
    enum = frame.EvaluateExpression("{0}".format(enum_name))
    print("baseenum:")
    print(enum)
    variant_name = enum.value
    print("variant_name:")
    print(variant_name)
    enum_info = enum.GetValueForExpressionPath('.' + variant_name)
    print("enuminfo:")
    print(enum_info)
    att_count = enum_info.GetNumChildren()

    print("att_count")
    print(att_count)
    types = []
    if att_count == 0:
        print("no att_value")
        return False
    elif att_count == 1:
        types.append(enum_info.type.name)
        print(types)
    else:
        raw_type = enum_info.type.name
        print(raw_type)
        tmp = re.sub("\(|\)", "", raw_type)
        types = re.split(r',', tmp)
        print(types)
    
    exp = r"""
    let h: (() -> Any?) = {
    if case .{0}({1}) = self.{2} {
        return {3}
        }
        return nil
    }
    (h() as! {4})
    """

    result.AppendMessage('Hello! the enum_open command is working!')


def generateOptionParser():
    usage = "usage: %prog [options] TODO Description Here :]"
    parser = optparse.OptionParser(usage=usage, prog="enum_open")
    parser.add_option("-m", "--module",
                      action="store",
                      default=None,
                      dest="module",
                      help="This is a placeholder option to show you how to use options with strings")
    parser.add_option("-c", "--check_if_true",
                      action="store_true",
                      default=False,
                      dest="store_true",
                      help="This is a placeholder option to show you how to use options with bools")
    return parser
    
