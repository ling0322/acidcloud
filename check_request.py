'''
Created on 2012-5-10

@author: ling0322

Part of the following code are from oauth-gae:

A simple OAuth implementation for authenticating users with third party
websites.
@author: Mike Knapp
@copyright: Unrestricted. Feel free to use modify however you see fit. Please
note however this software is unsupported. Please don't email me about it. :)

'''

import urlparse
import userinfo
from hashlib import sha1
from hmac import new as hmac
import webapp2
from urllib import quote as urlquote

def checked_request(f):
    def _handler_function(self, *args, **kwargs):
        url = self.request.url
        method = f.__name__.upper()
        if method not in ('GET', 'POST'):
            raise Exception('invaild http method {0}'.format(method))
        
        if _check_request(url, method) == False:
            raise webapp2.HTTPException(403)
        
        return f(self, *args, **kwargs)
    
    return _handler_function

def encode(text):
    return urlquote(str(text), "~")

def _check_request(request_url, method = 'GET'):
    try:
        if isinstance(request_url, unicode):
            request_url = request_url.encode('utf8')
    
        p = urlparse.urlparse(request_url)
        url = p.scheme + '://' + p.netloc + p.path
        params = {key: value[0] for key, value in urlparse.parse_qs(p.query).items()}
        
        signature = params['oauth_signature']
        del params['oauth_signature']
        user_name = params['oauth_consumer_key']
        secret = userinfo.user_info(user_name)['password']

        # Join all of the params together.
        params_str = "&".join(["%s=%s" % (encode(k), encode(params[k]))
                            for k in sorted(params)])

        # Join the entire message together per the OAuth specification.
        message = "&".join([encode(method), encode(url), encode(params_str)])

        # Create a HMAC-SHA1 signature of the message.
        key = "%s&%s" % (secret, '') # Note compulsory "&".
        key = key.encode('utf-8')
        
        if signature == hmac(key, message, sha1).digest().encode("base64").strip():
            return True
        else:
            return False
    
    except:
        return False
    
def get_user_from_request(request):
    return request.GET['oauth_consumer_key']