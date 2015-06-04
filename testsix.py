from linedrop.mutation.collect_hook import CollectStatements
import sys
path = "/whatever"
hook = CollectStatements(path)
print sys.meta_path
sys.meta_path.append(hook)
import six
print sys.meta_path

from six.moves import html_parser

print "ok"
print sys.meta_path
import time
