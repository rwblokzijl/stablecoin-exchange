from requests_http_signature import HTTPSignatureAuth as HSA

import warnings
from cryptography.utils import CryptographyDeprecationWarning

class HTTPSignatureAuth(HSA):

    def __call__(self, request):
        warnings.filterwarnings("ignore", category=CryptographyDeprecationWarning)
        if "Authorization" in request.headers:
            auth = request.headers["Authorization"]
            req = super(HTTPSignatureAuth, self).__call__(request)
            req.headers["Signature"]=req.headers["Authorization"].split(' ', 1)[1]
            req.headers["Authorization"]=auth
            return req
        else:
            return super(HTTPSignatureAuth, self).__call__(request)

    def add_digest(self, request):
        if request.body:
            request.body=request.body.encode('utf-8')
            super(HTTPSignatureAuth, self).add_digest(request)
        else:
            super(HTTPSignatureAuth, self).add_digest(request)
            request.headers["Digest"] = "SHA-256=47DEQpj8HBSa+/TImW+5JCeuQeRkm5NMpJWZG3hSuFU="
            # Since the message body (payload) is empty, the digest is defaulted to the hash256 of an empty body.

