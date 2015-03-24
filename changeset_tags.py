#!/usr/bin/python

# Parses http://planet.osm.org/planet/changesets-latest.osm.bz2
#
# Martin Dittus, March 2015

import argparse
import os, errno

from lxml import etree

def strip(str_):
    if str_ == None:
        return None
    return str_.replace("\\", "\\\\").replace("\n", " ").replace("\r", " ").replace("\t", " ").encode('utf8')

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
    parser.add_argument('outfile', help='Output TSV file for changeset metadata.')
    parser.add_argument('tagfile', help='Output TSV file for changeset tags.')
  
    args = parser.parse_args()

    outfile = os.path.abspath(args.outfile)
    mkdir_p(os.path.dirname(outfile))

    tagfile = os.path.abspath(args.tagfile)
    mkdir_p(os.path.dirname(tagfile))

    # 
    # Parse
    #

    fi = open(args.infile, 'r')
    fo = open(outfile, 'w')
    ft = open(tagfile, 'w')
    
    context = etree.iterparse(fi, events=('start',))
    
    cs = None
    num_total_changesets = 0
    num_changesets = 0
    num_tags = 0

    has_complete_cs_record = False
    cs_record = None
    for action, elem in context:
        if elem.tag=='changeset':
            cs = elem.attrib.get('id')
            uid = elem.attrib.get('uid')
            created_at = elem.attrib.get('created_at')
            closed_at = elem.attrib.get('closed_at')
            has_complete_cs_record = (cs and uid and created_at and closed_at)
            if has_complete_cs_record:
                cs_record = "%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % (cs,
                    created_at,
                    closed_at,
                    uid,
                    strip(elem.attrib.get('user')) or '',
                    elem.attrib.get('num_changes') or '',
                    elem.attrib.get('comments_count') or '')
            num_total_changesets += 1
        elif elem.tag=='tag' and has_complete_cs_record:
            ft.write("%s\t%s\t%s\n" % (cs, strip(elem.attrib.get('k')), strip(elem.attrib.get('v'))))
            num_tags += 1

            if cs_record:
                fo.write(cs_record)
                cs_record = None
                num_changesets += 1
                if num_changesets % 500000 == 0:
                    print "%d tags in %d changesets" % (num_tags, num_changesets)
      
        # cleanup current element, and all previous siblings
        elem.clear()
        while elem.getprevious() is not None:
            del elem.getparent()[0]
    
    print "Processed %d changesets total, %d had tags." % (num_total_changesets, num_changesets)    

    close(fi)
    close(fo)
    close(ft)
