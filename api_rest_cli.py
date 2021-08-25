import urllib3
import json

DECODE_DATA = {"application/json":json.loads #lambda x:json.loads(x,object_hook=DecodeDateTime)
              }

DEBUG = 1

class Answer(object):
    
    DEBUG = False
    
    def __init__(self,url,code,data,fields={},headers={}):
        self.request = {"url":url,
                        "fields":fields,
                        "headers":headers}
        self.code = code
        self.data = data
        self.debug()
    
    def debug(self):
        if not Answer.DEBUG:
            return
        print("### DEBUG ### :",self.code,self.request)
    
    def __repr__(self):
        return "%i\n%s" % (self.code,json.dumps(self.data,indent=4))
        
class ApiRestCli(object):
    def __init__(self,host,apikey=None,debug=DEBUG,headers={}):
        self.__host = host
        
        self.__apikey = apikey
        self.headers = headers
        if self.__apikey:
            self.headers["apikey"] = self.__apikey
        
        self.__http = urllib3.PoolManager(timeout=urllib3.Timeout(connect=1.0, read=60.0))
        
        Answer.DEBUG = debug

    def reset_http(self):
        self.__http.clear()

    def __enter__(self):
        self.reset_http()
        return self

    def __exit__(self,*_,**__):
        self.reset_http()
        return 0

    def _decode(self,r):
        if "Content-Type" in r.headers:
            return (r.status,DECODE_DATA.get(r.headers["Content-Type"].split(";")[0],lambda x:x)(r.data.decode()))
        else:
            return (r.status,r.data)
    
    def _url(self,path,paras):
        return ('%s%s' % (self.__host,path)) + (paras and "?" + "&".join(["%s=%s" % (str(key),str(value)) for key,value in paras.items()]) or "")
    
    def _request(self,cmd,path,paras={},fields={},headers={}):
        url = self._url(path,paras)
        headers.update(self.headers)
        code,data = self._decode(self.__http.request(cmd,
                                                     url,
                                                     body=fields and json.dumps(fields) or "",
                                                     headers=headers))
        return Answer(url,code,data,fields,headers)
    
    def _get(self,path="",paras={},headers={}):
        return self._request("GET", path,headers=headers)

    def _put(self,path="",paras={},fields={},headers={}):
        return self._request("PUT", path,headers=headers)

    def _patch(self,path="",paras={},fields={},headers={}):
        return self._request("PATCH", path,headers=headers)

    def _post(self,path="",paras={},fields={},headers={}):
        return self._request("POST", path,paras,fields,headers=headers)
    
    def _delete(self,path=""):
        pass
        