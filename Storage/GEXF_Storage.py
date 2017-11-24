import xml.etree.ElementTree as ET
from Storage import Counter

class GEXF_Storage(object):

    #defining the data structure for a GEXF file which is just a specially formatted xml file (https://gephi.org/gexf/format/)
    #this will serve as data storage and as an export format for visualization using gexf OR sigma.js
    def __init__(self):

        self.count = Counter.Counter()
        self.edge_count = Counter.Counter()
        #These dictionaries will be used to ensure we have consistent, numerical IDs for nodes accross all USc titles.
        self.gexf_Dict = {}  # Allows us to take an arbitrary ID and lookup up gexf node...
        self.reverse_gexf_Dict = {}
        self.adr_Dict = {}  # Allows us to take an arbitrary ID and lookup the string "addr" as that's that actual unique ID in the USC
        self.reverse_adr_Dict = {}

        #storage for edge to/from addr pairs until we later traverse the nodes to add the edges
        self.edge_Storage = {}

        self.gexf = ET.Element("gexf")
        self.gexf.attrib['version'] = "1.2"
        self.gexf_tree = ET.ElementTree(self.gexf)

        meta = ET.SubElement(self.gexf, "meta")
        meta.attrib['lastmodifieddate'] = "2017-06-01"
        ET.SubElement(meta, "creator").text = "J Scrudato - USC Parser v1"
        ET.SubElement(meta, "description").text = "Network Graph of United States Code"

        self.graph = ET.SubElement(self.gexf, "graph")
        self.graph.attrib['mode'] = 'static'
        self.graph.attrib['defaultedgetype'] = "directed"

        attributes = ET.SubElement(self.graph,"attributes")
        attributes.attrib['class']='node'

        type = ET.SubElement(attributes,'attribute')
        type.attrib['id']='0'
        type.attrib['title']='type'
        type.attrib['type'] = 'string'

        self.nodes = ET.SubElement(self.graph, "nodes")
        self.edges = ET.SubElement(self.graph, "edges")

    # This will output the gexf tree as xml file to path
    def write_File(self, path = "/home/descartes/workspace/USC_Visualizer/USC_GEXF_Data/usc.xml"):
        with open(path, 'w', encoding='utf-8') as file:
            self.gexf_tree.write(file, encoding='unicode')

    def add_Node(self, Node):
        if (Node.absolute_address in self.adr_Dict):
            print ("Node already exists")
        else:

            #increment class ID counter
            self.count.advance_Count()
            print("Counter value is")
            print(self.count.get_Count())

            #create a new xml tree node as child of nodes
            new_node = ET.SubElement(self.nodes,"node")
            #TODO what about text? and headers?
            new_node.attrib['id'] = str(self.count.get_Count())
            new_node.attrib['value'] = str(Node.value)
            new_node.attrib['label'] = str(Node.absolute_address)
            new_node.attrib['type'] = str(Node.type)
            new_node.attrib['heading'] = str(Node.heading)
            new_node.attrib['absolute_address']= str(Node.absolute_address)

            attvalues = ET.SubElement(new_node,'attvalues')
            attvalue = ET.SubElement(attvalues,'attvalue')
            attvalue.attrib['for']='0'
            attvalue.attrib['value']=str(Node.type)

            #populate the lookup dictionaries... this really should be a DB... do that later.
            self.gexf_Dict[self.count.get_Count()] = new_node
            self.reverse_gexf_Dict[new_node] = self.count.get_Count()
            self.adr_Dict[self.count.get_Count()] = Node.absolute_address
            self.reverse_adr_Dict[Node.absolute_address] = self.count.get_Count()

    #TODO... the edges should be added at the end... to ensure that all of the nodes in our network have been added first...
    #TODO not dictionary for edges... should there be?
    def process_Edge(self, to_addr, from_addr):

        if (from_addr in self.reverse_adr_Dict) or (to_addr in self.reverse_adr_Dict) :

            #if the source node does not exist... assume it wasn't in xml tree so create a dummy external reference to element in another tree
            if not (to_addr in self.reverse_adr_Dict):
                print("Source node exists... target node does not... assuming external and adding external reference node.")
                self.add_External_Node(to_addr)

            # if the source node does not exist... assume it wasn't in xml tree so create a dummy external reference to element in another tree
            if not (from_addr in self.reverse_adr_Dict):
                print(
                    "Source node exists... target node does not... assuming external and adding external reference node.")
                self.add_External_Node(from_addr)

            self.edge_count.advance_Count()
            print("Edge Counter value is")
            print(self.edge_count.get_Count())

            # create a new xml tree node as child of nodes
            new_edge = ET.SubElement(self.edges, "edge")
            # TODO what about text? and headers?
            new_edge.attrib['id'] = str(self.edge_count.get_Count())
            #need to lookup the ***ID*** of the adr as that's how gexf works... everything referenced by IDs
            new_edge.attrib['source'] = str(self.reverse_adr_Dict[to_addr])
            new_edge.attrib['target'] = str(self.reverse_adr_Dict[from_addr])

        else:
            print("What's going on here? No nodes in this edge are in the data store")
            print("Edge from "+from_addr+"to "+to_addr+" not logged")

    #Because we have to traverse the tree and create all of the nodes first... then create the edge references between them... we will collect edge references
    #as key pairs first. Then, once the nodes are setup, we'll create the edge references.
    def add_Edge(self, to_addr, from_addr):
        self.edge_Storage[to_addr] = from_addr

    #this method will run through the edge_Storage dictionary and create all of the edge xml entries... each time it's run it will empty out the edge
    #dictionary and recreate the xml edge elements using whatever is in the edge storage. If edge_storage is empty it will result in empty edge xml elements.
    def traverse_Edges(self):

        #TODO erase existing edges... at the moment not important as this only runs once so it's always empty
        for to_addr in self.edge_Storage:
            self.process_Edge(to_addr,self.edge_Storage[to_addr])

        self.edge_Storage = {}

    #Where we have a reference to an address that was not in the source xml tree... we just create a dummy node using the
    #str address of that node.
    def add_External_Node(self, addr):
        # increment class ID counter
        self.count.advance_Count()
        print("Counter value is")
        print(self.count.get_Count())

        # create a new xml tree node as child of nodes
        new_node = ET.SubElement(self.nodes, "node")
        # TODO what about text? and headers?
        new_node.attrib['id'] = str(self.count.get_Count())
        new_node.attrib['value'] = str("REFERENCE to "+str(addr))
        new_node.attrib['label'] = str(addr)
        new_node.attrib['type'] = str("REFERENCE")
        new_node.attrib['heading'] = str("Referenced Section")
        new_node.attrib['absolute_address'] = str(addr)

        attvalues = ET.SubElement(new_node, 'attvalues')
        attvalue = ET.SubElement(attvalues, 'attvalue')
        attvalue.attrib['for'] = '0'
        attvalue.attrib['value'] = str("External")

        # populate the lookup dictionaries... this really should be a DB... do that later.
        self.gexf_Dict[self.count.get_Count()] = new_node
        self.reverse_gexf_Dict[new_node] = self.count.get_Count()
        self.adr_Dict[self.count.get_Count()] = new_node.attrib['absolute_address']
        self.reverse_adr_Dict[new_node.attrib['absolute_address']] = self.count.get_Count()