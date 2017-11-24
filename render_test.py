# -*- coding: UTF-8 -*-

from Spaghetti import Orient_Node #this is clearly the main class.
from Spaghetti import USC
from Storage import GEXF_Storage
from Storage import content_storage

import ete3
from ete3 import TreeStyle, NodeStyle, TextFace, add_face_to_node
import time
import xml.etree.ElementTree as ET


tit15 = USC.get_Title_XML_Tree(9)  #returns ElementTree Tree
USC_title15_node = tit15.find('{http://xml.house.gov/schemas/uslm/1.0}main').find('{http://xml.house.gov/schemas/uslm/1.0}title')


#fill database with arbitrary range of titles
def populate_Titles(start_Title = 1, end_Title=1):

    store = GEXF_Storage.GEXF_Storage()
    content_store = content_storage.content_storage()
    content_store.setup_DB()

    for i in range(start_Title,end_Title):
        if not (i==34 or i==53):
            tit = USC.get_Title_XML_Tree(i)
            USC_title_node = tit.find('{http://xml.house.gov/schemas/uslm/1.0}main').find(
            '{http://xml.house.gov/schemas/uslm/1.0}title')

            title_obj = Orient_Node.Orient_Node(root=USC_title_node,gstore=store,cstore=content_store) #I see... DB and GEXF object being passed from recursive call to call.
            print(title_obj)

    print(store.edge_Storage)
    store.traverse_Edges()

    store.write_File()
    print(store.gexf_Dict)
    print(store.adr_Dict)

    content_store.save_DB()
    content_store.save_Out_DB()
    content_store.close_DB()


populate_Titles(15,16)


#print('Testing Render')
#test.render('./test.png', w=1920, units = "px", tree_style=default)
#print('Render Complete')

#Trying to figure out how to get the ; and ;or from the content nodes... they're locked by hrefs.
#specifically, going to be working with /us/usc/t9/s16/b/1
# print test.abs_Addresses
# plaything = test.abs_Addresses.get('/us/usc/t9/s201').node.find('{http://xml.house.gov/schemas/uslm/1.0}content')
# print plaything[:]
