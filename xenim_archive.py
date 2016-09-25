import urllib, json
import sys, codecs

url = "http://feeds.streams.demo.xenim.de/api/v1/episode/?list_endpoint"
response = urllib.urlopen(url)

data = json.loads(response.read().decode("utf-8-sig"))


# j = json.loads(input_file.read().decode("utf-8-sig"))

# data.encode('ascii', 'ignore')
utf8_writer = codecs.getwriter('UTF-8')
sys.stdout = utf8_writer(sys.stdout, errors='replace')

# print(data['meta'])
for objects in data['objects']:
    for attribute, value in objects.iteritems():
            # if attribute=="absolute_url":
        # value.encode('ascii', 'ignore')
        print attribute, value
        # tmp_str=value
        # if type(tmp_str)==str:
        #     tmp_str.encode('ascii', 'ignore') # example usage
        # print attribute, tmp_str# example usage

# print data
