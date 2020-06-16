from stablecoin.bank.util.HttpSignatureAuth import HTTPSignatureAuth

import requests

import unittest

class TestHTTPSignatureAuth(unittest.TestCase):

    """Testing HTTPSignatureAuth"""

    def setUp(self):
        self.client_id = "e77d776b-90af-4684-bebc-521e5b2614dd" # example id

        self.key = "-----BEGIN PRIVATE KEY-----\n" \
        "MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC6rJOdlMTR4gxl\n" \
        "EprBPE6ukJOWhDb+DeFU/mR/n+AxMiJNPeEC0u5pabG1gpH9xftqSU7mjTWlHcjU\n" \
        "JukmveayFdk0TCMXb2QQLIw5MG1tbjvp5oKrnLq7wAMOePVETkYNe51kn3ieurAt\n" \
        "lENay4alqQimGHuf/A67osKkVl0jPjD5XilqMvNtaUp1ikfp8RW1OvxE6w4CqUtR\n" \
        "DPOsBZPOFLiccINrvv8pPmI9Kf+kJIlTO2d5bCCZ+XOJRguqx0Ip/b5HtkIiU4kh\n" \
        "xNEZAx2QghjADJ9Nzeuk8oen3SpIXB+LsOfVjx34I3m1NVfG4VPd3Yt7phifEWIP\n" \
        "l8eVlxrrAgMBAAECggEADLWfP0VXuSp4yZDgtHNUsBHr2n2Z+OYdB1pioUXTT8Yo\n" \
        "C7ZA0Z5m2Qp3LPJ82hhWq7/d/Vhz5JAIklkr2pVnVYyjQypD4V6WI3vE+EfRy3eL\n" \
        "4Lru/pwnIo1KJ/wYRtRFdLmL18P7xGLVh+TmSRI+Up0Vl6lnEVdp8WB9fA7dPH7r\n" \
        "fi1l+y1CcLkaxj07ZtD0XIKT573pneemRJXG6y2Njb6tS/9FOEgtJsRfjPyHwK5A\n" \
        "62LIT47GxR2mjWAzMtaekdpfzLldr/F+BzkkldGpettdzee2/Qc4N9+S6RuB4Led\n" \
        "fAFHLpPU1RpD68x0aT5Kg1hMbChylzkepF8aXyNrUQKBgQD2xfXt7iF6fXmaoeMo\n" \
        "o4DRmsG5bS79yHR335NxA6BBnSY6wEKTyIhU0b1JWhR+OhRJRgDaTxClkXHZ9Bya\n" \
        "c3egcnWeANHP3nkKXUq2ePV3Zakvt7Z2X9XrjmJmE/sC40/q0EkgUZoQAzBe6enF\n" \
        "xZP+yHtU0DTIvTECN83imbgnXwKBgQDBp11v5BKG7/Ze98w0uuLUmayHcWQW5KW6\n" \
        "Eh4V8BXf1DP36XUfvfvylADKx//GpuD/Wu3rAj+UDeYOOKICFOXBIWOKsuq723sk\n" \
        "a7Xl5rke90cHe3SEObCObRgPo1mp2VCyvus2Bl28xvzqBejC5477Qfk7zp61c7x3\n" \
        "ZSvYdm6z9QKBgE2HmGJuRFplfYUVg3bLF7fCtUZ6hR76kYzv0zTYfMrggphGuyQP\n" \
        "BrYPRzb6dCHMQX9b3Py5hnNeJLTjOvFTgawJCebgPwrdzI1zDfwSOJyQdf0l7M94\n" \
        "AI+HJmcHs/8OR5dwZOkgehS5y8KmHuohzwNnHUhiOZMvzWvy+F5PCUplAoGAIjJg\n" \
        "4KJg1y1Gz2xoxiL+bVaZze0rJJPJ5DrQz0TvR/BcIPo78ZgGBsc2AJkixLyxXMZ8\n" \
        "3xQtkAKITpiXm1B/ZgR0ZIjFxNi0PTE8FNYSeLJn+51EbRkW4X/IUPKioci7ZGUs\n" \
        "egTTxsNI5DaY7NohOKNk1Lfe9OH0NQ1LmdUIJYUCgYEArEpa96YYAZ3M3RAuUCDm\n" \
        "tvyL/4z4UuUoRF7nvl4H2Qak9BPReTd+HNSiNUK/3v86O08is2zDX4erC0wdmHCP\n" \
        "aQUUP5GD9YP/EGWPIUSDwFzYgIENv5OUnIFW6OIPQ+cmCjNUxmdI6rMpCXRhKItv\n" \
        "NpvvaSj1dWcnWSbCkxA+Yv8=\n" \
        "-----END PRIVATE KEY-----\n"

        self.cert_tls = "-----BEGIN CERTIFICATE-----\n" \
        "MIIDZzCCAk+gAwIBAgIJAN6l06/9DUciMA0GCSqGSIb3DQEBCwUAMEoxEzARBgNV\n" \
        "BAoMClNhbXBsZSBPcmcxFjAUBgNVBAsMDUlUIERlcGFydG1lbnQxGzAZBgNVBAMM\n" \
        "EmV4YW1wbGVfY2xpZW50X3RsczAeFw0xODA1MDkwODQ3MDJaFw0yMTA1MTMwODQ3\n" \
        "MDJaMEoxEzARBgNVBAoMClNhbXBsZSBPcmcxFjAUBgNVBAsMDUlUIERlcGFydG1l\n" \
        "bnQxGzAZBgNVBAMMEmV4YW1wbGVfY2xpZW50X3RsczCCASIwDQYJKoZIhvcNAQEB\n" \
        "BQADggEPADCCAQoCggEBAKr+xEHPAguqBBnvIUJVy3DImJOAD7kdg7NASgJi9iId\n" \
        "6d++bWtBPvFqzT0M0NjvdzlhHkkDufTBmdHfjT3gjapqv0pHidmbuOofE+20wsyJ\n" \
        "Ug4KBAO7NeR4LXfrsH+bhU5XyK817VUQ5+BIYk0JX4uFWR+tMZZFDzHQkT38TjMQ\n" \
        "Y7OY2xXZ2NgEWcqCTj0mSX48j5ECm7nKa6v83HnKe1qvKyHWqvhsecl4y1YPeLXJ\n" \
        "mCazZ69/EyGxOEw4MkFOaMrYHpvRrrqWnPe3e/OPwmeWJlVaFv9D8troqyNX65zs\n" \
        "KlVlMQFU0q3fWWDIvv0NDccVdZqtLM+7aUKp5BWWknMCAwEAAaNQME4wHQYDVR0O\n" \
        "BBYEFHF8wEth05uM+UTkNkw13hPU6uddMB8GA1UdIwQYMBaAFHF8wEth05uM+UTk\n" \
        "Nkw13hPU6uddMAwGA1UdEwQFMAMBAf8wDQYJKoZIhvcNAQELBQADggEBAAv+LMrG\n" \
        "H1zgoBRaYZXn4NPCLGKd3d03MlvTZ1zzmFipB8PyrscSdKOzY30tD+JrKjgOjX20\n" \
        "45HuUCEG/KgqlxdMnCLcclZXMvnWjfh4iS6rdPtTp1svQKtCioClful1W5gfPYmW\n" \
        "JOr1/4YNNrvg1eNr6C3xTvncOhR1Tc7u4NX5xKsLGLIn+Qnxvvy/0+Bww6/smFkW\n" \
        "iH6eeJEqJEk9KihSFXli2Os3ZWt9ojIMqhbgV+JoPuv7CeaQPoq1kGkwlkXFhxpI\n" \
        "VLDlVMN1DB/bf64rusIxSn+5ebIpk7w0Mjjupj4Qs9Jshx5b9li4C88hFxVDU+If\n" \
        "gx9kFIUgtVBAKw4=\n" \
        "-----END CERTIFICATE-----\n"

        self.key_tls = "-----BEGIN PRIVATE KEY-----\n" \
        "MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCq/sRBzwILqgQZ\n" \
        "7yFCVctwyJiTgA+5HYOzQEoCYvYiHenfvm1rQT7xas09DNDY73c5YR5JA7n0wZnR\n" \
        "34094I2qar9KR4nZm7jqHxPttMLMiVIOCgQDuzXkeC1367B/m4VOV8ivNe1VEOfg\n" \
        "SGJNCV+LhVkfrTGWRQ8x0JE9/E4zEGOzmNsV2djYBFnKgk49Jkl+PI+RApu5ymur\n" \
        "/Nx5yntarysh1qr4bHnJeMtWD3i1yZgms2evfxMhsThMODJBTmjK2B6b0a66lpz3\n" \
        "t3vzj8JnliZVWhb/Q/La6KsjV+uc7CpVZTEBVNKt31lgyL79DQ3HFXWarSzPu2lC\n" \
        "qeQVlpJzAgMBAAECggEAc45iENsVVc6aoPASeOLD7j8RpTR466+/bea3XS+FiH7Q\n" \
        "q0zkYwQfxkRX2LcNeF00JAm2zr7+7yHakpNRvww+kHk9NrRruyxaZZWFATIUJudy\n" \
        "FVy9Y8wjWnfAuncDuujdyJjYXVfDQKaBHPetvsPj1sTR+u8vQI8A+rgpP0t/iU+h\n" \
        "nw5ILuBJPFO/UJMq3v5YMV1GYqQ8ZpiGJHn50yl/neqcDbO05FKmXzE2ES1cnAhJ\n" \
        "BUAcK5DxXMiSkJloG/4Qy/rNPNXwN+eDTuPAfdaDLPHanR3UiUB77HFqNt3UJhLB\n" \
        "bFAItfg1O0SQgklLmhEj3aEyqFQ14o70syWtfBWS4QKBgQDguFl6jtOD1OHdBY1l\n" \
        "zM6Rtw2lYzkgNX5eRq8t8GuyQaKsVP8Kxzhk9DBw7a6toF+NgVP6YN9/DvnF8GMP\n" \
        "kxprr8/sQ3mN8YUSLdUoLUTZgHbAKIYCDlr9u4VSGHcmeCJf8N6pM9rChqauNJ/y\n" \
        "4AXR0UfHRY+gPijEPlKRYtKFIwKBgQDCy/00KdJidw0gMoSUFNiq6zPu9abaXAtJ\n" \
        "WR45dpsWBjufIIqMhZ7QmT16pEmdqRIJmL994vvHcAzUfoaMoSlyYVDkp8Hzs12I\n" \
        "jhxLef/gcB0VdF4cDle9eJqP+1ioUANks3CuXkQTIJTBKsXzUwRYMSvy6WVlXN6n\n" \
        "J7DTdy7acQKBgQC+N+4uCwZKGoJR5+hH2rSkrbHUZIgvlnhwbx7MIS3Yhyye+Zel\n" \
        "1PsMoZL7lIX/HLilfGrMjwHAeLm+7nu77EY6D2lOUdNr7pw4xikfyCn2foKGqAa/\n" \
        "aM1m6DuzQVhibOCUG70utuEfNoGTBqK6IR1r/N3odR5dgyBY9XRI8sDGxwKBgBpS\n" \
        "pmyeGifkHonzSacZCg5Oqj3oRBvNxFitCkCJnntjbDsckpxakhNuIbio6qm7ZwyU\n" \
        "74t7WLqikZlFX7kxLgCe1eeQI81it4j0ay5n1gPmIof7qZvw9DpOSdSbCmf0KAE7\n" \
        "nkZxxpEvHercdNNkrHmea2nv0BvaaNv9qQ9qU5KBAoGAT94i+1Yaa9ZZebN1TOGa\n" \
        "A4+7KpdVEJlklwRmPV/tvMJVlrJVimX/r6z906qd2JrsBjT3l9glj20w3t4LaSkl\n" \
        "z5snXhoJ6BJXpHfYXLWRayfI7GyZr15AqnS2YyKBOQCNiFukQeQRayLWClNjLJNI\n" \
        "lEeKMgLqx81YVbuPXztPfxo=\n" \
        "-----END PRIVATE KEY-----\n"

    def test_get_sign(self):
        auth   = HTTPSignatureAuth(algorithm="rsa-sha256",
                headers=[ '(request-target)', 'date', 'digest' ],
                key=self.key.encode("utf-8"), key_id=self.client_id)

        headers = {
                'Authorization': 'Bearer sdfasdf...'
                }
        req = requests.get(url='https://www.example.com', headers=headers, auth=auth)
        self.assertTrue("Authorization" in req.request.headers)
        self.assertTrue("Digest" in req.request.headers)
        self.assertTrue("Date" in req.request.headers)
        self.assertTrue("Signature" in req.request.headers)

    def test_post_sign(self):
        auth   = HTTPSignatureAuth(algorithm="rsa-sha256",
                headers=[ '(request-target)', 'date', 'digest' ],
                key=self.key.encode("utf-8"), key_id=self.client_id)

        headers = {
                'Authorization': 'Bearer sdfasdf...'
                }
        body = "Testing string"
        req = requests.post(url='https://www.example.com', headers=headers, auth=auth, data=body)
        self.assertTrue("Authorization" in req.request.headers)
        self.assertTrue("Digest" in req.request.headers)
        self.assertTrue("Date" in req.request.headers)
        self.assertTrue("Signature" in req.request.headers)
        self.assertEqual(req.request.headers["Digest"], "SHA-256=qykbZcCWKKhzI4bEmiyi8VsY22+ccm7jxZ/wct4nD5o=")

