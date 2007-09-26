## NOTE:
## This code doesn't get used.  Nathan Yergler wrote something instead
## that we do use.

import feed2map

PASSWORD=open('password').read().strip()

url = 'http://ccidonor:%s@ccidonor.civicactions.net/v7VILBpo26ww?contribDate=2007-06-12' % PASSWORD

url_data = feed2map.curl_get(url)
data = feed2map.feed2dicts(url_data)
value = sum( [float(datum['amount']) for datum in data] )

PRE_CIVIC_ACTION=12250.96
print PRE_CIVIC_ACTION + value

