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
            self.StandardFolder, self.TempFolder = xmlinfo[7], xmlinfo[8]
            self.calibrate = xmlinfo[9]
            if len(self.variables) > 0:
                self.Data = Data.Data(self.variables)
        else:
            self.name, self.Institution = "", ""
            self.variables, self.outputs = None, None
            self.ardProtocol, self.ardEProtocol, self.ardBaud = None, None, None
            self.StandardFolder, self.TempFolder = "", ""
            self.calibrate = []
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
    def _getfromMetadata(self, path):
        try:
            import xml.etree.ElementTree as ET
            tree = ET.parse(path)
            root = tree.getroot()
        except ImportError:
                return []
        except FileNotFoundError:
                return []
        if str(root.tag).lower() != "aripeproject":
            return []
        tree = ET.parse("project-metadata.xml")
        root = tree.getroot()

        try:
            vars = root.find("variables").findall("variable")
        except AttributeError:
            return []

        ardFlag = False
        ardProtocol = None
        ardErrorProtocol = None
        pvariables = []
        for v in vars:
            vi = {}
            try:
                vi["name"] = v.find("name").text.strip()
                vi["method"] = v.find("name").attrib["type"].strip().lower()
                if vi["method"] == "arduino":
                    ardFlag = True
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
        ardBaud = 0
        if ardFlag:
            try:
                ardProtocol = root.find("arduino").attrib["protocol"]
                ardErrorProtocol = root.find("arduino").attrib["rotocolerror"]
                ardBaud = int(root.find("arduino").attrib["baud"])
                
            except AttributeError:
                pass
            except KeyError:
                pass
            if ardProtocol is None:
                return []
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
                            collist.append(c.text)
                        ol["columns"] = collist
                    if ol["type"].strip() in ["plot"]:
                        axislist = []
                        axis_xml = o.findall("axis")
                        for a in axis_xml:
                            ae = a.attrib
                            ae["var"] = a.text.strip()
                            axislist.append(ae)
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
                        i = 0
                        while i < len(ofl):
                            ofl[i] = ofl[i].strip()
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
        
        rv = [name, institution, pvariables, outputs, ardProtocol, ardErrorProtocol, ardBaud, tempFolder, standardFolder, calibrate_for]
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
    
    def setCalibration(self, variable):
        if type(variable) is list:
            for v in variable:
                self.calibration_information.append(v)
        else:
            self.calibration_information.append(variable)
    
    def getVariables(self):
        return self.Data.provide_compact_variable_information()