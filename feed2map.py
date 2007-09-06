import urllib
import pycurl
import StringIO
import BeautifulSoup
import bag
import sys
import memoize

def scale_image(dimensions, number):
    # What scaling strategy to use?
    # For now, just multiply by number * 0.5 since the numbers are so small.
    # This way, 1 -> 1/2 size, 2 -> full size, 3 -> 1.5 size, etc.
    return [int(dim * number * 0.5) for dim in dimensions]

@memoize.memoize
def location2latlong(s):
    args = {'appid': 'cc-location-feed', 'location': s}
    reslut = curl_get('http://local.yahooapis.com/MapsService/V1/geocode?' + 
                      urllib.urlencode(args))
    soup = BeautifulSoup.BeautifulSoup(reslut)
    
    # No error handling below.  If any of this fails, there's something terribly
    # wrong, and a human will have to come by anyway.
    lat = float(soup('latitude')[0].string)
    long = float(soup('longitude')[0].string)
    return (lat, long)

def feed2latlong(feed_contents):
    soup = BeautifulSoup.BeautifulSoup(feed_contents)
    ret = []

    for li in soup('li'):
        date_time, amount, location = li.string.split(',', 2)
        if location.replace(',', '').replace(' ', ''):
            ret.append(location2latlong(location))
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
    base_iconsize = (21, 25)
    for (lat, long), count in latlong_bag.mostcommon():
        my_iconsize = map(str, scale_image(base_iconsize, count))
        this_row = dict(lat='%f' % lat,
                        lon='%f' % long,
                        iconSize = ','.join(my_iconsize))
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

    print format_table(latlong2table(feed2latlong(feed_contents)))

if __name__ == '__main__':
    main()
    
