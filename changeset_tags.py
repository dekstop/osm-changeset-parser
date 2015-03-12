#!/usr/bin/python

# Parses http://planet.osm.org/planet/changesets-latest.osm.bz2
#
# Martin Dittus, March 2015

import argparse
import os, errno

from lxml import etree

def strip(str_):
    return str_.replace("\n", " ").replace("\r", " ").replace("\t", " ").encode('utf8')

def mkdir_p(path):
  try:
    os.makedirs(path)
  except OSError as exc:
    if exc.errno == errno.EEXIST and os.path.isdir(path):
      pass
    else: raise

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
    description='Parses OSM changeset XML files, e.g. http://planet.osm.org/planet/changesets-latest.osm.bz2')
    parser.add_argument('infile', help='Input file, in XML format.')
    parser.add_argument('outfile', help='Output TSV file.')
  
    args = parser.parse_args()

    outfile = os.path.abspath(args.outfile)
    mkdir_p(os.path.dirname(outfile))

    # 
    # Parse
    #

    fi = open(args.infile, 'r')
    fo = open(args.outfile, 'w')
    
    context = etree.iterparse(fi)
    
    cs = None
    allcs = set()
    num = 0
    for action, elem in context:
        if elem.tag=='changeset':
            #print elem.attrib.get('id'), elem.attrib.get('created_at'), elem.attrib.get('user')
            cs = elem.attrib.get('id')
            allcs.add(cs)
        elif elem.tag=='tag':
            fo.write("%s\t%s\t%s\n" % (cs, strip(elem.attrib.get('k')), strip(elem.attrib.get('v'))))
            num += 1
            if num % 100000 == 0:
                print "%d tags in %d changesets" % (num, len(allcs))
      
        # cleanup current element, and all previous siblings
        elem.clear()
        while elem.getprevious() is not None:
            del elem.getparent()[0]
    
    close(fi)
    close(fo)
