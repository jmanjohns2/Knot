import sqlite3
import xml.etree.ElementTree as ET


class content_storage(object):

    def __init__(self, dbname = "usc.db"):
        self.sql = sqlite3.connect(dbname)

    def setup_DB(self):
        c = self.sql.cursor()

        c.execute('''CREATE TABLE USC
                     (address TEXT, id INT, content TEXT)''')

    def add_Entry(self, addr, id, content):
        print("Get Cursor")
        c = self.sql.cursor()
        # Insert a row of data
        print("Execute statement")
        c.execute("INSERT INTO USC (address, id, content) VALUES (?,?,?)".format(addr, id, content),(addr, id, content))

    def save_DB(self):
        self.sql.commit()

    def close_DB(self):
        self.sql.close()

    def lookup_by_ID(self, id):

        c = self.sql.cursor()
        for d in c.execute('SELECT * FROM USC WHERE id=?', id):
            print(d)

    def lookup_by_Addr(self, addr):

        c = self.sql.cursor()
        for d in c.execute('SELECT * FROM USC WHERE address=?', addr):
            print(d)

    def save_Out_DB(self, path="/home/descartes/workspace/USC_Visualizer/USC_GEXF_Data/USC_content.xml"):

        output = ET.Element("content")
        output.attrib['version'] = "1.0"
        output_tree = ET.ElementTree(output)

        meta = ET.SubElement(output, "meta")
        meta.attrib['lastmodifieddate'] = "2017-06-01"
        ET.SubElement(meta, "creator").text = "J Scrudato - USC Parser v1"
        ET.SubElement(meta, "description").text = "Database of Node Content"

        contents = ET.SubElement(output,"contents")

        c = self.sql.cursor()
        for d in c.execute('SELECT * FROM USC'):
            f = ET.SubElement(contents,"content")
            p = ET.SubElement(f,"p")
            p.text = str(d)

        with open(path, 'w', encoding='utf-8') as file:
            output_tree.write(file, encoding='unicode')
