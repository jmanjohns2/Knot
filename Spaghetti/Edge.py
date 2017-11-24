import networkx as nx
#import Orient_Node
import matplotlib.pyplot as plt

#TODO: check that the references to the abs_Addresses object in ETE_Node won't be a problem.

#The problem with this rendering enginge as it stands now is that it does not traverse and parse the entire United States Code.
#So, I can't just look for a toss code nodes into networkX, because they very well might be None objects at the moment.

#Soooo.... this class exists (for now, at least until the entire USC can be put into a database or something) and it holds text references
#from one node to another (extracted from the <ref> tags in the xml data).

#the method network_Graph() will then go try to finds objects and create a networkx object. If the reference does not actually exist... (meaning
#in this limited implementation that it is from another title of the code), just use the plaintext String object of the address. I believe
#networkx allows this.

class Edge(object):
    def __init__(self, addres_Coll = None):
        self.edge_dictionary = {}  # the key marks the node making the reference and the value is the node being referred to
        self.processed = False #False if there are unprocessed nodes, True if otherwise
        self.nx_Graph = nx.Graph()
        self.address_Collection = addres_Coll

    def draw_Network(self,file="./test.pgn"):
        if self.processed:
            nx.draw(self.nx_Graph, with_labels=True)
            plt.savefig(file)

    def update_Address_Coll(self,coll):
        self.address_Collection = coll

    def networkx_Refresh(self):

        i = 1
        for key in self.edge_dictionary:
            print("Iteration #"+str(i))
            i+=1

            referee = self.edge_dictionary[key]
            referee_obj = None
            key_obj = None

            #test to see if we can use an ETE_Node object for the referred to object or whether we need to use a string object
            try:
                #this will throw a KeyError if these addresses were never traversed by the parses and hence never created ETE_Nodes
                referee_obj = self.address_Collection[referee]

            #if the address directory did not contain the address or addresses we're looking for, the parser has not traversed that part
            #of the USC and a KeyError was thrown.
            except KeyError:
                #print "WARNING: selected notes for edge do not exist as ETE_Nodes, using plain text"
                referee_obj = referee

            #Now do the same for the key
            try:
                key_obj = self.address_Collection[key]

            except KeyError:
                #print "WARNING: selected notes for edge do not exist as ETE_Nodes, using plain text"
                key_obj = key

            # Check there is no duplicate text key in the network... only add the text addreses if they're not already there
            if not self.nx_Graph.has_node(key_obj):
                self.nx_Graph.add_node(key_obj)
            if not self.nx_Graph.has_node(referee_obj):
                self.nx_Graph.add_node(referee_obj)

            #now add the edge
            self.nx_Graph.add_edge(key_obj,referee_obj)


        #flag that we've processed the Edges
        self.processed = True

        return True

    def append_Addresses(self, referer = None, referee = None):
        if isinstance(referer,str) and isinstance(referee, str):
            print('Attempting to append')
            self.edge_dictionary[referer] = referee
            self.processed = False
            return True
        else:
            print('ERROR: This method requires the two string absolute addresses between the xml nodes of the USC')
            return False
