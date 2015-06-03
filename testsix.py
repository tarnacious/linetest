from linedrop.mutation.collect_hook import CollectStatements
import sys
path = "/whatever"
hook = CollectStatements(path)
sys.meta_path.append(hook)
import six
from six.moves import html_parser
print "ok"
