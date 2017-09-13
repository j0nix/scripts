#! /usr/bin/python
# j0nix 2017
# Checks status of a ES luster, if yellow checks if we nissing nodes, otherwise ignore. Room for improvements but catches obvious cluster problems

#import modules
import sys
from optparse import OptionParser
import urllib2
try:
    import json
except ImportError:
    import simplejson as json

#NAGIOS return codes
RETURN_CODE = { "UNKNOWN":0,"OK":0,"WARNING":1,"CRITICAL":2}

# Parse options
def build_parser():
    parser = OptionParser()
    parser.add_option("-H", "--host", dest="host", help="Host to connect to", default="127.0.0.1")
    parser.add_option("-p", "--port", dest="port", help="Port where http API is published", type="int", default=9200)
    parser.add_option("-n", "--nr_of_nodes", dest="nr_of_nodes", help="Number of cluster nodes this cluster have", type="int")
    parser.add_option("-d", "--debug", dest="debug", help="Enable debug", action="store_true")
    return parser
def validate_args(p,o):

    if not o.nr_of_nodes:
        p.error("Number of nodes in cluster is required")
        sys.exit(RETURN_CODE['UNKNOWN'])

# Your magic check funktion
def check(options):

        try:
            response = urllib2.urlopen(r'http://%s:%d/_cluster/health' % (options.host, options.port))
        except urllib2.HTTPError, e:
            print "status unknown, API failure: {}".format(e)
            sys.exit(RETURN_CODE['UNKNOWN'])
        except urllib2.URLError, e:
            print "UrlError: {}".format(e.reason)
            sys.exit(RETURN_CODE['CRITICAL'])

        response_body = response.read()

        if options.debug:
                print "\n\rDEBUG::check:\n\r{}".format(response_body)

        try:
            es_cluster_health = json.loads(response_body)
        except ValueError:
            print "status unknown, could not parse JSON response"
            sys.exit(RETURN_CODE['UNKNOWN'])

        return es_cluster_health


# Validate your check result against thresholds
def validate_and_notify(cluster_health, options):

    if options.debug:
        print "\n\rDEBUG::validate_and_notify:\n\r{}".format(cluster_health)

    if cluster_health['status'].lower() == 'red':
        print "Status red, number_of_nodes: {}, relocating_shards: {}, initializing_shards {}, unassigned_shards: {}, active_shards_percent_as_number: {}".format(cluster_health['number_of_nodes'],cluster_health['relocating_shards'] ,cluster_health['initializing_shards'],cluster_health['unassigned_shards'],cluster_health['active_shards_percent_as_number'] )
        sys.exit(RETURN_CODE['CRITICAL'])
    elif cluster_health['status'].lower() == 'yellow' and cluster_health['number_of_nodes'] < int(options.nr_of_nodes):
        print "STATUS == YELLOW and missing cluster nodes. Have {}, expecting {}".format(cluster_health['number_of_nodes'],options.nr_of_nodes)
        sys.exit(RETURN_CODE['WARNING'])
    else:
        print "All OK, status: {}, number_of_nodes: {}, relocating_shards: {}, initializing_shards {}, unassigned_shards: {}, active_shards_percent_as_number: {}".format(cluster_health['status'],cluster_health['number_of_nodes'],cluster_health['relocating_shards'] ,cluster_health['initializing_shards'],cluster_health['unassigned_shards'],cluster_health['active_shards_percent_as_number'] )
        sys.exit(RETURN_CODE['OK'])


# logical script flow
def main():

  # Get, parse and validate args
  parser = build_parser()
  options, _args = parser.parse_args()
  validate_args(parser,options)

  if options.debug:
        print "\n\rDEBUG::options:\n\r{}".format(options)

  result = check(options) # check stuff
  validate_and_notify(result,options)

if __name__ == '__main__':
  main()
