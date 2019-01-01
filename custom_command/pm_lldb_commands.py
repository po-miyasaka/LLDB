import lldb
import os
import re
import shlex
import optparse

def __lldb_init_module(debugger, internal_dict):
    debugger.HandleCommand('command script add -f pm_lldb_commands.cclet cclet')
    debugger.HandleCommand('command script add -f pm_lldb_commands.vinfo vinfo')
    debugger.HandleCommand('command script add -f pm_lldb_commands.enum_open enum_open')
    debugger.HandleCommand('command script add -f pm_lldb_commands.cbd cbd')
    debugger.HandleCommand('command script add -f pm_lldb_commands.preturn preturn')

def cclet(debugger, command, result, internal_dict):
    
    ### Command Parse ###
    command_args = re.split(r'(\.|\=\s*)', command)
    instance = command_args[0].strip()
    member = command_args[2].strip()
    new_value = command_args[4].strip()
    new_value_length = len(new_value) -2
    
    print (new_value)
    print (new_value_length)
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
   
    ###  extract instance & member ###
    class_info_expression = '{}'.format(instance)
    class_info = frame.EvaluateExpression(class_info_expression, swift_options)
    member_info = class_info.GetValueForExpressionPath('.{}'.format(member))
    member_string_addr = member_info.GetChildAtIndex(0).load_addr
    
    ### Change String Value ###
    old_value_expression = '*(char**)({0})'.format(member_string_addr)
    change_value_expression = "{0} = {1}".format(old_value_expression, new_value)
    frame.EvaluateExpression(change_value_expression, objc_options_o)
    
    ### Change Length ###
    
    old_len_expression = '*(int*)({0})'.format(( member_info.GetChildAtIndex(0).GetChildAtIndex(1).location))
    
    change_len_expression = 'exp -l objc -o -- {0} = (int){1}'.format(old_len_expression, new_value_length)
    debugger.HandleCommand(change_len_expression)
    
    result.AppendMessage('')



def vinfo(debugger, command, result, internal_dict):
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
    res = ""
    if len(class_name_splited) == 3: # Swift
        import_exp = 'import {0}'.format(target.executable.basename)
        exp_swift = 'unsafeBitCast({0}, to: {1}.self)'.format(address, class_name)
        res = frame.EvaluateExpression("{0};{1}".format(import_exp, exp_swift), swift_options)
        print("Use in swift context")
    else: # Objective-C
        res = frame.EvaluateExpression("{0}".format(command), objc_options_o)
        print("Use in objc context")
    print(res.path)



def enum_open(debugger, command, result, internal_dict):
    
    
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
        print(enum.path)
    
        res = lldb.SBCommandReturnObject()
        debugger.GetCommandInterpreter().HandleCommand("expression -l swift -o -- {0}".format(enum.path), res)
        print(res.GetOutput())
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
        print(enum.type.name + "." + variant_name)
    print(result.type.name)
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





def cbd(debugger, command, result, internal_dict):
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
  parser.add_option("-c", "--continue", action="store_true", default=False, dest="conti", help="continue after excution")
  return parser


def generateOptionParser():
    usage = "usage: %prog [options] breakpoint_query\n" +"Use 'cbd -h' for option desc"
    parser = optparse.OptionParser(usage=usage, prog='b')
    parser.add_option("-d", "--delete", action="store_true", default=False, dest="delete", help="delete breakpoint")
    parser.add_option("-c", "--continue", action="store_true", default=False, dest="conti", help="continue after excution")
    return parser


def preturn(debugger, command, result, internal_dict):
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
