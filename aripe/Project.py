class Project:
    def __init__(self, **kwargs):
        defdict = None
        self.Messreihe = None
        if "definition" in kwargs:
            defdict = kwargs["definition"]
        if "fromMetadata" in kwargs:
            defdict=self._getfromMetadata(kwargs["fromMetadata"])
            self.Messreihe = [kwargs["DataContainer"]]
        self.name = ""
        self.tmpFileName = ""
        self.StandardFolder = ""
        self.CreationDate = ""
        self.Contributors = []
        self.Institution = ""

    """
    Needed by Data.createMetaXML, provides the necessary information as String
    """
    def __str__(self):
        rv = "<name>"+self.name+"</name>\n<contributors>\n"
        for c in self.Contributors:
            rv += "\t<person>"+c+"</person>\n"
        rv += "\n</contributors>\n"
        rv += "<institution>"+self.Institution+"</institution>\n"
        rv += "<creationdate>"+str(self.CreationDate)+"</creationdate>\n"
        rv += "<projectfile>"+self.StandardFolder+self.tmpFileName+"</projectfile>"
        return rv

    def getTMPFileName(self):
        return self.StandardFolder + self.tmpFileName

    def _getfromMetadata(self, path_to_project_xml):