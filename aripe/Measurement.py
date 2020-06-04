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

class Data:
    def __init__(self, variables, **kwargs):
        self.reservedNames = ["SYS_Time", "MEASUREMENT_GROUP"]
        self.independent_dependent = False         #Helper variable to determine quickly whether a single variable is included or a independent-dependent-pair
        self.values = {"SYS_Time": []}
        self.unit = {"SYS_Time": "s"}
        self.error = {"SYS_Time": 0.1}
        self.comment = {"SYS_Time": "Systemzeit seit 01.01.1970, 00:00.00"}
        self.name_independent = ""
        self.calulatedcerror = {}
        self.number_of_variables = 1
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
                for m in range(n+1,len(names))
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
                n = v["name"].strip()
                self.values[n] = []
                self.unit[n] = v["unit"].strip()
                self.error[n] = self._ini_helper_error(v["error"])
                self.calulatedcerror[n] = []
                if "comment" in v.keys():
                    self.comment[n] = v["comment"]
                else
                    self.comment[n] = ""
        elif type(variables) is dict:
            if self._checkProperVariableDeclaration(variables):
                n = variables["name"].strip()
                self.values[n] = []
                self.unit[n] = variables["unit"].strip()
                self.error[n] = self._ini_helper_error(variables["error"])
                if "comment" in variables.keys():
                    self.comment[n] = variables["comment"]
                else:
                    self.comment[n] = ""
            else:
                raise ValueError("ERR-D-INI07: The dictionary for the variables ")
        else:
            raise ValueError("ERR-D-INI06: For single variable the constructor must contain a dict or a list of dicts.")

        # Handle importing values, with integrity check
        if "values" in kwargs:
            self.importValues(kwargs["values"])

        #Should a column for Measurement Group be added? That allows statistical measurements.
        self.useGroupedMeasurement = False
        if "GroupedMeasurement" in kwargs and type(kwargs["GroupedMeasurement"]) is bool:
            self.useGroupedMeasurement = kwargs["GroupedMeasurement"]

        self.tmpFileName = "data_" + str(time()).split(".")[0]
        if "proj_tmp_file" in kwargs:
            self.tmpFileName = self._getavailableFileName(kwargs["proj_tmp_file"] + "_data-")+"_"


    """
    Helper for __init__-Method: Determines the error information for a variable
    """
    def _ini_helper_error(self, errorinfo):
        rv = 0.0
        if type(errorinfo) is str:
            if errorinfo == "":
                return []
            else:
                try:
                    rv = float(errorinfo)
                except ValueError:
                    try:
                        rv = float(errorinfo.replace(",","."))
                    except ValueError:
                        rv = errorinfo
                return rv
        elif type(errorinfo) is float or type(errorinfo) is int:
            return float(errorinfo)

    """
    Helper: Extracts the variable names
    """
    def _listvariablenames(self, excludesys=False):
        rv = []
        for key in self.values:
            if excludesys:
                if key in self.reservedNames:
                    continue
            rv.append(key)
        return rv
    """
    Helper, checks the next avaialable file for the temporary files.
    """
    def _getavailableFileName(self, string):
        running = 0
        while path.exists(string+str(running)+"_.meta"):
            running += 1
        return string+str(running)

    """
    Helper, checks whether variable declaration is proper
    """

    def _checkProperVariableDeclaration(self, vardecl):
        k = vardecl.keys()
        if "name" not in k:
            return False
        if "unit" not in k:
            return False
        if "error" not in k:
            return False
        return True

    """
    Importing values into the table with integrity check
    val:
      - List of dicts containing the fields "name", "values", "error"
      - single dict with fields mentioned above
    timematched=True data shall be included for timematched values (see documentation for information about systime): val must contain of two lists: val[0] list of systimepoints, val[1] data to import
    tmtolerance tolerance for timematching (in seconds)
    
    addnewcolumn: A new set of values shall be included, important: timematching for addnewcolumn is compulsory
    
    """
    def importValues(self, val, timematched=False, tmtolerance=0.5, addnewcolumn=False, append=False):
        if type(val) is list:
            if



            if len(val["values"]) != self.values("SYS_Time")


                if type(val) is list and (len(val) == self.number_of_variables):
                    for i in range(self.number_of_variables - 1):
                        if type(val[i]) is not list:
                            raise ValueError("ERR-M-VALIMPORT01: Error with importing values[" + str(i) + "]. It's not a list.")
                        if type(val[i + 1]) is not list:
                            raise ValueError("ERR-M-VALIMPORT02: Error with importing values[" + str(i + 1) + "]. It's not a list.")
                        if len(val[i]) != len(val[i + 1]):
                            raise ValueError("ERR-M-VALIMPORT03: Error with importing values. The numbers for values[" + str(i) + "] and values[" + str(i + 1) + "] do not match.")
                    self.values = val
                else:
                    raise ValueError("ERR-M-VALIMPORT04: Error with importing values. The number of defined variables and imported variables do not match. OR: values is not a list.")
            else:
                if val is not list:
                    raise ValueError("ERR-M-VALIMPORT05: Error with importing values. The values are not stored in a list")
                self.value = val
        else:
            if type(focus) is str:
                try:
                    focus = self.getcolumn(focus, getvalues=False)
                except ValueError as err:
                    raise ValueError(str(err))
            if type(focus) is not int:
                raise ValueError("ERR-M-VALIMPORT06: Focus is neither int nor string containing a valid name.")
            if type(val) is not list:
                raise ValueError("ERR-M-VALIMPORT07: Data for single variable import must be contained in a list.")
            if len(val) == 0:
                raise ValueError("ERR-M-VALIMPORT08: There must be some data to import.")


    """
    getcolumn(column, values)
    column: either variable name or number of column (starting with 0)
    """
    def getcolumn(self, column, getvalues=True):
        if type(column) is str:
            try:
                column = self.name.index(column)
            except ValueError:
                raise ValueError("ERR-M-GETC01: There is no column with this name.")
        else:
            if type(column) is not int:
                raise ValueError("ERR-M-GETC02: The column parameter must either be a string or an integer.")
            elif column > len(self.values)-1:
                raise ValueError("ERR-GETC03: The number of columns exceed the number of variables stored.")
        if not getvalues:
            return column
        else:
            return self.values[column]

    def addValue(self, value, **kwargs):
        if self.independent_dependent:
            if type(value) is list or type(value) is tuple:
                self.values[0].append(value[0])
                self.values[1].append(value[1])
            else:
                raise LookupError("ERR04 Measurement: This class handles an independent-dependent variable pair, you try to add only one value.")
            if type(self.error[0]) is list:
                if
        else:
            self.values.append(value)
        if len(kwargs) != 0:
            if type(self.error) is list:
                try:
                    self.error.append(float(kwargs["errorvalue"]))
                except KeyError:
                    raise LookupError
                except ValueError:
                    try:
                        a = kwargs["errorvalue"].replace(",", ".")
                        self.error.append(float(a))
                    except ValueError:
                        raise ValueError

    def calcError(self):
        if type(self.error = )

    def returnValue(self):
        rv = {"values": self.values, "error": None}
        if type(self.error) is list:
            if len(self.error) != 0:
                rv["error"] = self.error
        elif type(self.error) is float:
            rv["error"] = self.error
        else:
            if len(self.calcerrors) != len(self.values):
                try:
                    self.calcError()
                    rv["error"] = self.calcerrors
                except ValueError:
                    rv["error"] = None
            if len(values) == 0:
                rv["values"] = None
        return rv
