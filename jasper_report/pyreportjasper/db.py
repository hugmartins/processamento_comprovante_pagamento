import jpype
import jpype.imports

from jasper_report.pyreportjasper.config import Config


class Db:
    Connection = None
    DriverManager = None
    Class = None
    JRXmlDataSource = None
    JsonDataSource = None
    JsonQLDataSource = None

    def __init__(self):
        self.Connection = jpype.JPackage('java').sql.Connection
        self.DriverManager = jpype.JPackage('java').sql.DriverManager
        self.Class = jpype.JPackage('java').lang.Class
        self.JRCsvDataSource = jpype.JPackage('net').sf.jasperreports.engine.data.JRCsvDataSource
        self.JRXmlDataSource = jpype.JPackage('net').sf.jasperreports.engine.data.JRXmlDataSource
        self.JsonDataSource = jpype.JPackage('net').sf.jasperreports.engine.data.JsonDataSource
        self.JsonQLDataSource = jpype.JPackage('net').sf.jasperreports.engine.data.JsonQLDataSource
        self.JRLoader = jpype.JPackage('net').sf.jasperreports.engine.util.JRLoader
        self.StringEscapeUtils = jpype.JPackage('org').apache.commons.lang.StringEscapeUtils
        self.File = jpype.JPackage('java').io.File

    def get_csv_datasource(self, config: Config):
        ds = self.JRCsvDataSource(self.get_data_file_input_stream(config), config.csvCharset)
        ds.setUseFirstRowAsHeader(jpype.JObject(jpype.JBoolean(config.csvFirstRow)))
        if config.csvFirstRow:
            ds.setColumnNames(config.csvColumns)
        ds.setRecordDelimiter(self.StringEscapeUtils.unescapeJava(config.csvRecordDel))
        ds.setFieldDelimiter(config.csvFieldDel)
        return jpype.JObject(ds, self.JRCsvDataSource)

    def get_data_file_input_stream(self, config: Config):
        return self.JRLoader.getInputStream(self.File(config.dataFile))
