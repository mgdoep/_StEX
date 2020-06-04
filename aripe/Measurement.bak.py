"""
aripe.Measurement is a class that works as a data container with a number of data inserted
It gets the following parameters:
- name (What is the measured variable called: e.g. current, temperature): String or Tuple of Strings
- unit (What is the unit of the measured variable: e.g. mA, K): String or Tuple of Strings
- error (optional, What is the error of the measurement):
    * no argument given, it is assumed that either no error is logged or an individual error is given for each value (e.g., input by hand)
    * argument is float: fixed error for each measurement (e.g. distance measurement using a ruler: error = 1 mm)
    * argument is string: error is calculated using this string, string must be given in RPN
"""

from copy import deepcopy

class Measurement:
    def __init__(self, name, unit, error="", **kwargs):
        self.independent_dependent = False         #Helper variable to determine quickly whether a single variable is included or a independent-dependent-pair
        if type(name) is tuple:
            if type(unit) is not tuple:
                raise ValueError("ERR01 Measurent: Name suggest that dependent independent, but unit suggests otherwise. No class is generated.")
            else:
                self.independent_dependent = True
        self.name = name
        self.unit = unit
        if self.independent_dependent:
            self.values = [[],[]]
            self.error = [[],[]]
        else:
            self.values = []
            self.error = []

        self.calcerrors = []
        if error != "": #error shall be a list of values when no error is given
            if self.independent_dependent:
                if type(error) is tuple:
                    self.error = [0,0]
                    for i in range(2):
                        try:
                            self.error[i] = float(error[i])
                        except ValueError:
                            if error[i] == "":
                                self.error[i] = []
                            else:
                                self.error[i] = error[i]
                else:
                    raise ValueError("ERR02 Measurement - Error: Name suggests that independent-dependent pair, but error suggests otherwise. No class generated.")
            else:
                try:
                    self.error = float(error)       #error shall be standard value (e.g. 0.5 for each measurement) when
                except ValueError:
                    self.error = error              #error shall be calculated if it is a string, string must be in RPN

        if len(kwargs) != 0:
            if self.independent_dependent:
                if type(kwargs["values"]) is list:
                    if len(kwargs["values"]) == 2:
                        if type(kwargs["values"][0]) is list and type(kwargs["values"][1]) is list:
                            if len(kwargs["values"][0]) == len(kwargs["values"][1]):
                               self.values = kwargs["values"]
                               try:
                                   if len(kwargs("errorvalues")) == len(self.error):
                                       if type(kwargs["errorvalues"][0]) is type(self.error[0]) and type(kwargs["errorvalues"][1]) is type(self.error[1]):
                                           if type(self.error[0]) is list and (len(self.values[0]) != len(kwargs["errorvalues"][0]) and len(kwargs["errorvalues"][0]) != 0):
                                               raise ValueError("ERR08a Measurement - The number of error values for the first imported variable does not match the number of values for the first variable.")
                                            if type(self.error[1]) is list and (if len(self.values[1]) != len(kwargs["errorvalues"][1]) and len(kwargs["errorvalues"[1]) != 0)):
                                                raise ValueError("ERR08b Measurement - The number of error values for the first imported variable does not match the number of values for the first variable.")
                                           self.error = kwargs["errorvalues"]
                                       else:
                                           raise ValueError("ERR07 Measurement - Import Error Error: The types of errorvalues do not match the definition")
                               except KeyError:
                                   pass
                            else:
                                raise ValueError("ERR06 Measurement - Import Value Error: This class manages an independet-dependent pair. The value lists for both variable must have the same size.")
                        else:
                            raise ValueError("ERR05 Measurement - Import Value Error: This class manages an independent-dependent pair. Your list does not consist of two lists.")
                    else:
                        raise ValueError("ERR04 Measurement - Import Value Error: This class manages an independent-dependent pair. Your list does not contain two lists.")
                else:
                    raise ValueError("ERR03 Measurement - Import Value Error: This class manages an independent-dependent pair, but only one set of values is imported.")


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
