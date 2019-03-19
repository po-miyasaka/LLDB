import lldb
import re
import shlex
import optparse

def vinfo(debugger, inputs, result, internal_dict):
    inputs_splited = shlex.split(inputs, posix=False)
    parser = vinfoOptionParser()

    try:
        (options, raw_targets) = parser.parse_args(inputs_splited)
    except:
        result.SetError(parser.usage)
        return

    addresses = address_parse(raw_targets)
    vinfo_maker = VariableInfoMaker(debugger, options, addresses[0])
    vinfo_maker.output_result()

def address_parse(raw_targets):
    raw_targets_joined = " ".join(raw_targets)
    matched = re.match(r"^\(\(.+?\s?\)(.+)\)", raw_targets_joined)
    if matched:
        addresses = [matched.groups()[0]]
    else:
        addresses = raw_targets
    return addresses


class VariableInfoMaker:
    def __init__(self, debugger, options_inputed, address):
        ### Debugger Info ###
        self.swift_options = lldb.SBExpressionOptions()
        self.swift_options.SetLanguage(lldb.eLanguageTypeSwift)

        self.objc_options = lldb.SBExpressionOptions()
        self.objc_options.SetLanguage(lldb.eLanguageTypeObjC)

        self.debugger = debugger
        self.target = debugger.GetSelectedTarget()
        self.process = self.target.GetProcess()
        self.thread = self.process.GetSelectedThread()
        self.frame = self.thread.GetSelectedFrame()
        self.address = address
        self.options_inputed = options_inputed
        

    def main_module_name(self):
        module_name = self.target.executable.basename.replace('-', '_')
        return module_name

    def target_module_name(self):
        class_name_splited = self.class_name_swift().strip().split(".")[0]
        target_module_name = class_name_splited.replace('-', '_')
        return target_module_name

    def import_module(self):
        target_module_name = self.target_module_name() 
        import_exp = 'import {0}; import UIKit;'.format(self.main_module_name())
        if target_module_name:
            import_exp = import_exp + 'import {0}'.format(target_module_name)
        self.frame.EvaluateExpression("{0};".format(import_exp), self.swift_options)

    def generate_variable_swift(self):
        exp_swift = 'unsafeBitCast({0}, to: {1}.self)'.format(self.address, self.class_name_swift().strip())
        variable_swift = self.frame.EvaluateExpression("{0}".format(exp_swift), self.swift_options)
        if variable_swift.path:
            return variable_swift
        return False

    def generate_variable_objc(self):
        exp_objc = "(({0}) {1})".format(self.class_name_objc(), self.address)
        variable_objc = self.frame.EvaluateExpression(exp_objc, self.objc_options)
        return variable_objc


    def class_name_objc(self):
        exp = "pc (id){0} ".format(self.address)
        raw_result = self.expressionHandle(exp)
        class_name = re.match(r"^\((.+)?\).*", raw_result).groups()[0]
        return class_name

    def class_name_swift(self):
        exp = "expression -o -l objc++  -- [{0} class];".format(self.address)
        raw_result = self.expressionHandle(exp)
        if not re.match(r"(^_)?", raw_result).groups()[0]:
            return raw_result
        else:
            demangled = self.get_demangled_name(raw_result)
            return demangled

    def get_demangled_name(self, mangled_name):
        #FIXME to correct algorithm
        exp = "poc {0} ".format(self.address)
        object_class_name = self.expressionHandle(exp)
        result = re.sub(r'(\(.*?\).)', '', object_class_name)
        return result

    def output_result(self):
        self.import_module()
        if not self.options_inputed.is_for_objc:
            variable_swift = self.generate_variable_swift()
            if variable_swift:
                print("For Swift")
                print("type lookup " + self.class_name_swift().strip())
                print(variable_swift.path)
                return

        variable_objc = self.generate_variable_objc()  
        print("For Objc")
        print("type lookup " + self.class_name_objc().split(" ")[0])
        print(variable_objc.path)
        return
        

    def expressionHandle(self, exp):
        returnObject = lldb.SBCommandReturnObject()
        self.debugger.GetCommandInterpreter().HandleCommand(exp, returnObject)
        if returnObject.GetError():
            raise AssertionError(returnObject.GetError())
        elif not returnObject.HasResult():
            raise AssertionError("")

        result = returnObject.GetOutput()
        return result
        

def vinfoOptionParser():
    usage = "usage: %prog [options] breakpoint_query\n" + "Use 'vinfo -h' for option desc"
    parser = optparse.OptionParser(usage=usage, prog='b')
    parser.add_option("-c", "--for-objc", action="store_true", default=False, dest="is_for_objc", help="cast for objc")
    return parser

def __lldb_init_module(debugger, internal_dict):
    debugger.HandleCommand('command script add -f vinfo.vinfo vinfo')

    debugger.HandleCommand("command regex pc  's/(.*)?-op?(.*)/ exp -l objc++ %2 -- %1/'\
                                              's/(.*)/ exp -l objc     -- %1/'")
    debugger.HandleCommand("command regex poc 's/(.*)?-op?(.*)/ exp -l objc++ -O %2 -- %1/'\
                                              's/(.*)/ exp -l objc  -O -- %1/'")
    debugger.HandleCommand("command regex ps  's/(.*)?-op?(.*)/ exp -l swift     %2 -- %1/'\
                                              's/(.*)/ exp -l swift    -- %1/'")
    debugger.HandleCommand("command regex pos 's/(.*)?-op?(.*)/ exp -l swift -O  %2 -- %1/'\
                                              's/(.*)/ exp -l swift -O -- %1/'")