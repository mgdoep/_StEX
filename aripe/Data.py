# coding: utf8

"""
aripe.Data is a class that works as a data container with a number of data inserted
All data manipulation is also defined in this class
It gets the following parameters:
- variables: List of dicts or a single dict containing the following entries:
    * name (What is the measured variable called: e.g. current, temperature): String or Tuple of Strings
    * unit (What is the unit of the measured variable: e.g. mA, K): String or Tuple of Strings
    * error (optional, What is the error of the measurement):
        > no argument given, it is assumed that either no error is logged or an individual error is given for each value (e.g., input by hand)
        > argument is float: fixed error for each measurment (e.g. distance measurement using a ruler: error = 1 mm)
        > argument is string: error is calculated using this string, string must be given in RPN
"""

from copy import deepcopy
from time import time
from os import path
from .Helper import Helper
from .Project import Project



class Data:
    def __init__(self, variables, **kwargs):
        self.misc = Helper()
        self.reservedNames = ["SYS_Time", "MEASUREMENT_GROUP", "FILTER"]
        self.values = {"SYS_Time": [], "FILTER": []}
        self.unit = {"SYS_Time": "s"}
        self.error = {"SYS_Time": []}
        self.comment = {"SYS_Time": "Systemzeit seit 01.01.1970, 00:00.00", "FILTER": "Wert, ob "}
        self.errorrule = {"SYS_Time": 0.1}
        self.name_independent = ""
        self.filter = {}

        self._values_backup = None
        self._unit_backup = None
        self._error_backup = None
        self._comment_backup = None
        self._errorrule_backup = None

        self._currentImportNumber = 0

        self.number_of_variables = 1

        path_to_value_file = None
        path_to_project_file = None

        if "fromMetadata" in kwargs and type(kwargs["fromMetadata"]) is str:
            variables, path_to_value_file, path_to_project_file = self.createFromMetadata(kwargs["fromMetadata"])

        if type(variables) is list:
            names = []
            for v in variables:
                if not self._checkProperVariableDeclaration(v):
                    raise ValueError("ERR-D-INI01: In the list of variable declarations is an error.")
                if type(v["name"]) is not str:
                    raise ValueError("ERR-D-INI02: The of one variable in the list is not a string.")
                if type(v["unit"]) is not str:
                    raise ValueError("ERR-D-INI03: The unit of one variable in list is not a string.")
                names.append(v["name"])
            for n in range(len(names)-1):
                for m in range(n+1,len(names)):
                    names[n] = names[n].strip()
                    names[m] = names[m].strip()
                    if names[n] == names[m]:
                        raise ValueError("ERR-D_INI04: The names of the variables must be unique.")
                    if names[n] in  self.reservedNames or names[m] in self.reservedNames:
                        raise ValueError("ERR-D-INI05: A reserved variable name is used.")
            self.independent_dependent = True
            self.number_of_variables = len(names)
            self.name_independent = names[0]
            for v in variables:
                s = self._addVarUsingDef(v)

        elif type(variables) is dict:
            if self._checkProperVariableDeclaration(variables):
                s = self._addVarUsingDef(variables)
            else:
                raise ValueError("ERR-D-INI07: The dictionary for the variables is incorrect.")
        else:
            raise ValueError("ERR-D-INI06: For single variable the constructor must contain a dict or a list of dicts.")

        # Handle importing values, with integrity check
        if "values" in kwargs and "fromMetadata" not in kwargs:
            if type(kwargs["values"]) is list:
                for v in kwargs["values"]:
                    self.importValues(v, append=True)
            elif type(kwargs["values"]) is dict:
                self.importValues(kwargs["values"])
            else:
                raise ValueError("ERR-D-INI08: values must either be dict or a list of dicts.")
        elif "fromMetadata" in kwargs:
            val = self.getValuesFromCSV(path_to_value_file)
            for v in val:
                self.importValues(v, append = True)

        """#Should a column for Measurement Group be added? That allows statistical measurements.
        self.useGroupedMeasurement = False
        if "GroupedMeasurement" in kwargs and type(kwargs["GroupedMeasurement"]) is bool:
            self.useGroupedMeasurement = kwargs["GroupedMeasurement"]
            if self.useGroupedMeasurement and "MEASUREMENT_GROUP" not in self.values.keys():
                self.values["MEASUREMENT_GROUP"] = []"""

        self.StandardFolder = ""
        self.relatedProject = None
        self.tmpFileName = self.misc.getavailableFileName(self.StandardFolder+ str(time()).split(".")[0]+"_data-", ".meta")
        if "project" in kwargs:
            self.relatedProject = kwargs["project"]
            self.tmpFileName = self.misc.getavailableFileName(self.relatedProject.getTMPFileName() + "_data-", ".meta")

    """
    _ini_helper_error()
    gets the errorinfo string and transfer it to something useful for self.error:
    - returns
        -None, if errors are either protocolled for each value or no errors are recorded
        - a float
        - a string (that should be a formula in RPN)
    Parameter:
        errorinfo: string defining errors
    """

    def _ini_helper_error(self, errorinfo):
        rv = 0.0
        if type(errorinfo) is str:
            if errorinfo == "":
                return None
            else:
                rv = self.misc.str_to_float(errorinfo)
                if rv is None:
                    rv = errorinfo
                return rv
        elif type(errorinfo) is float or type(errorinfo) is int:
            return float(errorinfo)
        else:
            raise ValueError("ERR-D-ERRORINIT: The error information is neither a string nor a float or integer.")


    """
    Helper, adds a new Variable in the relevant dictionaries
    """
    def _addVarUsingDef(self, var):
        n = var["name"].strip()
        if n in self.values.keys:
            return False
        else:
            self.values[n] = []
            self.unit[n] = var["unit"].strip()
            self.errorrule[n] = self._ini_helper_error(var["errorrule"])
            self.error[n] = []
            if "comment" in var.keys():
                self.comment[n] = var["comment"]
            else:
                self.comment[n] = ""
            return True
    """"
    Helper, removes a variable from all the relevant dictionaries
    """
    def _delVar(self, name):
        n = name.strip()
        self.values.pop(n, None)
        self.unit.pop(n, None)
        self.errorrule.pop(n, None)
        self.error.pop(n, None)
        self.comment.pop(n, None)
    """
    Helper: Extracts the variable names
    """
    def _listvariablenames(self, excludesys=False):
        rv = []
        for key in self.values:
            if excludesys:
                if key in self.reservedNames:
                    continue
            rv.append(str(key))
        return rv

    """
    Helper, checks whether variable declaration is proper
    """
    def _checkProperVariableDeclaration(self, vardecl):
        checkfor = ["name", "unit", "errorrule"]
        rv = True
        k = vardecl.keys()
        for i in checkfor:
            if rv:
                rv = i in k
        return rv

    """"
    Helper: Uses backup instances of the data to undo changes made
    delbackup ... sets backup instances to None (True by default)
    """
    def _undochanges(self, delbackup = True):
        if self._values_backup is not None:
            self.values = deepcopy(self._values_backup)
            if delbackup:
                self._values_backup = None
        if self._unit_backup is not None:
            self.unit = deepcopy(self._unit_backup)
            if delbackup:
                self._unit_backup = None
        if self._error_backup is not None:
            self.error = deepcopy(self._error_backup)
            if delbackup:
                self._error_backup = None
        if self._errorrule_backup is not None:
            self.errorrule = deepcopy(self._errorrule_backup)
            if delbackup:
                self._errorrule_backup = None
        if self._comment_backup is not None:
            self.comment = deepcopy(self._comment_backup)
            if delbackup:
                self._comment_backup = None

    """"
    Helper, creates backup instances of the relevant data:
    valbackup ... bool, whether values are backed up (True by default)
    unitbackup ... bool, whether unit data is backed up (True by default)
    errbackup ... bool, whether error values are backed up (True by default)
    errrulebackup ... bool, whether error rules ares backed up (True by default)
    commentbackup ... bool, whether comments are backed uo (True by default)
    enforce ... bool, backup is created regardless of whether existing backups are overwritten (True by default, as one might think, you know what you do)
    """

    def _createbackups(self, valbackup = True, errrulebackup = True, errbackup = True, unitbackup = True, commentbackup = True, enforce = True):
        if valbackup and (enforce or self._values_backup is None):
            self._values_backup = deepcopy(self.values)
        if unitbackup and (enforce or self._unit_backup is None):
            self._unit_backup = deepcopy(self.unit)
        if errbackup and (enforce or self._error_backup is None):
            self._error_backup = deepcopy(self.error)
        if errrulebackup and (enforce or self._errorrule_backup is None):
            self._errorrule_backup = deepcopy(self.errorrule)
        if commentbackup and (enforce or self._comment_backup is None):
            self._comment_backup =deepcopy(self.comment)

    def createMetaXML(self, createnew=False):
        string = self.tmpFileName.split(".meta")[0].split("_data-")[0]
        fnold = self.misc.getavailableFileName(string, ".meta", getlatest=True)+".meta"
        filename = self.misc.getavailableFileName(string, ".meta")+".meta"
        previousdatafiles = []
        if not createnew:
            for line in open(fnold, "r").readlines():
                if "<datafile>" in line:
                    previousdatafiles.append(line)
        variables = self.values.keys()

        string = "<aripeDataMeta>\n\n"
        string += "<project>\n"+str(self.relatedProject)+"\n</project>\n"
        string += "<variables>\n"
        for v in variables:
            string += "\t<variable>\n\t\t<varname>"+v+"</varname>\n"
            string += "\t\t<comment>"+self.comment[v]+"</comment>\n"
            string += "\t\t<unit>"+self.unit[v]+"</unit>\n"
            string += "\t\t<errorrule>"+self.errorrule[v]+"</errorrule>\n\t</variable>"
        string += "</variables>\n"
        string += "<useGroupMeasurement>"+str(self.useGroupedMeasurement)+"</useGroupMeasurement>\n"
        string += "<datafiles>\n"
        for v in previousdatafiles:
            string += v
        string += "<datafile creationTimePoint=\""+str(path.getctime(self.tmpFileName+".val"))+"\" lastmodifyTimePoint=\""+str(path.getmtime(self.tmpFileName+".val"))+"\">"+self.tmpFileName+".val</datafile>\n"
        string += "</datafiles>\n"
        string += "\n\n</aripeDataMeta>"
        file = open(filename, "w")
        file.write(string)
        file.close()

    """
    calculateErrors(variablename)
    If a RPN-String is given for error calculation, this method calculates the errors
    variablename: Name of the variable, the errors shall be calculated for
    
    returns a bool: True if successful, False if not
    """
    def calculateErrors(self, variablename):
        if (variablename in self.values.keys()) and (type(self.errorrule[variablename]) is str):
            er = self.errorrule[variablename]
            if "VAR" in er:
                er.replace("VAR", variablename)
            if variablename not in er:
                return False
            e = self.misc.calculate_using_RPN(er, {variablename: self.values[variablename]})
            if e is not None:
                self.error[variablename] = e
                return True
        return False


    """"
    getDataFromMetadata(path)
    
    This method can be used to extract relevant information from a metadata file generated 
    
    path ... Path to metadata file generated by Data.aripe 
    
    returns 3 values: 
    list_of_dict_with_variable_definition, path_to_newest_datafile, path_to_related_project_file = getDataFromMetadata(path)
    
    """
    def getDataFromMetadata(self, path):
        try:
            import xml.etree.ElementTree as ET
            tree = ET.parse(path)
            root = tree.getroot()
        except ImportError:
                return None, None, None
        except FileNotFoundError:
                return None, None, None

        rv_list_of_dict = []

        project_file_path = root.find("project").find("projectfile").text
        rv_path_to_newest_valuefile = root.find("datafiles").findall("datafile")[-1].text
        for v in root.find("variables").findall("variable"):
            d = {"name": v.find("varname").text,
                 "unit": v.find("unit").text,
                 "comment": v.find("comment").text,
                 "errorrule": v.find("errorrule").text}
            rv_list_of_dict.append(d)
        return rv_list_of_dict, rv_path_to_newest_valuefile, project_file_path

    """
    Importing values into the table with integrity check
    
    val: single dict with fields "values", "name", "error". 
    If this is used to add a new variable: the following information have to be provided in val too: "unit", "errorrule"
    "comment" is optional
    
    timematched=True data shall be included for timematched values (see documentation for information about systime): val must contain of two lists: val[0] list of systimepoints, val[1] data to import
    tmtolerance tolerance for timematching (in seconds), mind that SYS_Time is recorded with an accuracy of 0.1 µs
    Note: For time matching purposes, val needs the field "SYS_Time" (round(time.time()%150 000 000, 7))
    
    addnew: A new set of values shall be included, important: timematching for addnew is compulsory, meaning that a timematched = False will be ignored.
    
    append: The values shall be appended to a new given set of variables (e.g. for merching purposes)
    
    Note: addnew and append cannot be True at the same time!
    """
    def importValues(self, val, timematched=False, tmtolerance=0.5, addnew=False, append=False, importerrors=False):
        self._createbackups()

        if type(val) is dict:
            k = val.keys()
        else:
            raise ValueError("ERR-D-IMVAL00: Values have to be provided using a dict.")
        if addnew and append:
            raise ValueError("ERR-D-IMVAL01: append and new cannot be True at the same time.")
        n = val["name"].strip()
        if addnew:
            timematched = True
            if not self._checkProperVariableDeclaration(val) or "SYS_Time" not in k:
                raise ValueError("ERR-D-IMVAL02: The dict provided in val does not contain the necessary fields.")
            if val["name"] in self.values.keys():
                raise ValueError("ERR-D-IMVAL03: A variable with the name exists already.")
            success = self._addVarUsingDef(val)
        if val["name"] == "SYS_Time" and not append:
            if len(self.values["SYS_Time"]) == 0:
                self.values["SYS_Time"] = val["values"]
                return
            else:
                raise ValueError("ERR-D-IMVAL04: SYS_Time is not empty.")
        if timematched:
            if "SYS_Time" not in k:
                if addnew:
                    self._delVar(n)
                raise ValueError("ERR-D-IMVAL05: SYS_Time has to be provided.")
            if len(val["SYS_Time"]) != len(val["values"]):
                if addnew:
                    self._delVar(n)
                raise ValueError("ERR-D-IMVAL06: Length of SYS_Time and Values do not match.")
            index_lastimport = -1
            maxindex = len(val["SYS_Time"])
            for x in range(len(self.values["SYS_Time"])):
                candidates = []
                cont = True
                i = index_lastimport + 1
                while cont and i < len(val["SYS_Time"]):
                    difference = val["SYS_Time"][i] - self.values["SYS_Time"]
                    if difference < (-1.0)*tmtolerance:
                        i += 1
                    elif difference > (-1.0)*tmtolerance-(1e-15) and difference < tmtolerance+(1e-15):
                        candidates.append((i, difference))
                        i += 1
                    else:
                        cont = False
                    if cont and i == maxindex:
                        cont = False
                if len(candidates) == 0:
                    self.values[n].append(None)
                    if importerrors:
                        self.error[n].append(None)
                elif len(candidates) == 1:
                    self.values[n] = val["values"][candidates[0][0]]
                    if importerrors:
                        self.error[n] = val["error"][candidates[0][0]]
                    index_lastimport = candidates[0][0]
                else:
                    nearest = 0
                    for i in range(1, len(candidates)):
                        if abs(candidates[nearest][1]) > abs(candidates[i][1]):
                            nearest = i
                    self.values[n] = val["values"][candidates[nearest][0]]
                    if importerrors:
                        self.error[n] = val["error"][candidates[nearest][0]]
                    index_lastimport = candidates[nearest][0]
        else:
            if len(self.values["SYS_Time"]) != len(val["values"]):
                raise ValueError("ERR-D-IMVAL07: The number of values, you want to add does not match the number of values in the dataset.")
            self.values[n] = val["values"]
            if importerrors:
                self.error[n] = val["error"]
        if append:
            n = val["name"].strip()
            addmultiple = (n == "")
            vars_to_append = []
            if addmultiple:
                vars_to_append = val.keys()
            allvariables = self.values.keys()
            foe = self.values["SYS_Time"][-1]
            for vindex in range(len(val["SYS_Time"])):
                if val["SYS_Time"][vindex] > foe:
                    self.values["SYS_Time"].append(val["SYS_Time"][vindex])
                    if not addmultiple:
                        try:
                            self.values[n].append(val["values"][vindex])
                            if importerrors:
                                self.error[n].append(val["error"][vindex])
                        except KeyError:
                            self._undochanges()
                            raise ValueError("ERR-IMVAL08: There seems to be a problem with the variable name.")
                    for v in allvariables:
                        if not addmultiple and n not in ["SYS_Time", v]:
                            self.values[v].append(None)
                        elif addmultiple and n != "SYS_Time":
                                if v in vars_to_append:
                                    self.values[v].append(val[v][vindex])
                                    if importerrors:
                                        self.error[v].append(val[v+"_ERROR"][vindex])
                                else:
                                    try:
                                        self.values[v].append(None)
                                        if importerrors:
                                            self.error[v].append(val[v][vindex])
                                    except:
                                        self._undochanges()


    def saveValues(self, witherrors=True, empty="None", **kwargs):
        istmpfile = True
        filename = self.misc.getavailableFileName(self.tmpFileName, ".values")
        if "filename" in kwargs:
            filename = kwargs["filename"]
            istmpfile = False

        variables = []
        vari = self.values.keys()
        if "variables" in kwargs and ".values" not in filename:
            for v in kwargs["variables"]:
                if v in vari:
                    variables.append(v)
        else:
            for v in vari:
                variables.append(v)

        seperator = ";"
        if "seperator" in kwargs:
            seperator = kwargs["seperator"]

        length_value = []
        length_error = []
        for v in variables:
            length_value.append(len(self.values[v]))
            length_error.append(len(self.error[v]))


        file = open(filename, "w")
        string = ""
        nov = len(variables)
        for i in range(nov):
            string += variables[i] + " [" + self.unit[variables[i]] + "]"
            if witherrors:
                string += ";"+variables[i]+"_ERROR"
            if i == nov-1:
                string += "\n"
            else:
                string += seperator
        file.write(string)


        nol = len(self.values["SYS_Time"])
        for i in range(nol):
            string = ""
            for j in range(nov):
                if i < length_value[j]:
                    if istmpfile or self.values[variables[j]][i] is not None:
                        string += str(self.values[variables[j]][i])
                    else:
                        string += empty
                elif istmpfile:
                    string += "None"
                else:
                    string += empty
                if witherrors:
                    string += seperator
                    if i < length_error[j]:
                        if istmpfile or self.error[variables[j]][i] is not None:
                            string += str(self.error[variables[j][i]])
                    elif istmpfile:
                        string += None
                    else:
                        string += empty
                if j == nov-1:
                    string += "\n"
                else:
                    string += seperator
            file.write(string)
        file.close()

    """
    getValuesFromCSV(self, filename, witherrors=True, error_column_app="_ERROR")
    filename ... Filename (with path)
    error_column_app ... Suffix of the column providing error information
    
    optional parameters:
    seperator ... Seperation character between columns (normally ";")
    output ... What kind of output is desired?:
        "list-known" ... list of dicts of already defined variables 
        
    returns:
        - a list of dicts OR
        - a single dict 
    """

    def getValuesFromCSV(self, filename, error_column_app="_ERROR", **kwargs):
        rv = []
        add_unknown = False
        if "output" in kwargs:
            if "dict" in kwargs["output"]:
                rv = {"name": "", "errorrule": "", "values": [], "error": []}
            add_unknown = "unknown" in kwargs["output"]

        rv_is_list = type(rv) is list
        imported_variables = []
        imported_errors = []
        imported_units = []
        is_defined = []
        seperator = ";"

        if "seperator" in kwargs:
            seperator = kwargs["seperator"]
        file = open(filename, "r")
        lines = file.readlines()
        file.close()

        #Get variable information
        line = lines[0].strip().split(seperator)
        number_of_columns = len(line)
        for i in range(number_of_columns):
            li = lines[0].split("[")
            info = li[0].strip()
            if error_column_app in info:
                imported_errors.append(info.split(error_column_app)[0].strip())
                imported_variables.append(None)
                is_defined.append(info.split(error_column_app)[0].strip() in self.error.keys())
            else:
                imported_variables.append(info.strip())
                imported_errors.append(None)
                is_defined.append(info.strip() in self.values.keys())

            if len(li) > 1:
                imported_units.append(li[1].split("]")[0].strip())
            else:
                imported_units.append("")

        SYS_Time_provided = "SYS_Time" in imported_variables
        for i in range(number_of_columns):
            if rv_is_list and (is_defined[i] or add_unknown):
                if imported_variables[i] is not None:
                    dict_to_add = {"name": imported_variables[i],
                                   "unit": imported_units[i],
                                   "values": [],
                                   "errorrule": "",
                                   "error": []}
                    if SYS_Time_provided:
                        dict_to_add["SYS_Time"] = []
                    rv.append(dict_to_add)
            elif is_defined[i] or add_unknown:
                key = imported_variables[i]
                if imported_variables is None:
                    if imported_errors[i] in imported_variables:
                        key = imported_errors[i]+"_ERROR"
                    else:
                        key = None
                        imported_errors = None
                if key is not None:
                    rv[key] = []
            else:
                pass
        if rv_is_list:
            rv_vars = self.misc.get_values_of_variable_in_dict_list(rv, "name")
            rv_indexes = {}
            for i in range(len(rv_vars)):
                rv_indexes[rv_vars[i]] = i
            del rv_vars
        for i in range(1, len(lines)):
            line = lines[i].split(seperator)
            if len(line) != number_of_columns:
                continue
            else:
                for c in range(number_of_columns):
                    if is_defined[c] or add_unknown:
                        if rv_is_list:
                            if imported_variables[c] is not None:
                                index = rv_indexes[imported_variables[c]]
                                try:
                                    rv[index]["values"].append(float(line[c].strip()))
                                except ValueError:
                                    rv[index]["values"].append(line[c].strip())
                            elif imported_errors[c] in imported_variables:
                                index = rv_indexes[imported_errors[c]]
                                try:
                                    rv[index]["error"].append(float(line[c].strip()))
                                except ValueError:
                                    rv[index]["error"].append(line[c].strip())
                        else:
                            if imported_variables[c] is not None:
                                try:
                                    rv[imported_variables[c]].append(float(line[c].strip()))
                                except ValueError:
                                    rv[imported_variables[c]].append(line[c].strip())
                            elif imported_errors[c] is not None:
                                try:
                                    rv[imported_errors[c]+"_ERROR"].append(float(line[c].strip()))
                                except ValueError:
                                    rv[imported_errors[c]+"_ERROR"].append(line[c].strip())
        return rv


    """
    addValues
    adds values and (if provided) errors to the dicts
    
    Note: Run prepareForAdding
    
    Parameter
    - vallist ... List of tuples:
        - vallist[i][0] ... String (variablename)
        - vallist[i][1] ... value (can be str)
        - vallist[i][2] ... errorvalue (can be str)
    - adderrors ... bool, whether error shall be included, Default: True. Note: If the error of one of the variables shall be recorded,
    all values have to be provided with a value (preferably 0.0)
    
    For the sake of speed, addValue just appends the list. Therefore it is strongly recommended to run
    valueTransformation() afterwards.

    """
    def addValues(self, vallist, adderrors=True, addSysTime=True):
        number_added = 0            #Use this instead of len(importedvars) for the sake of speed
        importedvars = []
        importederrors = []
        for v in vallist:
            try:
                varname = v[0].strip()
                number_added = number_added + 1
                importedvars.append(varname)
            except KeyError:
                continue
            try:
                self.values[varname].append(v[1])
            except KeyError:                        #Take next element, importing error doesn't make sense
                number_added = number_added - 1
            if adderrors:
                try:
                    self.error[varname].append(v[2])
                    importederrors.append(varname)
                except KeyError:
                    pass

        if number_added > 0 and addSysTime:
            self.values["SYS_Time"].append(time())
        elif number_added < 2:
            for v in importedvars:
                throwaway = self.values[v].pop()
    """
    valueTransformation()   
    This method shall be run after the addition of new data, it converts Strings to numbers and 
    and extends lists in self.values and self.error with None, if length do not match the SYS_Time 
    vector
    """

    def valueTransformation(self):
        length = len(self.values["SYS_Time"])
        for k in self.values.keys():
            if k not in self.reservedNames:
                t = self.misc.str_to_float(self.values[k])
                if t is not None:
                    self.values[k] = t
                if len(self.values[k]) < length:
                    self.values[k].extend([None]*(length-len(self.values[k])))
                if k in self.error.keys() and len(self.error[k]) < length:
                    self.error[k].extend([None]*(length-len(self.values[k])))


    """
    returnValue(variablename)
    returns a dict with the following keys:
    - value: containing the values of the variable
    - error: containing the error values (which are calculated if neccessary)
    - unit: containing the unit
    
    The values can be rounded to significant digits or decimal places by providing the optional parameters
    - round_to=<number of decimal places>
    - significant_digits=<number of significant digits>
    => see Helper.rounddigits for details
    
    returns None if there is no variable by the name
    """

    def returnValue(self, variablename, **kwargs):
        rounding_to = None
        significant_digits = None
        if "round_to" in kwargs:
            rounding_to = kwargs["round_to"]
        if "significant_digits" in kwargs:
            significant_digits = kwargs["significant_digits"]

        vn = variablename.strip()
        if vn not in self.values.keys():
            return None

        if significant_digits is not None and rounding_to is not None:
            rvval = [self.misc.rounddigits(x, rounding_to, significant_digits) for x in self.values[vn]]
        else:
            rvval = self.values[vn]
        rv = {"values": rvval, "error": None, "unit": self.unit[vn]}

        if type(self.errorrule[vn]) is None:
            rv["error"] = self.error[vn]
        elif type(self.errorrule[vn]) is float:
            rv["error"] = [self.errorrule[vn]]*len(self.values[vn])
        else:
            if self.calculateErrors(vn):
                rv["error"] = self.error[vn]
        return rv

    def shiftFirstValue(self):
        pass

    def writeCSV(self, filename, target=None, **kwargs):
        seperator = ";"
        value_keys = [str(x) for x in self.values.keys()]
        error_keys = [str(x) for x in self.values.keys()]
        if "seperator" in kwargs:
            seperator = kwargs["seperator"]
        if target is None:
            target = value_keys
        else:
            i = 0
            l = len(target)
            if l == 0:
                return False
            while -1 < i < l:
                target[i] = target[i].strip()
                if target[i] not in value_keys:
                    target.remove(i)
                    l -= 1
                    continue
                i += 1
            if l == 0:
                return False

        file = open(filename, "w")
        counter = 0



        file.close()


    """
    cropDataSet(SYS_Time_start, SYS_Time_End, enforce)
    crops the data set, meaning that pplies the "crop" filter to the dataset
    Parameter
    """
    def cropDataSet(self, start, end, TimeVariable="SYS_Time", name="crop", enforce=True):
        if start < 0.0 and end < 0.0:
            return False
        if name in self.filter.keys() and not enforce:
            return False
        TimeVariable = TimeVariable.strip()
        if TimeVariable not in self.values.keys():
            return False
        ltv = len(self.values[TimeVariable])
        for v in self.values:
            if len(self.values[v]) != ltv:
                return False
        if end < 0.0:
            end = float(self.values[TimeVariable][-1])+1.0
        i = 0
        fl = []
        while -1 < i < ltv:
            if start < self.values[TimeVariable][i] < end:
                fl.append(True)
            else:
                fl.append(False)
            i += 1
        self.filter["crop"] = fl
        return True

    def deleteFilter(self, name):
        if name in self.filter.keys():
            del self.filter[name]
            return True
        return False

    def applyEquDistantFilter(self, name, number, independentvar="SYS_Time", basedon="crop", vars=None):
        useindizes = [] # list of the indizes to use
        fl = [] # filterlist
        if vars is None:
            vars = [str(x) for x in self.values.keys()]
        if independentvar not in self.values.keys():
            return False
        startindex = 0
        endindex = len(self.values[independentvar])-1
        if basedon in self.filter.keys():
            i = 0
            foundstart = False
            while i <= endindex:
                if not foundstart and self.filter["crop"][i]:
                    startindex = i
                    foundstart = True
                if foundstart and not self.filter["crop"][i]:
                    endindex = i
                i += 1
        elif basedon is not None:
            return False
        dindex = float((endindex-startindex)/(number-1))
        i = 0
        if independentvar not in vars:
            vars.append(independentvar)
        for v in vars:
            if v not in self.values.keys():
                return False

        while 0 <= i <= number:
            tryindex = startindex + round(float(i)*dindex)          #the index that would be a candidate
            j = 0
            foundindex = False
            while 0 <= j < round(dindex)-1 and not foundindex:      #look in the vicinity of the candidate
                allcan = True
                if i < number:                                      #look right of the candidate
                    for v in vars:
                        if self.values[v][tryindex+j] is None:      #Check for each variable whether there is a value
                            allcan = False
                            break
                    if allcan:                                      #if there is, break j-loop and put the index into the indexlist
                        useindizes.append(tryindex+j)
                        foundindex = True
                        break
                if i > 0 and not foundindex:
                    allcan = True
                    for v in vars:
                         if self.values[v][tryindex-j] is None:
                             allcan = False
                             break
                    if allcan:
                        useindizes.append(tryindex - j)
                        foundindex = True
                j += 1
            i += 1
        
        i = 1
        l = len(useindizes)
        if l > 0:
            fl = [False]*useindizes[0]
            fl.append(True)
        else:
            return False
        while i < l:
            fl.extend([False]*(useindizes[i]-useindizes[i-1]-1))
            fl.append(True)
            i += 1
        fl.extend([False]*(len(self.values[independentvar])-useindizes[-1]-1))
        self.filter[name] = fl
        return True