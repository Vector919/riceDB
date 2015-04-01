# rice/query.py
#
# Defines the Query class.
#

import urllib.request
import json
import os
from rice import error, util, package

class Query(object):
    def __init__(self, program_name, search_term, local=False):
        with open(util.RDBDIR + "config") as config_file:
            try:
                config = json.load(config_file)
            except Exception as e:
                raise error.corruption_error("Invalid JSON: %s" %(e))
        if not local:
            try:
                request = urllib.request.Request(config["db"] + query)
                response = urllib.request.urlopen(request).read().decode('utf-8')
                #print("Reponse is: " + response)
            except Exception as e:
                raise error.Error("Could not connect to server %s: %s" % (config["db"], e))
            try:
                self.results = json.loads(response)
            except Exception as e:
                raise error.corruption_error("Could not read JSON from server: %s" %(e))
        else:
            print(os.path.expanduser(config["localdb"]))
            rices = json.load(open(os.path.expanduser(config["localdb"])))
            if search_term in rices[program_name]:
                self.results = [{"name":search_term,"program":program_name}]
            else:
                self.results = []
    def get_results(self):
        # print(self.results)
        packs = []
        for i in self.results:
            #print(i)
            packs.append(package.Package(i))
        return packs
        #return self.results
        # return [package.Package(i) for i in self.results]

