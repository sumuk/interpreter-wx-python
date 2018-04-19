import os,glob
import xml.etree.ElementTree as ET
tree = ET.parse('def.xml')
root = tree.getroot()



def findall_tag(ptr,tag):
  return  ptr.findall(tag)

def find_tag(ptr,tag):
  return  ptr.find(tag)


def list_def():
  list_name=[]
  for file in glob.glob("Modules/*.xml"):
      tree=ET.parse(file) 
      root=tree.getroot()
      for i in findall_tag(root,'def'):
        if i.get('name'):
          list_name.append(i.get('name'))
  return list_name

def get_all(def_name):
  filename="Modules/"+def_name+".xml"
  tree=ET.parse(filename) 
  root=tree.getroot()
  def_list=root.findall('def')
  for def_tag in def_list:
    if def_tag.get('name')==def_name:
      break
  dict_para={}
  define=''
  syn=''
  for i in def_tag.findall('text'):
      define=i.text
  for i in def_tag.findall('par'):
      dict_para[i.get("name")]=i.text
  for i in def_tag.findall('syntax'):
      syn=i.text
  return(define,dict_para,syn)

def set_para(key,value):
    tree1= ET.parse('evn.xml')
    root1= tree1.getroot()
    ptr=root1.find(key)
    ptr.text=value
    tree1.write('evn.xml')
def get_para(key):
    tree1= ET.parse('evn.xml')
    root1= tree1.getroot()
    ptr=root1.find(key)
    return ptr.text

def get_ip():
    return get_para('IP')
def get_port():
   return int(get_para('Port'))

def make_mfile(filename,text,syntax):
  with open("Modules/"+filename+".xml","wb") as file:
    root = ET.Element("Sirenagui")
    def_name = ET.SubElement(root, "def",name=filename)

    ET.SubElement(def_name, "text").text = text
    ET.SubElement(def_name, "syntax").text = syntax
    
    tree = ET.ElementTree(root)
    tree.write(file)


##make_mfile()
