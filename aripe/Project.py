from datetime import datetime
import os
path = os.getcwd()
import importlib
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

        filters = root.find("filters").findall("filter")
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
            return []
        if outputs_xml is not None:
            outputs = []
            for o in outputs_xml:
                ol = o.attrib
                try:
                    if ol["type"].strip() in ["xls", "csv", "table", "list"]:
                        col_xml = o.findall("column")
                        collist = []
                        for c in col_xml:
                            if c.text.strip() not in pvariables:
                                continue
                            collist.append(c.text.strip())
                        ol["columns"] = collist
                    
                    if "error_column_appendix" not in ol.keys():
                        ol["error_column_appendix"] = "_Fehler"
                    
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
                        axislist = []
                        axis_xml = o.findall("axis")
                        foundxy = [False, False]
                        for a in axis_xml:
                            ae = a.attrib
                            var = a.text.strip()
                            if var not in pvariables:
                                continue
                            ae["var"] = var
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
                                        axislist.append(ae)
                                    else:
                                        foundxy[1] = True
                                        axislist.append(ae)
                        if len(axislist) < 2:
                            continue
                        ol["axis"] = axislist
                        try:
                            fit_xml = o.find("fit")
                            fitinfo = fit_xml.attrib
                            fitinfo["options"] = fit_xml.text.strip()
                            ol["fit"] = fitinfo
                        except:
                            pass
                        
                    if "filter" in ol.keys():
                        ofl = ol["filter"].split(",")
                        lofl = len(ofl)
                        i = 0
                        while i < lofl:
                            ofl[i] = ofl[i].strip()
                            if ofl[i] not in filter_list:
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
        
        startstop = {"start_button": True, "start_countdown": False, "start_delay": 0, "stop_button": True, "stop_after": False, "stop_time": 0}
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
        except:
            pass
        
        
        
        rv = [name, institution, pvariables, outputs, ardProtocol, ardErrorProtocol, ardBaud, ardSeperator, ardSleep, standardFolder, tempFolder, calibrate_for, startstop, filter_list]
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
    
    def calibrationFor(self):
        if len(self.calibrate) > 0:
            return self.calibrate
        else:
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
    
    def ManualArduinoVariables(self):
        rv = {"manual": [], "arduino": []}
        live = 0
        for v in self.variables:
            if v["method"] == "manual":
                ita = {"name": v["name"], "unit": v["unit"], "getErrorValue": False}
                for v2 in self.getVariables():
                    if v["name"] == v2["name"] and v2["errorrule"] is None:
                        ita["getErrorValue"] = True
                rv["manual"].append(ita)
                
            elif v["method"] == "arduino":
                rv["arduino"].append({"name": v["name"], "unit": v["unit"], "live": v["live"], "ardCol": v["ardCol"]})
                if v["live"]:
                    live += 1
        return rv, len(rv["manual"]) > 0, live
    
    def addManualValues(self, vars):
        self.Data.addValues(vars)
        
    def MeasurementPostProcessing(self, valTrans=True):
        if valTrans:
            self.Data.valueTransformation()
        for v in self.variables:
            if v["method"] == "calculation":
                self.Data.calculateVariable(v["name"], v["formula"])
    
    def importRAW(self, filename):
        vl = []
        for v in self.variables:
            if v["method"] == "arduino":
                vl.append((v["name"], v["ardCol"]))
        return self.Data.getValuesFromRawFile(filename, vl)
    
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
        if oi["type"] == "xls":
            try:
                import xlsxwriter
            except:
                return False
        columns = []
        lengths = []
        elengths = []
        for i in range(len(self.outputs[outputinfo_index]["columns"])):
            try:
                columns.append(self.Data.returnValues(self.outputs[outputinfo_index][i], round_to=roundto, significant_digits=sigdit))
                lengths.append(len(columns[-1]["values"]))
                elengths.append(len(columns[-1]["error"]))
            except:
                pass
        anzahl = len(columns)
        max_length = max(lengths)
        if anzahl < 1:
            return False
        
        if oi["type"]=="xls":
            filename = self._getSmoothFileNameForExport(filename, "xlsx")
        if oi["type"]=="cvs":
            filename = self._getSmoothFileNameForExport(filename, "csv")
        
        if oi["type"]=="xls":
            wb = xlsxwriter.Workbook(filename)
            sheet = wb.add_worksheet(self.name)
            for col in range(anzahl):
                colindex = col
                error_shift = 0
                if oi["error"]:
                    colindex = 2*col
                    error_shift = 1
                sheet.write(0, colindex, columns[i]["name"]+"["+columns[i]["unit"]+"]")
                if error_shift > 0:
                    sheet.write(0, colindex + 1, columns[i]["name"]+oi["error_column_appendix"])
                for j in range(lengths[col]):
                    sheet.write(j+1, colindex, columns[i]["values"][j])
                    if error_shift > 0 and j < elengths[col]:
                        sheet.write(j+1, colindex+1, columns[i]["error"][j])
            wb.close()
            return True
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
            file.close()
            return True
        return False
    
    def valuesForGUI(self, outputinfo_index):
        pass #TODO: Implement output for GUI
    
    def plot(self, filename, outputinfo_index):
        pass #TODO: Implement plotting
    
    def printData(self):
        print(self.Data.values)