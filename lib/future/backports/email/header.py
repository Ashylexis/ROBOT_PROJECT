# Copyright (C) 2002-2007 Python Software Foundation
# Author: Ben Gertzfield, Barry Warsaw
# Contact: email-sig@python.org

"""Header encoding and decoding functionality."""
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import
from future.builtins import bytes, range, str, super, zip

__all__ = [
    'Header',
    'decode_header',
    'make_header',
    ]

import re
import binascii

from future.backports import email
from future.backports.email import base64mime
from future.backports.email.errors import HeaderParseError
import future.backports.email.charset as _charset

# Helpers
from future.backports.email.quoprimime import _max_append, header_decode

Charset = _charset.Charset

NL = '\n'
SPACE = ' '
BSPACE = b' '
SPACE8 = ' ' * 8
EMPTYSTRING = ''
MAXLINELEN = 78
FWS = ' \t'

USASCII = Charset('us-ascii')
UTF8 = Charset('utf-8')

# Match encoded-word strings in the form =?charset?q?Hello_World?=
ecre = re.compile(r'''
  =\?                   # litera