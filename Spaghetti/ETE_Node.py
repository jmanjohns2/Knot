from ete3 import TreeNode, TreeStyle, NodeStyle, TextFace
from Spaghetti import Edge

#TODO: cleanup tree rendering so that we get a usable tree from a given title. Starting with title 9
#TODO: set up some kind of edge / inter-node relationship data structure and graph via NetworkX

class ETE_Node(TreeNode):
    # This incorporates the ETE3 node class... my hope is that this will allow easy visualization...
    # Guess we'll find out... It did, dumbass

    USC_Structure = ['main', 'title', 'chapter', 'subchapter', 'section', 'subsection', 'content', 'p']

    # I'm not sure there are airtight. Basically, they give the types of tags a given node
    # should expect as a possible child node.

    # interesting... the absolute addresses... they seem to count up from 1 and IGNORE chapters. For example,
    # Chapter 1, Section 1 has an absolute address of simply tit15/s1 ... This may be very helpful actually
    # Could build a directory for each level of the heirarchy so that you use an array to lookup NODE
    # objects rather than iterate accross a tree. More memory intensive, but much faster.

    # TODO: what about href references?
    # Also, be careful that some contents just have content as .text, some have p child.
    # This basically pre-sets what elements the parser should expect as children of a given node type (key)
    # The value mapped to the key is a list of the children elements that are possible and relevant to the
    # USC Topology, at least as it pertains to what this program is trying to do (visualize code structure and inter-relationships)

    # for example, given a subsection element, the parser should first try to find a paragraph element, then a content element.
    # In either case, if the result returns nothing, try the next tag given in the dictionary's keys.
    USC_Child_Type_Lookup = {'main': ['title'],
                             'title': ['chapter'],
                             'chapter': ['subchapter', 'section'],
                             'subchapter': ['section'],
                             'section': ['subsection','content'],
                             'subsection': ['paragraph','content'],
                             'paragraph': ['content', 'p', 'ref'],
                             'content': ['p', 'ref']}

    none_Element = 'NONE'

    #dictionary to map the absolute address of a node to the node object
    abs_Addresses = {}

    #edge object to track all of this stuff
    edge_Obj = Edge.Edge()

    def __init__(self, root=None, parent=None):

        TreeNode.__init__(self)

        self.node = root #elementtree xml node object
        self.parent = parent #parent ETE_Node object
        self.rid = '' #database identifier for orientDB...

        self.value = ''
        self.type = '' #a tag defined by xml files... these are put into python lists above
        self.xmlns = '' #xml namespace of this node. The same for all tags, as far as I can tell, but you need to include the ns in elementtree searches
        self.heading = '' #Human text heading of section
        self.absolute_address = '' #USC XML address of reference section. This is an addressing scheme unique to the USC xml

        self.content = None

        self.children = []

        # this should make this recursive:
        self.init()

        # Notes not implemented yet
        # Not sure TOC is necessary ever
        # sourceCredit is not implemented yet
        ETE_Node.edge_Obj.update_Address_Coll(ETE_Node.abs_Addresses)

    #oftentimes (all the time?), I get a content or p object that has a reference that refers to something else but has no address of its own
    #as you might imagine, this is a problem for a network graph. This routine searches up the tree until it finds an address that is not none-type
    def closest_Address_Above(self):

        elem = self

        while elem.parent != None:
            if elem.absolute_address==ETE_Node.none_Element:
                elem = elem.parent
            else:
                return elem.absolute_address

        return elem.absolute_address #catchall?

    #they way the DB is shaping up, I need unique addresses for absolutely everything... this is a problem for content and P nodes which have no addresses...
    #My solution is simple... take the parent address and add /CONTENT to the path. Should be unique as there is one terminal content node...
    def content_Address(self):
        return self.closest_Address_Above()+'/CONTENT'

    #override the inherited tostring method from ETE... it's lovely... but it's not very useful in most of the situations I'm dealing with.
    #I guess you could still access that by calling it from the parent class? Not sure how to do that in python. Must be easy.
    def __str__(self):
        if (self.absolute_address!=self.none_Element):
            return self.absolute_address
        else:
            return self.type

    def log_Edge(self, referring_Addr, referee_Adr):
        ETE_Node.edge_Obj.append_Addresses(referring_Addr, referee_Adr)

    def process_Edges(self):
        ETE_Node.edge_obj.networkx_Refresh()

    def load_Children(self):
        # first, let's see which child elements exist... going to test each possibility (given in USC_Child_Type_Lookup)
        # of the dictionary element's list... then, for the ones that don't return 0... popualte child list
        try_List = self.USC_Child_Type_Lookup.get(self.type)
        for t in try_List:
            child_List = self.node.findall(self.xmlns + t)
            # print 'Searching for children of type: '+t
            # if len(child_List)==0:
            # print 'Failed to find any children'
            if len(child_List) > 0:  # print 'Found children... iterating through results and appending'
                for c in child_List:

                    child_Node = ETE_Node(c, self) #was self.node
                    #if this is a content node... add the content (eventually as a text face):
                    if child_Node.type == 'content':
                        self.add_child(child_Node, child_Node.type + ": " + child_Node.content.encode('ascii','ignore')[:64]) #apparently, using a non-ascii string in node title makes ete3 crash. Truncated it
                        self.children.append(child_Node)
                    else:
                        print("Node name should be " + child_Node.type + " " + child_Node.value)
                        self.add_child(child_Node, child_Node.type + " " + child_Node.value)
                        self.children.append(child_Node)

    def init(self):
        if self.node == None:
            print('No node object exists... cannot initialize')
            return False

        else:
            try:
                print('---------------------------------------------------------')
                print('starting new parsing run of:')
                print(self.node)
                # these are common to all node types... so run these first.

                self.xmlns = self.node.tag.split('}')[0] + '}'
                print('XML NS is:')
                print(self.xmlns)

                self.type = self.node.tag.split('}')[1]
                print('Type is:')
                print(self.type)

                #content and heading tags don't (ever?) have attribute tags...
                if self.type=='content' or self.type == 'heading':
                    self.value = ETE_Node.none_Element
                else:
                    self.value = self.node.find(self.xmlns + 'num').attrib.get('value')

                print('Value is:')
                print(self.value)

                # I can't find a consistent pattern on which notes have a heading... I'll keep working on it
                # some of the nodes with content children nodes have heading... some don't.
                # I don't think any of the noes without content children but with text nodes have headings...
                # not sure. Regardless, using find returns a None object when there is no heading result:                heading = self.node.find(self.xmlns+'heading
                heading = self.node.find(self.xmlns + 'heading')
                if heading == None:
                    print('No heading found!')
                    self.heading = self.none_Element  # totally hardcoded and arbitrary right now.
                else:
                    self.heading = heading.text
                    # print 'Heading is:'
                    # print self.heading

                # Some node do not have any attributes... some have attribute but no iaddress
                #the ones without attributes appear to only be Heading and Content nodes. I cannot confirm this accross entire USC
                #the ones with attributes but no address appear to be <p>s only...? Less sure of that.

                addr = self.node.attrib.get('identifier')
                if (addr == None):
                    self.absolute_address = self.none_Element
                else:
                    self.absolute_address = addr

                print('Abs. Address is:')
                print(self.absolute_address)

                #TODO: for nodes that don't have addreses (terminal or near-terminal nodes like content or <p>), there will be multiple
                #values for the key "None." Perhaps I ought to add my own addresses for these? Or just leave them out to save memory
                #IF they're never going to need to be looked up...

                #TODO: this will be deprecated by the new OrientDB backend
                #add the node's absolute address to the node dictionary
                self.abs_Addresses[self.absolute_address] = self

                # now let's see if we're at the end of the road.
                if self.type == 'content':

                    #go back and change the address to a content address...
                    self.absolute_address = self.content_Address()

                    #get the content tail...
                    text = ''

                    #if there is text content (I don't think there ever would be in this circumstances.. but you never know
                    #this also works where there are no subnodes but there is content...
                    if (len(self.node.text)>0):
                        text = self.node.text

                    #If there are subnodes
                    if len(self.node[:])>0: #this means there are <ps> or <hrefs>
                        print('There are subnodes')
                        for e in self.node[:]:
                            if e.tag.split('}')[1]=='p':
                                print('<p> detected')
                                # get the addres of this <p> (if it exists)
                                p_Addr = e.attrib.get('identifier')
                                if (p_Addr == None):
                                    self.absolute_address = self.none_Element
                                    p_Addr = self.absolute_address
                                else:
                                    self.absolute_address = p_Addr

                                #if there are sub elements of the <p> element... unlikely but possible. One example I've found so far is <date> subelement
                                if len(e[:])>0:
                                    #this means there were subelements in the <p>... which is probably <hrefs>
                                    print('This was a <p> with subnodes...')
                                    text = text + e.text
                                    for se in e[:]:
                                        if se.tag.split('}')[1] == 'ref':
                                            print('Handle href child of <p> with address '+p_Addr)

                                            #TODO implement href handeling (check it works)
                                            print('REFERENCE TO: '+se.attrib['href'])
                                            print("Reference FROM: "+self.closest_Address_Above())
                                            self.log_Edge(self.closest_Address_Above(),se.attrib['href'])

                                            text = text + se.text
                                        else:
                                            print('1: Unexpected tag found in '+p_Addr)
                                            print(se.tag.split('}')[1])
                                            #try to get text anyway
                                            if se.text != None and len(se.text)>0:
                                                text = text + se.text

                                        #check to see if there is a tail of subelement
                                        if len(se.tail)>0:
                                            text = text + se.tail
                                            # check to see if there is a tail from subelement (se)

                                # If there are no sub elements
                                else:
                                    text = text + e.text

                            #Note: the ref node has an attribute called href which has a value equal to the absolute address of the element it references
                            #The plain text of the reference is the .text of the ref node.
                            elif e.tag.split('}')[1]=='ref':
                                print('Handle href child of <content>')

                                # TODO implement href handeling
                                print('REFERENCE TO: ' + e.attrib['href'])
                                print("REFERENCE FROM: " + self.closest_Address_Above())
                                self.log_Edge(self.closest_Address_Above(), e.attrib['href'])


                                text = text + e.text

                            else:
                                print('2: Unexpected tag found in ' + self.absolute_address)
                                print(e.tag.split('}'))

                            #add any tail on the parent element (e)
                            if len(e.tail) > 0:
                                text = text + e.tail

                    self.content = text

                    #TODO: upload the node to the persistent storage DB and update the rid
                    #self.rid =

                    return True

                elif self.type != 'content':
                    # populate the next level with children elements...
                    self.load_Children()

                    # TODO: upload the node to the persistent storage DB and update the rid

                    return True

                # catchall returns False if the if loops fails somehow
                return False

            except AttributeError:
                print('ERROR: There was a parsing error of some sort...')
                print(self.node)