def vinfo(debugger, command, result, internal_dict):
    '''
        Documentation for how to use vinfo goes here
        '''
    command_args = shlex.split(command, posix=False)
    parser = vinfoOptionParser()
    
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


    ### Command Parse###
    address = re.match(r"^\(\(.+?\s?\)(.+)\)", " ".join(args)).groups()[0]
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
    if len(class_name_splited) == 3 or options.is_for_swift: # Swift
        print(class_name)
        import_exp = 'import {0}'.format(target.executable.basename)
        exp_swift = 'unsafeBitCast({0}, to: {1}.self)'.format(address, class_name)
        res = frame.EvaluateExpression("{0};{1}".format(import_exp, exp_swift), swift_options)
        print("Use in swift context")
    else: # Objective-C
        res = frame.EvaluateExpression("{0}".format(command), objc_options_o)
        print("Use in objc context")
    print(res.path)

def vinfoOptionParser():
    usage = "usage: %prog [options] breakpoint_query\n" +"Use 'vinfo -h' for option desc"
    parser = optparse.OptionParser(usage=usage, prog='b')
    parser.add_option("-s", "--for-swift", action="store_true", default=False, dest="is_for_swift", help="cast for swift")
    return parser
