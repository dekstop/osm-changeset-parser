#!/usr/bin/python

# Parses http://planet.osm.org/planet/changesets-latest.osm.bz2
#
# Martin Dittus, March 2015

import argparse
import os, errno
import re

from collections import defaultdict
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

re_hot_project = re.compile('#hotosm[^ /#,+;.:]+-([0-9]+)')

def get_project_id(tag_value):
    match = re_hot_project.search(tag_value)
    if match:
        return int(match.group(1))
    return None

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
    description='Parses OSM changeset XML files and extracts all users who submitted HOT changesets, as identified based on changeset tags.')
    parser.add_argument('infile', help='Input file, in XML format.')
    parser.add_argument('outfile', help='Output TSV file for user list.')
  
    args = parser.parse_args()

    outfile = os.path.abspath(args.outfile)
    mkdir_p(os.path.dirname(outfile))

    # 
    # Parse
    #

    fi = open(args.infile, 'r')
    fo = open(outfile, 'w')
    
    context = etree.iterparse(fi, events=('start',))
    
    num_changesets = 0
    projects_users = defaultdict(lambda: defaultdict(lambda: 0))
    num_entries = 0

    for action, elem in context:
        if elem.tag=='changeset':
            uid = elem.attrib.get('uid')
            username = strip(elem.attrib.get('user')) or ''
            
            num_changesets += 1
            if num_changesets % 5000000 == 0:
                print "%d changesets" % (num_changesets)
        elif elem.tag=='tag' and uid!=None:
            if elem.attrib.get('k')=='comment':
                project = get_project_id(elem.attrib.get('v'))
                if project:
                    projects_users[project][uid] += 1
                    if projects_users[project][uid]==1:
                        fo.write("%d\t%s\t%s\n" % (project, uid, username))
                        num_entries += 1
      
        # cleanup current element, and all previous siblings
        elem.clear()
        while elem.getprevious() is not None:
            del elem.getparent()[0]
    
    print "Processed %d changesets, wrote %d entries." % (num_changesets, num_entries)

    fi.close()
    fo.close()
