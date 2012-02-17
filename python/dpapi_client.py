
import json, hashlib
import urllib.request, urllib.parse, urllib.error

__author__  = "Data Publica"
__email__   = "guillaume.lebourgeois@data-publica.com"
__version__ = "b1.0"

class Query:
  """
  Represent a DPAPI Query object
  """

  def __init__(self, apikey, passwd, dataref, tablename, format="json", limit=50, offset=0):
    """
    param: apikey: Developper API Key
    param: passwd: Developper password
    param: dataref: Data set reference number 
    param: tablename: Data table name
    param: format: response format (json, csv, excel)
    param: limit: results limit
    param: offset: results offset
    """
    self.apikey = apikey
    self.passwd = passwd
    self.dataref = dataref
    self.tablename = tablename
    self.format=format
    self.limit=limit
    self.offset=offset
    
    self.filters = ""
    self.str_q = ""

  def add_filters(self, filters):
    """
    Sets filters for the current query
    param: filters: a str representation of a dictionary of filters
    """
    self.filters = filters

  def to_url(self, domain):
    """
    Returns a string representation of the query
    param: domain: the domain to be queried
    """
    s = self._sign(domain)
    
    return self._build_url( domain, s )

  def _build_url(self, domain, signature):
    """
    Builds a complete URL under the form of a str
    param: domain: the domain to be queried
    param: signature: a generated signature for this query
    """
    #filter,format,key,limit,offset,reference,[signature],tablename
    url = domain + self.dataref + "/" + self.tablename + "/content?"
    params = {"filter": self.filters, "format": self.format, \
	      "key": self.apikey, "limit": self.limit, \
	      "offset": self.offset, "signature": signature}

    url += urllib.parse.urlencode( params )
    
    return url
    
  def _sign(self, domain):
    """
    Generates the query signature.
    param: domain: the domain to be queried
    """
    s = domain
    s += self.dataref + "/" + self.tablename + "/content"

    if len(self.filters) > 0:
      s += ",filter=" + self.filters

    s += ",format=" + self.format
    s += ",key="  + self.apikey
    s += ",limit=" + str(self.limit)
    s += ",offset=" + str(self.offset)
    s += "," + self.passwd
    
    h = hashlib.sha1()
    h.update( s.encode('utf-8' ) )
    signature = h.hexdigest()

    return signature

class DPAPIClient:
  """
  This class is a client to the Data Publica API V1.
  It is Python 3.x compliant.
  Documentation : http://integration.data-publica.com/content/api
  """

  def __init__(self, apikey, passwd, base_url="http://api.data-publica.com/v1/"):
    """
    param: apikey: Developper API Key
    param: passwd: Developper password
    """
    self.base_url = base_url
    self.apikey = apikey
    self.passwd = passwd

    # Current query
    self.q = None

  def prepare_query(self, dataref, tablename, format="json", limit=50, offset=0):
    """
    param: dataref: Data set reference number 
    param: tablename: Data table name
    param: format: response format (json, csv, excel)
    param: limit: results limit
    param: offset: results offset
    """
    self.q = Query(self.apikey, self.passwd, dataref, tablename, format="json", limit=50, offset=0)

  def add_filters(self, filters):
    """
    Adds filter respecting the DP API Syntax.
    For example : '{"index.name": "Séquestrations"}'
    param: filters: A dictionary containing filters
    """
    self.q.add_filters( json.dumps( filters ) )

  def execute_query(self):
    """
    return: a tuple (httpcode, data) where data is a Python dictionary
    """
    url = self.q.to_url(self.base_url)

    try:
      ans = urllib.request.urlopen( url )
    except urllib.error.HTTPError as e:
      return (e.getcode(), {"data": {}})
    
    data = json.loads( ans.read().decode('utf-8') )
    code = ans.getcode()

    return (code, data)
    

if __name__ == "__main__":
  """
  Stand alone execution as an example of use.
  You need to provide your own apikey, and associated 
  password, the ones presented below are fakes.
  """
  client = DPAPIClient("d051bf1ddf82f79c6af34f7f4e59707f081296ad", \
                       "d69d14f8d65acbfdfc03220d243fce04")
  
  client.prepare_query("12244", "data_table")
  client.add_filters({"index.name":"Recels"})
  httpcode, data = client.execute_query()

  print( "HTTP Code : " + str(httpcode) + " returned " + str(len(data["data"])) + " elements." )




