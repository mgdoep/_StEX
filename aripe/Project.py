from datetime import datetime
try:
    import matplotlib.pyplot as plt
    plt_import_success = True
except ImportError:
    plt_import_success = False

import os
path = os.getcwd()
import importlib
import numpy as np
Helper = importlib.import_module("Helper", path+"Helper.py")
Data = importlib.import_module("Data", path+"Data.py")
class Project:
    def __init__(self, path, **kwargs):
        self.misc = Helper.Helper()
        xmlinfo = self._getfromMetadata(path)
        self.Data = None
        if len(xmlinfo) > 0:
            self.name,  self.Institution = xmlinfo[0], xmlinfo[1]
            self.variables, self.outputs = xmlinfo[2], xmlinfo[3]
            self.ardProtocol, self.ardEProtocol, self.ardBaud = xmlinfo[4], xmlinfo[5], xmlinfo[6]
            self.ardSeperator, self.ardSleep = xmlinfo[7], xmlinfo[8]
            self.StandardFolder, self.TempFolder = xmlinfo[9], xmlinfo[10]
            self.calibrate = xmlinfo[11]
            self.control = xmlinfo[12]
            self.filters = xmlinfo[13]
            if len(self.variables) > 0:
                self.Data = Data.Data(self.variables)
        else:
            self.name, self.Institution = "", ""
            self.variables, self.outputs = None, None
            self.ardProtocol, self.ardEProtocol, self.ardBaud = None, None, None
            self.ardSeperator, self.ardSleep = None, None
            self.StandardFolder, self.TempFolder = "", ""
            self.calibrate = []
            self.control = None
            self.filters = xmlinfo[13]
        self.calibration_information = []
        self.tmpFileName = ""
        self.CreationDate = datetime.now
        self.Contributors = []

    """
    Needed by Data.createMetaXML, provides the necessary information as String
    """
    def __str__(self):
        rv = "<name>"+self.name+"</name>\n<contributors>\n"
        for c in self.Contributors:
            rv += "\t<person>"+str(c)+"</person>\n"
        rv += "\n</contributors>\n"
        rv += "<institution>"+self.Institution+"</institution>\n"
        rv += "<creationdate>"+str(self.CreationDate)+"</creationdate>\n"
        rv += "<projectfile>"+self.StandardFolder+self.tmpFileName+"</projectfile>"
        return rv

    def getTMPFileName(self):
        return self.StandardFolder + self.tmpFileName

    """
    _getfromMetadata
    returns: <List of variables>, <list of output options>, <string of arduino protocol>, <string of arduino protocol indicating error>
    """
    def _getfromMetadata(self, pfad):
        try:
            import xml.etree.ElementTree as ET
            tree = ET.parse(pfad)
            root = tree.getroot()
        except ImportError:
                return []
        except FileNotFoundError:
                return []
        if str(root.tag).lower() != "aripeproject":
            return []
        tree = ET.parse(pfad)
        root = tree.getroot()

        try:
            vars = root.find("variables").findall("variable")
        except AttributeError:
            return []

        ardFlag = False
        ardProtocol = None
        ardErrorProtocol = None
        ardSleep = 0
        pvariables = []
        for v in vars:
            vi = {}
            try:
                vi["name"] = v.find("name").text.strip()
                if "," in vi["name"]:
                    continue
                vi["live"] = False
                vi["method"] = v.find("name").attrib["type"].strip().lower()
                if vi["method"] == "arduino":
                    ardFlag = True
                    vi["ardCol"] = int(v.find("name").attrib["col"].strip().lower())
                if vi["method"] == "calculation":
                    vi["formula"] = v.find("name").attrib["formula"].strip()
                vi["unit"] = v.find("unit").text.strip()
                vi["unit"] = self._charstouni(vi["unit"])
                vi["errorrule"] = v.find("errorrule").text.strip()
            except AttributeError:
                continue
            except KeyError:
                continue
            try:
                vi["comment"] = v.find("comment").text
            except AttributeError:
                vi["comment"] = ""
    
            pvariables.append(vi)
        ardBaud = 9600
        ardSeperator = " "
        if ardFlag:
            try:
                ardProtocol = root.find("arduino").find("protocol").text
                ardErrorProtocol = root.find("arduino").find("protocolerror").text
                if root.find("arduino").find("baud").text.strip() != "":
                    ardBaud = int(root.find("arduino").find("baud").text)
                ardSeperator = root.find("arduino").find("seperator").text
                ardSleep = 0
                if root.find("arduino").find("sleep").text.strip() != "":
                    ardSleep = float(root.find("arduino").find("sleep").text.strip())
            except AttributeError:
                pass
            except KeyError:
                pass
            if ardProtocol is None:
                return []
        
        try:
            filters = root.find("filters").findall("filter")
        except AttributeError:
            filters = []
        filter_list = []
        for f in filters:
            fi = f.attrib
            varexist = False
            filexist = False
            if "name" in fi.keys() and len(fi["name"].strip()) > 0:
                fi["name"] = fi["name"].strip()
                if "," in fi["name"]:
                    continue
                for ef in filter_list:
                    if ef["name"] == fi["name"]:
                        filexist = True
                vn = f.text.strip()
                if "," in vn:
                    fi["variable"] = fi["variable"].split(",")
                    lvl = len(fi["variable"])
                    ivn = 0
                    while ivn < lvl:
                        fi["variable"][ivn] = fi["variable"][ivn].strip()
                        if len(fi["variable"][ivn]) > 0:
                            for v in pvariables:
                                if fi["variable"][ivn] == v["name"]:
                                    varexist = True
                            ivn += 1
                        else:
                            del fi["variable"][ivn]
                            lvl -= 1
                    if len(fi["variable"]) < 1:
                        varexist = True
                else:
                    fi["variable"] = vn
                for v in pvariables:
                    if vn == v["name"]:
                        varexist = True
            else:
                continue
            if not varexist or filexist:
                continue
            fi["name"] = fi["name"].strip()
            if "type" not in fi.keys() or fi["type"].lower().strip() not in ["crop", "croponce", "number", "step"]:
                continue
            fi["type"] = fi["type"].lower().strip()
            if "value" not in fi.keys():
                continue
    
            if "(" in fi["value"]:
                begin = None
                end = None
                try:
                    begin = self.misc.str_to_float(fi["value"].split("(")[1].split(",")[0])
                    end = self.misc.str_to_float(fi["value"].split(",")[1].split(")")[0])
                except:
                    continue
                if begin is None or end is None or "crop" not in fi["type"]:
                    continue
                else:
                    fi["start"] = begin
                    fi["ende"] = end
                    del fi["value"]
            else:
                fi["value"] = self.misc.str_to_float(fi["value"])
                if fi["value"] is None or fi["type"] not in ["number", "step"]:
                    continue
            if "basedon" in fi.keys():
                fi["basedon"] = fi["basedon"].strip()
                filexist = False
                for ef in filter_list:
                    if ef["name"] == fi["basedon"]:
                        filexist = True
                if not filexist:
                    continue
            filter_list.append(fi)
        
        outputs_xml = None
        try:
            outputs_xml = root.find("outputs").findall("output")
        except AttributeError:
            pvariables = []
            return [None]*13
        if outputs_xml is not None:
            outputs = []
            for o in outputs_xml:
                ol = o.attrib
                
                try:
                    ol["type"] = ol["type"].lower().strip()
                except:
                    continue
                
                textsset = False
                
                if "text" not in ol.keys():
                    types = ["xlsx", "csv", "table", "list", "plot"]
                    texts = ["XLSX-Datei", "CSV-Datei", "Tabelle", "Liste", "Diagramm"]
                    for i in range(len(types)):
                        if ol["type"] == types[i]:
                            ol["text"] = texts[i]
                    textsset = True
                
                try:
                    if ol["type"].strip() in ["xlsx", "csv", "table", "list"]:
                        col_xml = o.findall("column")
                        collist = []
                        for c in col_xml:
                            for pv in pvariables:
                                if c.text.strip() != pv["name"]:
                                    continue
                            collist.append(c.text.strip())
                        ol["columns"] = collist
                    
                    if "eca" not in ol.keys():
                        ol["error_column_appendix"] = "_Fehler"
                    else:
                        ol["error_column_appendix"] = ol["eca"]
                        del ol["eca"]
                    
                    if "seperator" not in ol.keys():
                        ol["seperator"] = ","
                        
                    if "error" in ol.keys():
                        ol["error"] = ol["error"].lower().strip() == "true"
                    else:
                        ol["error"] = False

                    if "save" in ol.keys():
                        ol["save"] = ol["save"].lower().strip() == "true"
                    else:
                        ol["save"] = False
                    
                    if "sigdit" in ol.keys():
                        try:
                            ol["sigdit"] = int(ol["sigdit"])
                        except ValueError:
                            del ol["sigdit"]
                    
                    if "round" in ol.keys():
                        try:
                            ol["round"] = int(ol["round"])
                        except ValueError:
                            del ol["round"]
                    
                    if ol["type"].strip() in ["plot"]:
                        axislist = {"x": None, "xopt": None, "yopt": None,"y":None}
                        axis_xml = o.findall("axis")
                        foundxy = [False, False]
                        for a in axis_xml:
                            ae = a.attrib
                            var = a.text.strip()
                            found = False
                            for pv in pvariables:
                                if var == pv["name"]:
                                    found = True
                            if not found:
                                print("Variable", var, "nicht in definiert.")
                                continue
                            if "type" not in ae.keys():
                                pass
                            else:
                                ae["type"] = ae["type"].strip().lower()
                                if (ae["type"] == "x" and foundxy[0]) or (ae["type"] == "y" and foundxy[1]):
                                    pass
                                else:
                                    if ae["type"] not in ["x", "y"]:
                                        pass
                                    elif ae["type"] == "x":
                                        foundxy[0] = True
                                        axislist["x"] = var
                                        del ae["type"]
                                        axislist["xopt"] = ae
                                    else:
                                        foundxy[1] = True
                                        axislist["y"] = var
                                        del ae["type"]
                                        axislist["yopt"] = ae
                                        
                        if axislist["x"] is None or axislist["y"] is None:
                            continue
                        ol["axis"] = axislist
                        try:
                            ol["plotoptions"] = o.find("option").text.strip()
                        except:
                            ol["plotoptions"] = "ko"
                        
                        try:
                            fit_xml = o.find("fit")
                            fitinfo = fit_xml.attrib
                            if "type" not in fitinfo:
                                continue
                            fitinfo["type"] = fitinfo["type"].lower().strip()
                            if textsset:
                                ol["text"] += " mit Kurve"
                            if "showparameter" in fitinfo.keys():
                                fitinfo["showparameter"] = "true" in fitinfo["showparameter"].lower()
                            else:
                                fitinfo["showparameter"] = False
                            if "degree" in fitinfo.keys():
                                try:
                                    fitinfo["degree"] = int(fitinfo["degree"])
                                except:
                                    fitinfo["degree"] = 2
                            try:
                                fitinfo["line"] = fit_xml.find("line").text.strip()
                            except:
                                fitinfo["line"] = "r-"
                            try:
                                fitinfo["envelop"] = fit_xml.find("envelop").text.strip()
                            except:
                                fitinfo["envelop"] = None
                            ol["fit"] = fitinfo
                        except:
                            pass
                        
                    if "filter" in ol.keys():
                        ofl = ol["filter"].split(",")
                        lofl = len(ofl)
                        i = 0
                        while i < lofl:
                            ofl[i] = ofl[i].strip()
                            filnotfound = True
                            for f in filter_list:
                                if ofl[i] == f["name"]:
                                    filnotfound = False
                                
                            if filnotfound:
                                del ofl[i]
                                lofl -= 1
                            else:
                                i += 1
                        ol["filter"] = ofl
                except:
                    continue
                outputs.append(ol)
            
            name = ""
            try:
                name = root.find("name").text
            except AttributeError:
                pass
            tempFolder=""
            standardFolder = ""
            try:
                tempFolder = root.find("tfolder").text
                standardFolder = root.find("sfolder").text
            except:
                pass
            institution = ""
            try:
                institution = root.find("institution").text
            except:
                pass
        
        calibrate_for = []
        try:
            calvars = root.find("calibration").findall("variable")
            for c in calvars:
                cvi = c.attrib
                cvi["name"] = c.text.strip()
                cvi["setto"] = self.misc.str_to_float(cvi["setto"])
                if cvi["setto"] is None:
                    print("Kalibrierung konnte für", cvi["name"],"nicht definiert werden. Der angegebene Wert für \"setto\" konnte nicht in Zahl konvertiert werden.")
                if "getvalue" not in cvi.keys():
                    cvi["getvalue"] = True
                else:
                    cvi["getvalue"] = "man" in cvi["getvalue"].lower().strip()
                calibrate_for.append(cvi)
        except:
            pass
        
        try:
            lv = root.find("live").findall("value")
            for lvi in lv:
                lvt = lvi.text.strip()
                for i in range(len(pvariables)):
                    if lvt == pvariables[i]["name"] and pvariables[i]["method"] == "arduino":
                        pvariables[i]["live"] = True
        except:
            pass
        
        startstop = {"start_button": True, "start_countdown": False, "start_delay": 0,
                     "stop_button": True, "stop_after": False, "stop_variable": None, "stop_time": 0, "stop_value": None}
        try:
            st = root.find("start")
            if st.attrib["type"].strip().lower() == "countdown":
                startstop["start_button"] = False
                startstop["start_countdown"] = True
            if st.text.strip() != "":
                try:
                    startstop["start_delay"] = int(st.text.strip())
                except:
                    pass
        except:
            pass
        
        if startstop["start_countdown"] and (type(startstop["start_delay"]) is not int or startstop["start_delay"] < 1):
            startstop["start_delay"] = 5
        
        try:
            st = root.find("stop")
            if st.attrib["type"].strip().lower() == "after":
                startstop["stop_after"] = True
                startstop["stop_button"] = False
                startstop["stop_time"] = int(st.text.strip())
            if st.attrib["type"].strip().lower() == "value":
                try:
                    var = st.attrib["variable"].strip()
                    possible = False
                    for v in pvariables:
                        if v["name"] == var and v["type"] == "arduino":
                            possible = True
                    if possible:
                        startstop["stop_value"] = self.misc.str_to_float(st.text)
                        if startstop["stop_value"] is not None:
                            startstop["stop_variable"] = var
                            startstop["stop_button"] = False
                except:
                    pass
        except:
            pass
        
        
        
        rv = [name, institution, pvariables, outputs, ardProtocol, ardErrorProtocol, ardBaud, ardSeperator, ardSleep, standardFolder, tempFolder, calibrate_for, startstop, filter_list]
        return rv
    
    def _charstouni(self, s):
        rv = ""
        unicode = {"-": "\u207b", "1": "\u00b9", "2": "\u00b2", "3": "\u00b3", "4": "\u2074", "5": "\u2075", "6": "\u2076",
                   "7": "\u2077", "8": "\u2078", "9": "\u2079", "*": "\u00b7"}
        for c in s:
            if c in unicode.keys():
                rv += unicode[c]
            else:
                rv += c
        return rv

    def addConributor(self, name):
        self.Contributors.append(name)
    
    def succLoad(self):
        return self.variables is not None and self.outputs is not None
    
    def usesArduino(self):
        return self.ardProtocol is not None
    
    def getName(self):
        return self.name
    
    def getBaud(self):
        if self.ardBaud is None:
            return 0
        return self.ardBaud
    
    def getOutputs(self):
        if self.outputs is None:
            return []
        return self.outputs
    
    def getNumberOfVariables(self):
        return len(self.variables)
    
    def calibrationFor(self, mode = "all"):
        if mode == "all" and len(self.calibrate) > 0:
            return self.calibrate
        elif len(self.calibrate) > 0:
            rv = []
            for c in self.calibrate:
                if c["getvalue"]:
                    rv.append(c)
            return rv
        return []
    
    def getArduinoValues(self):
        rv = []
        rv2 = False
        for v in self.variables:
            if v["method"] == "arduino":
                rv.append({"name": v["name"], "unit": v["unit"], "ardCol": v["ardCol"], "live": v["live"]})
                if v["live"]:
                    rv2 = True
        return rv, rv2
    """
    setCalibration
    saves the calibration information
    Parameter variable is dict with the following keys:
    - name ... variable name
    - cvalue ... calibration value
    """
    def setCalibration(self, variable):
        for i in range(len(self.calibrate)):
            if variable["name"] == self.calibrate[i]["name"]:
                self.calibrate[i]["cvalue"] = self.misc.str_to_float(variable["cvalue"])
    
    
    
    def getVariables(self):
        return self.Data.provide_compact_variable_information()
    
    def getArduinoColumn(self, name):
        for v in self.variables:
            if v["name"] == name and v["method"] == "arduino":
                return v["ardCol"]
        return -1
    
    def getStopVariableCol(self):
        if self.control["stop_button"] or self.control["stop_after"]:
            return -1, -1
        return self.getArduinoColumn(self.control["stop_variable"]), self.control["stop_value"]
    
    def ManualArduinoVariables(self):
        rv = {"manual": [], "arduino": []}
        live = 0
        for v in self.variables:
            if v["method"] == "manual":
                ita = {"name": v["name"], "unit": v["unit"], "getErrorValue": False}
                for v2 in self.getVariables():
                    if v["name"] == v2["name"] and v2["errorrule"] is None and v["errorrule"].lower().strip() != "none":
                        ita["getErrorValue"] = True
                rv["manual"].append(ita)
                
            elif v["method"] == "arduino":
                rv["arduino"].append({"name": v["name"], "unit": v["unit"], "live": v["live"], "ardCol": v["ardCol"]})
                if v["live"]:
                    live += 1
        return rv, len(rv["manual"]) > 0, live
    
    def addManualValues(self, vars):
        self.Data.addValues(vars)
    
    def applyFilters(self):
        for f in self.filters:
            bo = None
            if "basedon" in f.keys():
                bo = f["basedon"]
            if "crop" in f["type"]:
                self.Data.cropDataSet(f["start"], f["ende"], TimeVariable=f["variable"], name=f["name"], once=f["type"]=="croponce")
            elif f["type"] == "number":
                self.Data.applyNumberFilter(f["name"], f["value"], f["variable"], basedon=bo)
            elif f["type"] == "step":
                self.Data.applyStepFilter(f["name"], f["value"], f["variable"], basedon=bo)
        
    def MeasurementPostProcessing(self, valTrans=True):
        if valTrans:
            self.Data.valueTransformation()
        self.calibrateVariables()
        for v in self.variables:
            if v["method"] == "calculation":
                self.Data.calculateVariable(v["name"], v["formula"])
        self.applyFilters()

    def importRAW(self, filename):
        vl = []
        for v in self.variables:
            if v["method"] == "arduino":
                vl.append((v["name"], v["ardCol"]))
        return self.Data.getValuesFromRawFile(filename, vl, self.ardProtocol)
    
    def _getSigDitRoundTo(self, index):
        sigdit, roundto = -1, -1
        if "sigdit" in self.outputs[index].keys():
            sigdit = self.outputs[index]["sigdit"]
        if "round" in self.outputs[index].keys():
            roundto = self.outputs[index]["round"]
        return sigdit, roundto
    
    def _getSmoothFileNameForExport(self, filename, ext):
        if "."+ext not in filename:
            if "." in filename:
                fns = filename.split(".")
                del fns[-1]
                filename = ""
                filename = filename.join(fns)
            filename = filename + "." + ext
        return filename
        
    def exportToFile(self, filename, outputinfo_index):
        sigdit, roundto = self._getSigDitRoundTo(outputinfo_index)
        oi = self.outputs[outputinfo_index]
        if oi["type"] == "xlsx":
            try:
                import xlsxwriter
            except:
                return False, 0
        columns = []
        lengths = []
        elengths = []
        for i in range(len(self.outputs[outputinfo_index]["columns"])):
            try:
                vals = self.Data.returnValue(self.outputs[outputinfo_index]["columns"][i], round_to=roundto, significant_digits=sigdit)
                vals["values"] = [str(x) for x in vals["values"]]
                vals["error"] = [str(x) for x in vals["error"]]
                columns.append(vals)
                lengths.append(len(columns[-1]["values"]))
                elengths.append(len(columns[-1]["error"]))
            except:
                return False, 0
        anzahl = len(columns)
        max_length = max(lengths)
        if anzahl < 1:
            return False
        
        if oi["type"]=="xlsx":
            filename = self._getSmoothFileNameForExport(filename, "xlsx")
        if oi["type"]=="cvs":
            filename = self._getSmoothFileNameForExport(filename, "csv")
        
        if oi["type"]=="xlsx":
            wb = xlsxwriter.Workbook(filename)
            sheet = wb.add_worksheet(self.name)
            error_shift = 0
            if oi["error"]:
                error_shift = 1
            for col in range(anzahl):
                colindex = col
                if error_shift > 0:
                    colindex = 2*col
                sheet.write(0, colindex, columns[col]["name"]+"["+columns[col]["unit"]+"]")
                if error_shift > 0:
                    sheet.write(0, colindex + 1, columns[col]["name"]+oi["error_column_appendix"])
                for j in range(lengths[col]):
                    sheet.write(j+1, colindex, columns[col]["values"][j])
                    if error_shift > 0 and j < elengths[col]:
                        sheet.write(j+1, colindex+1, columns[col]["error"][j])
            wb.close()
            return True, filename
        if oi["type"] == "csv":
            file = open(filename, "w")
            for i in range(anzahl):
                file.write(columns[i]["name"]+"["+columns[i]["unit"]+"]")
                if oi["error"] or (i < anzahl - 1):
                    file.write(oi["seperator"])
                if oi["error"]:
                    file.write(columns[i]["name"]+oi["error_column_appendix"])
                    if (i < anzahl - 1):
                        file.write(oi["seperator"])
                if i == anzahl - 1:
                    file.write("\n")
            for i in range(max_length):
                for j in range(anzahl):
                    if i < lengths[j]:
                        file.write(columns[j]["values"][i])
                    if oi["error"]:
                        file.write(oi["seperator"]+columns[j]["error"][i])
                    if j < anzahl-1:
                        file.write(oi["seperator"])
                file.write("\n")
            file.close()
            return True, filename
        return False, 0
    
    def _valuesForGUI(self, outputinfo_index):
        sigdit, roundto = self._getSigDitRoundTo(outputinfo_index)
        rv = {"error": self.outputs[outputinfo_index]["error"], "col": []}
        fan = "filter" in self.outputs[outputinfo_index].keys()
        for c in self.outputs[outputinfo_index]["columns"]:
            if fan:
                rv["col"].append(self.Data.returnValue(c, round_to=roundto, significant_digits=sigdit, filters=self.outputs[outputinfo_index]["filter"]))
            else:
                rv["col"].append(self.Data.returnValue(c, round_to=roundto, significant_digits=sigdit))
        return rv
    
    def valuesForGUIList(self, outputindex):
        c = {"pm": " \u00b1 ", ".": "\u00b7", "n": "\n"}
        info = self._valuesForGUI(outputindex)
        a = len(info["col"])
        for i in range(a):
            info["col"][i]["values"] = [str(x) for x in info["col"][i]["values"]]
            info["col"][i]["error"] = [str(x) for x in info["col"][i]["error"]]
        text = "<ul style=\"list-style-type: circle;\">\n"
        #text = ""
        l = len(info["col"][0]["values"])
        f = info["error"]
        for i in range(l):
            for j in range(a):
                #text += info["col"][j]["name"] + " = "
                if j == 0:
                    text += "<li>&#x2022; "
                text += info["col"][j]["name"] + " = "
                if f:
                    text += "("
                text += info["col"][j]["values"][i] + " "
                if f:
                    text += c["pm"] + " " + info["col"][j]["error"] + ") "
                text += info["col"][j]["unit"] + " ;"
            if j == a-1:
                text += "</li>\n"
        text += "</ul>"
        return text
    
    def GUITableMatrix(self, outputindex):
        info = self._valuesForGUI(outputindex)
        a = len(info["col"])
        l = len(info["col"][0]["values"])
        for i in range(a):
            info["col"][i]["values"] = [str(x) for x in info["col"][i]["values"]]
            info["col"][i]["error"] = [str(x) for x in info["col"][i]["error"]]
        f = info["error"]
        eca = self.outputs[outputindex]["error_column_appendix"]
        rv = []
        z = []
        for i in range(a):
            z.append(info["col"][i]["name"] + "\u00b7(" + info["col"][i]["unit"]+")\u207b\u00b9")
            if f:
                z.append(info["col"][i]["name"] + eca)
        rv.append(z)
        for i in range(l):
            z = []
            for j in range(a):
                z.append(info["col"][j]["values"][i])
                if f:
                    z.append(info["col"][j]["error"][i])
            rv.append(z)
        return rv
        
        pass
    
    def getReturnData(self, var, filters):
        return self.Data.returnValue(var, filters=filters)
    
    def getfitparam(self, x_values, y_values, outputindex):
        fitinfo = None
        oinfo = self.outputs[outputindex]
        if oinfo["fit"]["type"] == "poly":
            fitinfo = self.Data.fit_poly(x_values, y_values, oinfo["fit"]["degree"])
        if oinfo["fit"]["type"] == "osci":
            fitinfo = self.Data.fit_osci(x_values, y_values)
        if oinfo["fit"]["type"] == "damped-osci":
            fitinfo = self.Data.fit_damped_osci(x_values, y_values)
        if "exp" in oinfo["fit"]["type"]:
            dec = "damped" in oinfo["fit"]["type"]
            fitinfo = self.Data.fit_exp(x_values, y_values, decay=dec)
        sd, rt = None, None
        if "sigdit" in oinfo.keys():
            sd = oinfo["sigdit"]
        elif "round" in oinfo.keys():
            rt = oinfo["round"]
        if sd is not None or rt is not None:
            for k in fitinfo.keys():
                if str(k) not in ["xfit", "yfit", "envel1", "envel2"]:
                    if type(fitinfo[k]) is np.ndarray:
                        fitinfo[k] = fitinfo[k].tolist()
                    if type(fitinfo[k]) is list:
                        for i in range(len(fitinfo[k])):
                            fitinfo[k][i] = self.misc.rounddigits(fitinfo[k][i], rt, sd)
                    else:
                        fitinfo[k] = self.misc.rounddigits(fitinfo[k], rt, sd)
        return fitinfo
    
    def var_unit(self, varname):
        return self.Data.unit[varname]
    
    def calibrateVariables(self):
        for c in self.calibrate:
            if "cvalue" in c.keys():
                if c["getvalue"] and c["cvalue"] is None:
                    print("Calibration für Variable", c["name"], "nicht möglich! Ausgangswert ist <None>!")
                    continue
                self.Data.calibrateVariable(c["name"], c["setto"], init_value=c["cvalue"])
            else:
                self.Data.calibrateVariable(c["name"], c["setto"], init_value=None)

    
    def getFitText(self, fitinfo, fittype, x_name, y_name, x_unit, y_unit):
        c = {"pm": " \u00b1 ", "sm": "\u207b", "s1": "\u00b9", "s2": "\u00b2", "s3": "\u00b3", "s4": "\u2074",
             "w": "\u03c9", "p": "\u03c6", "d": "\u03b4", "D": "\u0394", "n": "\n", ".": "\u00b7",
             ".(": "\u00b7(", ")m": ")\u207b", "y0m": " + " + y_name+"\u2080 mit: \n", "yd": "\u0177", "y0": y_name+"\u2080"}
        
        fittext = y_name + " = "
        
        if fittype == "poly":
            fitinfo["values"] = [str(x) for x in fitinfo["values"]]
            fitinfo["errors"] = [str(x) for x in fitinfo["errors"]]
            deg = len(fitinfo["values"]) - 1
            if deg == 1:
                fittext += "m\u00b7" + x_name + c["y0m"]
                fittext += "m = (" + fitinfo["values"][0] + c["pm"] + fitinfo["errors"][0] + ") " + y_unit + c[".("] + x_unit + c[")m"] + c["s1"] + c["n"]
                fittext += c["y0"] +" = (" + fitinfo["values"][1] + c["pm"] + fitinfo["errors"][1] + ") " + y_unit
            elif deg == 2:
                fittext += "a"+c["."]+x_name+c["s2"]+" + b"+c["."]+x_name+ c["y0m"]
                fittext += "a = (" + fitinfo["values"][0] + c["pm"] + fitinfo["errors"][0] + ") " + y_unit + c[".("] + x_unit + c[")m"] + c["s2"] + c["n"]
                fittext += "b = (" + fitinfo["values"][1] + c["pm"] + fitinfo["errors"][1] + ") " + y_unit + c[
                    ".("] + x_unit + c[")m"] + c["s1"] + c["n"]
                fittext += c["y0"] +" =  (" + fitinfo["values"][2] + c["pm"] + fitinfo["errors"][2] + ") " + y_unit
            elif deg == 3:
                fittext += "a" + c["."] + x_name + c["s3"] + " + b" + c["."] + x_name + c["s2"] + " + c" + c["."] + x_name + c["y0m"]
                fittext += "a = (" + fitinfo["values"][0] + c["pm"] + fitinfo["errors"][0] + ") " + y_unit + c[
                    ".("] + x_unit + c[")m"] + c["s3"] + c["n"]
                fittext += "b = (" + fitinfo["values"][1] + c["pm"] + fitinfo["errors"][1] + ") " + y_unit + c[
                    ".("] + x_unit + c[")m"] + c["s2"] + c["n"]
                fittext += "c = (" + fitinfo["values"][2] + c["pm"] + fitinfo["errors"][2] + ") " + y_unit + c[
                    ".("] + x_unit + c[")m"] + c["s1"] + c["n"]
                fittext += c["y0"] +" =  (" + fitinfo["values"][3] + c["pm"] + fitinfo["errors"][2] + ") " + y_unit
            else:
                fittext += "a" + c["."] + x_name + c["s4"] + " + b" + c["."] + x_name + c["s3"]
                " + c" + c["."] + x_name + c["s2"] + " + d " + c["."] + x_name + c["y0m"]
                fittext += "a = (" + fitinfo["values"][0] + c["pm"] + fitinfo["errors"][0] + ") " + y_unit + c[
                    ".("] + x_unit + c[")m"] + c["s4"] + c["n"]
                fittext += "b = (" + fitinfo["values"][1] + c["pm"] + fitinfo["errors"][1] + ") " + y_unit + c[
                    ".("] + x_unit + c[")m"] + c["s3"] + c["n"]
                fittext += "c = (" + fitinfo["values"][2] + c["pm"] + fitinfo["errors"][2] + ") " + y_unit + c[
                    ".("] + x_unit + c[")m"] + c["s2"] + c["n"]
                fittext += "d = (" + fitinfo["values"][3] + c["pm"] + fitinfo["errors"][3] + ") " + y_unit + c[
                    ".("] + x_unit + c[")m"] + c["s1"] + c["n"]
                fittext += c["y0"] +" = (" + fitinfo["values"][4] + c["pm"] + fitinfo["errors"][4] + ") " + y_unit
        if fittype == "osci":
            for k in fitinfo.keys():
                fitinfo[k] = str(fitinfo[k])
            fittext += c["yd"] + c["."] + "sin("+c["w"] + c["."] + x_name + " + " + c["p"] + ")" + c["y0m"]
            fittext += c["yd"] + " = (" + fitinfo["a"] + c["pm"] + fitinfo["ae"] + ") " + y_unit + c["n"]
            fittext += c["w"] + " = (" + fitinfo["w"] + c["pm"] + fitinfo["we"] + ") rad" + c[".("] + x_unit + c[")m"]+ c["s1"] + c["n"]
            fittext += c["p"] + " = (" + fitinfo["p"] + c["pm"] + fitinfo["pe"] + ") rad"
            fittext += c["y0"] + " = (" + fitinfo["o"] + c["pm"] + fitinfo["oe"] + ") "+y_unit
        
        if fittype == "damped-osci":
            for k in fitinfo.keys():
                fitinfo[k] = str(fitinfo[k])
            fittext += c["yd"] + c["."] + "exp("+ c["d"] + c["."] + x_name +") " + c["."] +" sin(" +c["w"] + c["."] + x_name + " + " + c["p"] + ")" + c["y0m"]
            fittext += c["yd"] + " = (" + fitinfo["a"] + c["pm"] + fitinfo["ae"] + ") " + y_unit + c["n"]
            fittext += c["d"] + " = (" + fitinfo["d"] + c["pm"] + fitinfo["de"] + ") (" + x_unit + c[")m"] + \
                       c["s1"] + c["n"]
            fittext += c["w"] + " = (" + fitinfo["w"] + c["pm"] + fitinfo["we"] + ") rad" + c[".("] + x_unit + c[")m"]+ c["s1"] + c["n"]
            fittext += c["p"] + " = (" + fitinfo["p"] + c["pm"] + fitinfo["pe"] + ") rad"
            fittext += c["y0"] + " = (" + fitinfo["o"] + c["pm"] + fitinfo["oe"] + ") "+y_unit
        return fittext
    
    def printData(self):
        print(self.Data.values)
    