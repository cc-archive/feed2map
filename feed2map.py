import urllib
import pycurl
import StringIO
import BeautifulSoup
import bag
import sys
import memoize

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
        ret.append(location2latlong(location))

    return ret

def latlong2table(lats_and_longs):
    out = []
    latlong_bag = bag.bag(lats_and_longs)
    for (lat, long), count in latlong_bag.mostcommon():
        this_row = {'point': '%s,%s' % (lat, long)}
        # FIXME: this_row should do image scaling based on the frequency
        # of occurrence as seen in "count"
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
    
