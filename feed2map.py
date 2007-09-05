import urllib
import urllib2
import pycurl
import StringIO
import BeautifulSoup
import mechanize

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

def curl_get(url):
    ''' Basic auth isn't working for this.  How totally lame.
    So we'll use curl.  Are you happy, urllib2?'''
    out = StringIO.StringIO()
    c = pycurl.Curl()
    c.setopt(c.URL, url)
    c.setopt(c.WRITEFUNCTION,  out.write)
    c.perform()
    c.close()
    
    return out.getvalue()

def feed2latlong(password):
    feed_url = 'http://ccidonor:%s@ccidonor-qa.civicactions.net/v7VILBpo26ww?contribDate=2007-07-01' % urllib.quote(password)
    feed_contents = curl_get(feed_url)
    soup = BeautifulSoup.BeautifulSoup(feed_contents)
    ret = []

    for li in soup('li'):
        date_time, amount, location = li.string.split(',', 2)
        ret.append(location2latlong(location))

    return ret

def main():
    ''' No output if everything works.  That way,
    it's cron-job safe.'''
    try:
        password = open('password').read().strip()
    except:
        print >> sys.stderr, "You must store the password to use in the file called password."
        sys.exit(1)

    outfd = open('results', 'w')
    print >> outfd, feed2latlong(password)

if __name__ == '__main__':
    main()
    
