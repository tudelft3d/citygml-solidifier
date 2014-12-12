#!/usr/bin/python
# -*- coding: utf-8 -*-

# The MIT License (MIT)

# Copyright (c) 2014
# Hugo Ledoux
# Delft University of Technology
# h.ledoux@tudelft.nl

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import sys
from lxml import etree
import uuid

ns = {}

def main():
    parser = etree.XMLParser(ns_clean=True)
    tree = etree.parse(sys.argv[1], parser)
    root = tree.getroot()

    for key in root.nsmap.keys():
        if root.nsmap[key].find('www.opengis.net/gml') != -1:
            ns['gml'] = "%s" % root.nsmap[key]
        if root.nsmap[key].find('http://www.opengis.net/citygml/1.0') != -1:
            ns['cgml'] = "%s" % root.nsmap[key]
        if root.nsmap[key].find('http://www.opengis.net/citygml/2.0') != -1:
            ns['cgml'] = "%s" % root.nsmap[key]
        if root.nsmap[key].find('http://www.opengis.net/citygml/building/') != -1:
            ns['cgmlb'] = "%s" % root.nsmap[key]
        if root.nsmap[key].find('www.w3.org/1999/xlink') != -1:
            ns['xlink'] = "%s" % root.nsmap[key]    
        if root.nsmap[key].find('http://www.w3.org/2001/XMLSchema-instance') != -1:
            ns['xsi'] = "%s" % root.nsmap[key]

    if 'xlink' not in root.nsmap.keys():
        # can't just add a key to ns, so nasty/convoluted way is used
        newnsmap = root.nsmap
        newnsmap['xlink'] = 'http://www.w3.org/1999/xlink'
        new_root = etree.Element(root.tag, nsmap=newnsmap)
        # add the schemaLocation from the original root
        if 'xsi' in root.nsmap.keys():
            new_root.set("{%s}schemaLocation" % ns['xsi'], root.get("{%s}schemaLocation" % ns['xsi']))
        new_root[:] = root[:]
        root = new_root
        ns['xlink'] = "%s" % root.nsmap['xlink']


    buildings = root.findall(".//{%s}Building" % ns['cgmlb'])
    # print "Number of buildings:", len(buildings)

    for b in buildings:
        # if already a Solid then next one
        if (b.find("{%s}lod1Solid" % ns['cgmlb']) is not None or
            b.find("{%s}lod2Solid" % ns['cgmlb']) is not None or
            b.find("{%s}lod3Solid" % ns['cgmlb']) is not None):
            continue

        # if in MultiSurfaces
        if (b.find("{%s}lod1MultiSurface" % ns['cgmlb']) is not None or 
            b.find("{%s}lod2MultiSurface" % ns['cgmlb']) is not None or 
            b.find("{%s}lod3MultiSurface" % ns['cgmlb']) is not None):
            print "---multisurfaces---"
            # TODO : implement this.
        
        # if semantic surfaces are used
        if (b.findall("{%s}boundedBy" % ns['cgmlb'])):
            # print "---boundedBy---"
            semsurfaces = []
            lod = 0
            for bby in b.findall(".//{%s}boundedBy" % ns['cgmlb']):
                semsurface = bby[0]
                gmlid = semsurface.get("{%s}id" % ns['gml'])
                if gmlid == None:
                    semsurface.set("{%s}id" % ns['gml'], str(uuid.uuid4()))
                for i in range(1,4):
                    if len(semsurface.findall(".//{%s}lod%dMultiSurface" % (ns['cgmlb'], i))) != 0:
                        lod = i
                        break
                for i in semsurface.findall(".//{%s}Polygon" % ns['gml']):
                    semsurfaces.append(i)
            bsolid = etree.Element("{%s}lod2Solid" % ns['cgmlb'])
            s = etree.SubElement(bsolid, "{%s}Solid" % ns['gml'])
            e = etree.SubElement(s, "{%s}exterior" % ns['gml'])
            cs = etree.SubElement(e, "{%s}CompositeSurface" % ns['gml'])
            for s in semsurfaces:
                sm = etree.SubElement(cs, "{%s}surfaceMember" % ns['gml'])
                sm.set("{%s}href" % ns['xlink'], s.get("{%s}id" % ns['gml']))
            b.insert(0, bsolid)

    sys.stdout.write(etree.tostring(root, 
        pretty_print=True, 
        xml_declaration=True,
        encoding='utf-8'))


if __name__ == "__main__":
    main()


