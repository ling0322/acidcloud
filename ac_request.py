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

from __future__ import unicode_literals
from hashlib import sha1
from hmac import new as hmac
from random import getrandbits
from time import time
from urllib import urlencode
from urllib import quote as urlquote
import config
import httplib2
import re
from lava_potion import *

def prepare_request(url, token="", secret="", consumer_secret="", consumer_key="", 
                    additional_params=None, method='GET', t=None, nonce=None):
    """Prepare Request.

    Prepares an authenticated request to any OAuth protected resource.

    Returns the payload of the request.
    """

    def encode(text):
        return urlquote(str(text), "~")

    params = {
        "oauth_consumer_key": consumer_key,
        "oauth_signature_method": "HMAC-SHA1",
        "oauth_timestamp": t if t else str(int(time())),
        "oauth_nonce": nonce if nonce else str(getrandbits(64)),
        "oauth_version": "1.0"
    }

    if token:
        params["oauth_token"] = token

    if additional_params:
        params.update(additional_params)

    for k,v in params.items():
        if isinstance(v, unicode):
            params[k] = v.encode('utf8')

    # Join all of the params together.
    params_str = "&".join(["%s=%s" % (encode(k), encode(params[k]))
                            for k in sorted(params)])

    # Join the entire message together per the OAuth specification.
    message = "&".join([encode(method), encode(url), encode(params_str)])

    # Create a HMAC-SHA1 signature of the message.
    key = "%s&%s" % (consumer_secret, secret) # Note compulsory "&".
    
    key = key.encode('utf-8')
    signature = hmac(key, message, sha1)
    digest_base64 = signature.digest().encode("base64").strip()
    params["oauth_signature"] = digest_base64

    # Construct the request payload and return it
    return urlencode(params)



def ac_request(url, data = None, params = None, method = None, headers = None):
    if method == None:
        method = 'GET' if data == None else 'POST'
        
    flag = False
    failed_count = 0
    http = httplib2.Http()
    signed_url = url + '?' + prepare_request(
        url = url, 
        token = config.USER_NAME, 
        secret = config.PASSOWRD,
        consumer_key = config.CONSUMER_KEY,
        consumer_secret = config.CONSUMER_SECRET,
        additional_params = params, 
        method = method)
    log(config.ACREQUEST_LOG, "request to '{0}'".format(signed_url), __name__)
    while flag == False:
        try:
            data = encode_if_necessary(data)
            signed_url = encode_if_necessary(signed_url)
            method = encode_if_necessary(method)
            if headers != None:
                headers = {encode_if_necessary(key): encode_if_necessary(value) 
                           for key, value in headers.items()}
            resp, content = http.request(signed_url, method, data, headers)
            if re.match('(2|3)..', resp['status']) == None:
                raise Exception('failed to fetch {0}'.format(signed_url))
            flag = True
        except ItemNotFoundException as e:
            failed_count += 1
            log(config.ACREQUEST_LOG, "request to '{0}' failed {1} times".format(url, failed_count), __name__)
            if failed_count == config.RETRY_TIMES:
                raise e
            
    return resp, content