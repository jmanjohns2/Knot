# -*- coding: UTF-8 -*-

from Storage import GEXF_Storage
from Storage import content_storage

#TODO: cleanup tree rendering so that we get a usable tree from a given title. Starting with title 9
#TODO: set up some kind of edge / inter-node relationship data structure and graph via NetworkX

class Orient_Node(object):

    USC_Structure = ['main', 'title', 'chapter', 'subchapter', 'section', 'subsection', 'content', 'p']

    # for example, given a subsection element, the parser should first try to find a paragraph element, then a content element.
    # In either case, if the result returns nothing, try the next tag given in the dictionary's keys.
    USC_Child_Type_Lookup = {'main': ['title'],
                             'title': ['chapter'],
                             'chapter': ['subchapter', 'section','content'],
                             'subchapter': ['section','content'],
                             'section': ['subsection','content'],
                             'subsection': ['paragraph','content'],
                             'paragraph': ['content', 'p', 'ref'],
                             'content': ['p', 'ref']}

    none_Element = 'NONE'



    #root = root of this tree
    #parent = immediate parent of thise node
    #gstore = gexf file storage (export to GEPHI file)
    #cstore = db object (sqllite at this moment)
    #counter = for recursive self setup
    
    #remainder of variables are to set up a node manually (not really for autuoparsing)
    #content = add contne 
    
    def __init__(self, root=None, parent=None, gstore=None, cstore = None, counter = 0, content='', type='', value='', xmlns='',heading='',absolute_address='', id='', recursive=True):

        self.counter_ID = counter
        #self.DB = DB #orientDB DB to store or retrieve nodes
        self.node = root #elementtree xml node object
        self.parent = parent #It seems somehow I made this into an Orient_Node object as opposed to a Node...

        #If no gexf storage object is passed... create one.
        #if(gstore ==None):
        #    self.gexf = GEXF_Storage.GEXF_Storage()
        #else:
        self.gexf = gstore
        self.content_store = cstore

        self.value = value
        self.type = type #a tag defined by xml files... these are put into python lists above
        self.xmlns = xmlns #xml namespace of this node. The same for all tags, as far as I can tell, but you need to include the ns in elementtree searches
        self.heading = heading #Human text heading of section
        self.absolute_address = absolute_address #USC XML address of reference section. This is an addressing scheme unique to the USC xml
        self.id = counter
        self.content = content

        self.children = []

        # this should make this recursive:
        if recursive:
            print('Running recursive')
            self.init()

    #they way the DB is shaping up, I need unique addresses for absolutely everything... this is a problem for content and P nodes which have no addresses...
    #My solution is simple... take the parent address and add /CONTENT to the path. Should be unique as there is one terminal content node...
    def content_Address(self):
        return self.parent.absolute_address + '/CONTENT'

    def load_Children(self):
        # first, let's see which child elements exist... going to test each possibility (given in USC_Child_Type_Lookup)
        # of the dictionary element's list... then, for the ones that don't return 0... popualte child list
        try_List = self.USC_Child_Type_Lookup.get(self.type)
        for t in try_List:
            child_List = self.node.findall(self.xmlns + t)
            if len(child_List) > 0:  # print 'Found children... iterating through results and appending'
                for c in child_List:
                    self.counter_ID = self.counter_ID+1
                    child_Node = Orient_Node(root = c, parent = self, counter = self.counter_ID,gstore=self.gexf, cstore=self.content_store) #was self.node
                    self.children.append(child_Node)

        #log RIDs of children
        child_rids = []

        print('Creating child ids')

        #for c in self.children:
        #    print(type(c))
        #    child_rids.append(c.rid)

        #print('Children array is')
        #print(child_rids)

        ##TODO: detect if parent node is title itself... in which case we don't want to link parent...
        #self.DB.link_Node(node_rid=self.rid, children_rids=child_rids, parent_rid=self.parent.rid)

    # oftentimes (all the time?), I get a content or p object that has a reference that refers to something else but has no address of its own
    # as you might imagine, this is a problem for a network graph. This routine searches up the tree until it finds an address that is not none-type
    def closest_Address_Above(self):

        elem = self

        while elem.parent != None:
            if elem.absolute_address == Orient_Node.none_Element:
                elem = elem.parent
            else:
                return elem.absolute_address
        return elem.absolute_address  # catchall?
    
    #this traverses the xml file,builds a tree of Orient N
    def init(self):

        if self.node == None:
            print('No node object exists... cannot initialize')
            return False

        else:
            try:
                print('---------------------------------------------------------')
                print(self.node)

                print('Self.parent #1 Type: ')
                print(type(self.parent))

                self.xmlns = self.node.tag.split('}')[0] + '}'
                print('XMLns is: '+self.xmlns)

                self.type = self.node.tag.split('}')[1]
                print('Type is: '+self.type)

                if self.type=='content' or self.type == 'heading':
                    self.value = Orient_Node.none_Element
                else:
                    self.value = self.node.find(self.xmlns + 'num').attrib.get('value')
                print('Value is '+self.value)

                heading = self.node.find(self.xmlns + 'heading')

                if heading == None:
                    self.heading = self.none_Element  # totally hardcoded and arbitrary right now.
                else:
                    self.heading = heading.text

                # now let's see if we're at the end of the road.
                if self.type == 'content':
                    print('Terminal content node')
                    #go back and change the address to a content address...
                    self.absolute_address = self.content_Address()

                    #get the content tail...
                    text = ''

                    #if there is text content (I don't think there ever would be in this circumstances.. but you never know
                    #this also works where there are no subnodes but there is content...
                    if (self.node.text!=None):
                        if (len(self.node.text)>0):
                            text = self.node.text

                    #If there are subnodes
                    if len(self.node[:])>0: #this means there are <ps> or <hrefs>
                        print('There are subnodes')
                        for e in self.node[:]:
                            print('Subnode is ')
                            print(e)
                            if e.tag.split('}')[1]=='p':

                                print('This is a paragraph')
                                #if there are sub elements of the <p> element... unlikely but possible. One example I've found so far is <date> subelement
                                if len(e[:])>0:
                                    #this means there were subelements in the <p>... which is probably <hrefs>
                                    print('This was a <p> with subnodes...')

                                    if e.text!=None: #sometimes this is null... sometimes. Arg... so inconsistent.
                                        text = text + e.text

                                    #for each subelement
                                    for se in e[:]:
                                        if se.tag.split('}')[1] == 'ref':
                                            print('Handle href child of <p> with address '+self.absolute_address)

                                            referred_addr = ''

                                            # TODO: this could be a for loop through a list of possible reference classes...
                                            try:
                                                print('HREF REFERENCE TO: ' + se.attrib['href'])
                                                referred_addr = se.attrib['href']
                                                #referred_addr = e.attrib['href'] #I forget what this is supposed to do... it seems to break logging edges
                                                #I was trying to differentiate two types of links apparently? Take a look and try to figure this out.
                                                #UPDATE ^ a typo?

                                            except KeyError:
                                                print('NOT AN HREF REFERENCE')

                                            try:
                                                print('IDREF REFERENCE TO: ' + se.attrib['idref'])
                                                referred_addr = se.attrib['idref']
                                                #referred_addr = e.attrib['idref']
                                                # UPDATE commented line ^ a typo?

                                            except KeyError:
                                                print('NOT AN HREF REFERENCE')
                                            # TODO: end the loop

                                            print("REFERENCE FROM: " + self.closest_Address_Above())

                                            #Log the edge source destination pair in the gexf storage
                                            self.gexf.add_Edge(self.closest_Address_Above(), referred_addr)

                                            text = text + se.text

                                        else:
                                            print('1: Unexpected tag found in '+self.absolute_address)
                                            print(se.tag.split('}')[1])
                                            #try to get text anyway
                                            if se.text != None and len(se.text)>0:
                                                text = text + se.text

                                        #check to see if there is a tail of subelement
                                        if se.tail!=None:
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
                                print(e.attrib)
                                print(e.text)

                                # TODO implement href handeling
                                # Take source address and do lookup in GEXF dictionary
                                # Take target address and do lookup in GEXF dictionary
                                # Then append to gexf edges element

                                #Some details... there are multiple 'classes' of references...
                                #need some kind of list and and a try statement or something
                                #that loops through possible references...

                                referred_addr = ''

                                #TODO: this could be a for loop through a list of possible reference classes...
                                try:
                                    print('HREF REFERENCE TO: ' + e.attrib['href'])
                                    referred_addr=e.attrib['href']
                                except KeyError:
                                    print('NOT AN HREF REFERENCE')

                                try:
                                    print('IDREF REFERENCE TO: ' + e.attrib['idref'])
                                    referred_addr=e.attrib['idref']
                                except KeyError:
                                    print('NOT AN HREF REFERENCE')
                                #TODO: end the loop

                                print("REFERENCE FROM: " + self.closest_Address_Above())
                                #self.DB.log_Edge(self.closest_Address_Above(), referred_addr)
                                #TODO link to above

                                #It appears all of the references classes have text... so this is consistent
                                text = text + e.text
                                print('Complete subtag')

                            else:
                                print('2: Unexpected tag found in ' + self.absolute_address)
                                print(e.tag.split('}'))

                            print('If statements done')

                            #add any tail on the parent element (e)
                            #some elements were throwin an error... saying there is no tail... so added null detection
                            #TODO log those elements and figure out how to account for them...
                            if e.tail!=None and len(e.tail) > 0:
                                print('There is a tail')
                                text = text + e.tail

                            print('complete subtag level 2')
                    self.content = text
                    print('Content is '+self.content)

                    print('adding to gexf datastore, obj:')

                    #add the nodes to the gexf network data storage file
                    self.gexf.add_Node(self)

                    # add hierarchical relationship here.. always parent to child (or should it be child to parent?)
                    self.gexf.add_Edge(to_addr=self.absolute_address, from_addr=self.parent.absolute_address)

                    print('Adding the content to sqllite')
                    #add node content to sqllite db
                    print("ID: {id}".format(id=self.id))
                    print("Address: {abs}".format(abs=self.absolute_address))
                    print("Content: {t}".format(t=text))
                    print(type(self.content_store))
                    self.content_store.add_Entry(addr=self.absolute_address, id = self.id, content = text)
                    print("Successfully added content")

                    #Add the node to the gexf storage so we can get an rid
                    print(self.id)

                    print('Id is')
                    print(self.id)

                    #link the node to its parent... no need to worry about child nodes here...
                    #NOTE: this was failing because usually linking happens in add_children
                    print('I am:')
                    print(self.absolute_address)
                    print('I have a parent... it is')
                    print(self.parent)
                    print('I have a parent Id... it is')
                    print(self.parent.id)

                    return True

                elif self.type != 'content':
                    self.absolute_address = self.node.attrib.get('identifier')
                    print("#1 Address is "+self.absolute_address)

                    # store the node:
                    self.gexf.add_Node(self)

                    # add hierarchical relationship here.. always parent to child (or should it be child to parent?)
                    print("Passthrough node type is "+str(type(self.parent)))

                    #the root notes of each title need to refer to USC root node... don't have that yet (ever?) so need to handle this situation
                    #don't have to do this for content (leaf) nodes as they obv must have parents
                    if (self.parent is None):
                        self.gexf.add_Edge(to_addr=self.absolute_address, from_addr="/us/usc")
                    else:
                        self.gexf.add_Edge(to_addr=self.absolute_address, from_addr=self.parent.absolute_address)

                    # populate the next level with children elements...
                    self.load_Children()

                    return True

                #store the node:
                self.gexf.add_Node(self)

                #add hierarchical relationship here.. always parent to child (or should it be child to parent?)
                self.gexf.add_Edge(to_addr=self.absolute_address, from_addr=self.parent.absolute_address)

                return False

            except AttributeError:
                print('ERROR: There was a parsing error of some sort...')
                print(self.node)
                return False