import lldb
import os
import re

def __lldb_init_module(debugger, internal_dict):
    debugger.HandleCommand('command script add -f cclet.handle_command cclet')

def handle_command(debugger, command, result, internal_dict):
    
    ### Command Parse ###
    command_args = re.split(r'(\.|\=)', command)
    instance = command_args[0].strip()
    member = command_args[2].strip()
    new_value = command_args[4]
    
    ### Debugger Info ###
    target = debugger.GetSelectedTarget()
    process = target.GetProcess()
    thread = process.GetSelectedThread()
    frame = thread.GetSelectedFrame()
    swift_options = lldb.SBExpressionOptions()
    swift_options.SetLanguage(lldb.eLanguageTypeSwift)
    objc_options = lldb.SBExpressionOptions()
    objc_options.SetLanguage(lldb.eLanguageTypeObjC)
   
    ###  extract instance & member ###
    class_info_expression = '{}'.format(instance)
    class_info = frame.EvaluateExpression(class_info_expression, swift_options)
    member_info = class_info.GetValueForExpressionPath('.{}'.format(member))
    member_string_addr = member_info.GetChildAtIndex(0).load_addr
    
    ### Change String Value ###
    old_value_expression = '*(char**)({0})'.format(member_string_addr)
    old_value = frame.EvaluateExpression(old_value_expression, objc_options)
    change_value_expression = 'poco {0} = {1}'.format(old_value.name, new_value)
    debugger.HandleCommand(change_value_expression)
    
    ### Change Length ###
    new_value_length = len(new_value)
    old_len_expression = '(int*)({0})'.format(( member_info.GetChildAtIndex(1).load_addr))
    old_len = frame.EvaluateExpression(old_len_expression, objc_options)
    change_len_expression = 'poco {0} = *(int*){1}'.format(old_len.name, new_value_length)
    debugger.HandleCommand(change_len_expression)
    
    result.AppendMessage('')
