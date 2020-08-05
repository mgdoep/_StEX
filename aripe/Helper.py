# coding: utf8

"""
Helper contains a number of small routines needed in various classes.

"""


from platform import system
import numpy as np
import os
from re import compile, match
import serial.tools.list_ports as lipo

ArduinoIsRunning = True
ArdunioCurrentValues = ""

class Helper:
    def __init__(self):
        self.ArduinoIsRunning = True
        self.RawFileName = ""
        self.RawString = ""
        self.currentValues = []
    
    def writeRAWFile(self):
        file = open(self.RawFileName, "w")
        file.write(self.RawString)
        file.close()
        return self.RawFileName


    """
    get_file_times(filename_with_path)
    returns a dict with the creation and modification times of the file: {"creation": time.time() of creation, "modification": time.time() of modification}
    
    https://stackoverflow.com/questions/237079/how-to-get-file-creation-modification-date-times-in-python
    """
    def get_file_times(self, filename_with_path):
        rv = {}
        stat = os.stat(filename_with_path)
        rv["modification"] = path.getmtime(filename_with_path)
        if system() == "Windows":
            rv["creation"] = path.getctime(filename_with_path)
        else:
            try:
                rv["creation"] = stat.st_birthtime
            except AttributeError:
                rv["creation"] = stat.st_mtime
        return rv

    """
    get_index_of_dict_by_variable(list_of_dicts, variablename, values)
    
    returns an int with the index indicating index of the dict containing the specific value   
    """
    def get_index_of_dict_by_variable(self, list_of_dicts, variablename, value):
        rv = []
        for i in range(len(list_of_dicts)):
            d = list_of_dicts[i]
            if variablename in d.keys():
                if value is None and d[variablename] is None:
                    rv.append(i)
                elif d[variablename] == value:
                    rv.append(i)
        if len(rv) == 1:
            return rv[0]
        return rv

    """
    get_values_of_variable_in_dict_list(list_of_dicts, variablename)
    
    returns a list of values of a given variable, if the variable is not specified the dict, an ValueException is raised
    """
    def get_values_of_variable_in_dict_list(self, list_of_dicts, variablename, extend=False):
        rv = []
        hasAValue = False
        for d in list_of_dicts:
            if variablename in d.keys():
                if extend:
                    rv.extend(d[variablename])
                else:
                    rv.append(d[variablename])
                hasAValue = True
            else:
                rv.append[None]
        if hasAValue:
            return rv
        else:
            return None


    """
    Checks the next avaialable file for the temporary files.
    
    string ... Filename (incl. path information)
    ext ... Extension
    getlatest ... bool, provides the latest file created (False by default)
    """

    def getavailableFileName(self, string, ext, getlatest=False):
        running = 0
        while os.path.exists(string + str(running) + ext):
            running += 1
        if getlatest:
            return string + str(running - 1)
        return string + str(running)

    """
    Calculates values using an RPN-String (each element separated by space) 
    Parameters:
    - RPN_String (see technical documentation for details)
    - Variable values (an unlimited number of variables can be used in the string): dict with symbols as keys and float values
    
    Optional Paramter:
    round = <Integervalues> : Number of decimals to be rounded to   
    """
    def calculate_using_RPN(self, RPN_string, variableValues_list, **kwargs):
        def single_value_calc(variableValues, **kwargs):
            stack=[]
            RPN_parts=RPN_string.split(" ")
            operations_special_numbers = ["pi"]
            operations_2_v = ["+", "-", "*", "/", "%", "**", "^"]
            operations_1_v = ["SQRT", "SIN", "COS", "TAN", "ASIN", "ACOS", "ATAN", "EXP"]
            stacklen = 0
            for p in RPN_parts:
                n = self.str_to_float(p)
                if n is not None:
                    stack.append(float(p))
                    stacklen += 1
                else: #p is string
                    if p in variableValues.keys() and variableValues[p] is not None:
                        stack.append(variableValues[p])
                        stacklen += 1
                        
                    elif p in operations_2_v and stacklen > 1:
                        b = stack.pop()
                        a = stack.pop()
                        if p == "+":
                            stack.append(a+b)
                        elif p == "-":
                            stack.append(a-b)
                        elif p == "*":
                            stack.append(a*b)
                        elif p == "/":
                            stack.append(a/b)
                        elif p == "%":
                            stack.append(a%b)
                        elif p == "**" or p == "^":
                            stack.append(np.power(a, b))
                        stacklen -= 1
                    elif p in operations_1_v and stacklen > 0:
                        a = stack.pop()
                        if p == "SQRT":
                            stack.append(np.exp(a))
                        elif p == "SIN":
                            stack.append(np.sin(a))
                        elif p == "COS":
                            stack.append(np.cos(a))
                        elif p == "TAN":
                            stack.append(np.tan(a))
                        elif p == "ASIN":
                            stack.append(np.arcsin(a))
                        elif p == "ACOS":
                            stack.append(np.arccos(a))
                        elif p == "ATAN":
                            stack.append(np.arctan(a))
                        elif p == "EXP":
                            stack.append(np.exp(a))
                    elif p in operations_special_numbers:
                        if p == "pi":
                            stack.append(np.pi)
                        stacklen += 1
                    elif p == "":
                        continue
                    else:
                        return None
            if len(stack) != 1:
                return None
            
            if "round" in kwargs and (type(kwargs["round"]) is int or type(kwargs["round"]) is float):
                return round(stack[0], int(kwargs["round"]))
            return stack[0]
        
        rv = []
        values_length = []
        max_length = -1
        first = True
        for k in variableValues_list.keys():
            if type(variableValues_list[k]) is list:
                l = len(variableValues_list[k])
                values_length.append((k, l))
                if l > max_length or first:
                    first = False
                    max_length = l
            else:
                values_length.append((k, -1))
        if max_length < 0:
            rv = single_value_calc(variableValues_list)
        else:
            i = 0
            while i < max_length:
                vlsc = {}
                calc_possible = True
                for ll in values_length:
                    if ll[1] <= i:
                        calc_possible = False
                    else:
                        vlsc[ll[0]] = variableValues_list[ll[0]][i]
                if calc_possible:
                    rv.append(single_value_calc(vlsc))
                else:
                    rv.append(None)
                i += 1
        return rv
    
    def str_to_float(self, string):
        def calc(s2):
            if type(s2) is not str:
                if type(s2) is float or type(s2) is int:
                    try:
                        return float(s2)
                    except:
                        pass
                return None
            if bool(regex_int.match(s2)):
                try:
                    return float(s2)
                except:
                    pass
            if bool(regex_eng.match(s2)) and not bool(regex_ealone.match(s2)):
                try:
                    return float(s2)
                except:
                    pass
            if bool(regex_ger.match(s2)) and not bool(regex_ealone.match(s2)):
                try:
                    return float(s2.replace(",", "."))
                except:
                    pass
            return None

        regex_eng = compile(r'^[-+]?\d*\.?\d*[eE]?[-+]?\d*$')
        regex_ger = compile(r'^[-+]?\d*,?\d*[eE]?[-+]?\d*$')
        regex_int = compile(r'^\d*$')
        regex_ealone = compile(r'^[eE]?[+-]?\d*$')

        rv = []

        if type(string) is list:
            for e in string:
                if type(e) is str:
                    rv.append(calc(e.strip()))
                if type(e) is int or type(e) is float:
                    rv.append(calc(e))
            return rv
        if type(string) is str:
            return calc(string.strip())
        if type(string) is int or type(string) is float:
            return calc(string)
        return None

    """
    rounddigits rounds a float either to by applying round or by the number of significant digits
    if values for both are provided, rounding for significant digits is applied
    
    Parameter:
    - number (float)
    - round_digits (number of digits for round())
    - significant_digits (number of significant digits)
    """
    def rounddigits(self, number, round_digits, significant_digits):
        formatstring = None
        if type(number) is float and type(significant_digits) is int and significant_digits > 0:
            formatstring = "."+str(significant_digits)+"g"
        elif type(number) is float and type(round_digits) is int and round_digits > 0:
            formatstring = "."+str(round_digits)+"f"
        if formatstring is not None:
            return format(number, formatstring)
        return number
    
    """def rounddigits_with_error(self, vals, errs, rd=None, sig=None, errorsens = True):
        errs1 = [str(self.rounddigits(x, rd, sig)) for x in errs]
       """
    
    """
    getSerialPorts
    Returns a list of the available Serialports: for each port, the list contains a list l with the follwing information:
    0: PortName/Number (to be forwarded to the Arduino class)
    1: Description
    """
    
    def getSerialPorts(self):
        rv = list()
        ports = list(lipo.comports())
        for p in ports:
            rv.append(str(p).split(" - "))
        return rv
    
    def getCurrentValue(self):
        return self.currentValues
    
    def setCurrentValue(self, v):
        self.currentValues = v
