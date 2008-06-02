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
        

def scale_image(dimensions, number):
    # What scaling strategy to use?
    # For now, just multiply by number * 0.5 since the numbers are so small.
    # This way, 1 -> 1/2 size, 2 -> full size, 3 -> 1.5 size, etc.
    return [int(dim * number * 0.5) for dim in dimensions]

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

# Don't need this for now; using full precision.
def truncate_float(precision, float):
    scale = int(1/precision)
    return int(float * scale) * 1.0 / scale

def latlong2table(lats_and_longs):
    out = []
    latlong_bag = bag.bag(lats_and_longs)
    max_icon_height = 50
    
    for (lat, long), count in latlong_bag.mostcommon():
        count += 1 # lol
        my_icon_height = int(  min( (10 * count), 50)      )
        my_icon_width  = int( (140.0 / 50) * my_icon_height )
        this_row = dict(lat='%f' % lat,
                        lon='%f' % long,
                        icon = 'http://tilecache.creativecommons.org/pins/pin_green_h=%d.png' % my_icon_height,
                        iconSize='%d,%d' % (my_icon_width, my_icon_height))
        out.append(this_row)
    return out

def format_table(table):
    if not table:
        return '' # if the table is empty, nothing to do
    # inspect for keys

    first = table[0]
    our_keys = first.keys()

    # Store header row
    first_line = '\t'.join(our_keys)
    out_lines = [first_line]

    # Store data rows
    for row in table:
        out_lines.append('\t'.join([row[key] for key in our_keys]))

    return '\n'.join(out_lines)


def main():
    ''' No output if everything works.  That way,
    it's cron-job safe.'''
    try:
        feed_contents = open('input').read()
    except:
        print >> sys.stderr, "You must store the feed to use in the file called input."
        print >> sys.stderr, "You might want to set up a cron job to update that file every few whatevers."
        sys.exit(1)

    print format_table(latlong2table(dicts2latlong(feed2dicts(feed_contents))))

if __name__ == '__main__':
    main()
    
