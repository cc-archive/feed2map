import string
import csv
import urllib
import pycurl
import StringIO
import BeautifulSoup
import bag
import sys
import memoize

def curl_get(url):
    class Curl_appendee:
        def __init__(self):
            self.contents = ''
        def body_callback(self, buf):
            self.contents += buf

    c_a = Curl_appendee()
    curling = pycurl.Curl()
    curling.setopt(curling.URL, url)
    curling.setopt(curling.WRITEFUNCTION, c_a.body_callback)
    curling.perform()
    curling.close()

    return c_a.contents
        

@memoize.memoize
def location2latlong(s):
    try:
        return location2latlong_real(s)
    except:
        city, state, country = s.rsplit(',', 2)
        try:
            # uh, who knows?  Throw away the state.
            return location2latlong_real(','.join([city, country]))
        except:
            # uh, try just the country
            return location2latlong_real(country)

def location2latlong_real(s):
    args = {'appid': 'cc-location-feed', 'location': s}
    reslut = curl_get('http://local.yahooapis.com/MapsService/V1/geocode?' + 
                      urllib.urlencode(args))
    soup = BeautifulSoup.BeautifulSoup(reslut)
    
    # No error handling below.  If any of this fails, there's something terribly
    # wrong, and a human will have to come by anyway.
    lat = float(soup('latitude')[0].string)
    long = float(soup('longitude')[0].string)
    return (lat, long)

def csv2dicts(csv_fd):
    cols = ['name', None, 'date', 'location', 'attending', 'url']
    csv_obj = csv.reader(csv_fd)
    ret = []
    for row in csv_obj:
        my_data = {}
        for (i, value) in enumerate(row):
            # if i >= len(cols), we ditch
            if i >= len(cols):
                continue
            label = cols[i]
            if label:
                # special date hack
                if label == 'date':
                    value = value.split('T')[0] # is there a better way to parse W3C xsd:date values?
                my_data[label] = value
        ret.append(my_data)
    return ret

def enrich_dicts_with_latlong(list_o_dicts, human_readable_location_field='location'):
    ret = []
    for bag_o_data in list_o_dicts:
        my_data = bag_o_data.copy()
        if human_readable_location_field in bag_o_data:
            my_data['_coordinates'] = ','.join(map(str, location2latlong(my_data[human_readable_location_field])))
        ret.append(my_data) 
    return ret

def dicts2latlong(d):
    ret = []
    for row in d:
        location = row['location']
        try:
            if location.replace(',', '').replace(' ', ''):
                ret.append(location2latlong(location))
        except:
            print "That's weird, I can't place", location, "on the map with Yahoo."
            raise
        #else:
        #    print >> sys.stderr, li, 'was useless'

    return ret

def icon(data):
    _icon = {'Yes': 'http://labs.creativecommons.org/~paulproteus/pin_green_h=50.png',
            'No':  'http://labs.creativecommons.org/~paulproteus/pin_green_h=20.png'}
    return _icon[
        data['attending']]

def enriched_data2table(enriched):
    ret = ''
    # Look ma, I'm unsafe in every which way!
    header = '\t'.join(['point', 'title', 'icon', 'iconSize', 'iconOffset', 'description'])
    TEMPLATE_STRING = '\t'.join(['$_coordinates', '$name', '$icon', '56,20', '-28,-10'])
    TEMPLATE_STRING += '\t' + '''<p>$location</p> <p>$date</p> <p><a href="$url">more info</a></p>'''
    TEMPLATE = string.Template(TEMPLATE_STRING)
    ret += header + '\n'

    for row in enriched:
        row['icon'] = icon(row)
        ret += TEMPLATE.substitute(row) + '\n'
    return ret

def main():
    ''' No output if everything works.  That way,
    it's cron-job safe.'''
    try:
        csv_fd = open('input')
    except:
        print >> sys.stderr, "You must store the feed to use in the file called input."
        print >> sys.stderr, "You might want to set up a cron job to update that file every few whatevers."
        sys.exit(1)

    data = csv2dicts(csv_fd)
    enriched = enrich_dicts_with_latlong(data)
    table = enriched_data2table(enriched)
    print table

if __name__ == '__main__':
    main()
    
