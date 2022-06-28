#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright The IETF Trust 2018, All Rights Reserved

from __future__ import unicode_literals, print_function, division

import dict2xml
import io
import json
import lxml
import os
import pdfplumber
import sys

def get_fonts(page):
    fonts = []
    if 'char' in page.objects.keys():
        for obj in page.chars:
            # pdfplumber presents font names like `ROTXYT+Noto-Sans-Cherokee`
            fontname = obj['fontname'].split('+')[1].replace('-', ' ')
            if fontname not in fonts:
                fonts.append(fontname)
    return fonts

def pyobj(filename=None, bytes=None):
    pdffile = io.BytesIO(bytes) if bytes else io.open(filename, 'br')
    reader = pdfplumber.open(pdffile)
    doc = reader.metadata
    pages = []
    for num in range(len(reader.pages)):
        page = reader.pages[num]
        pages.append({
            'text': page.extract_text(),
            'FontFamily': get_fonts(page)})
    pdffile.close()
    doc['Page'] = pages
    return doc

def xmltext(filename=None, obj=None, bytes=None):
    if obj is None:
        obj = pyobj(filename=filename, bytes=bytes)
    return dict2xml.dict2xml(obj, wrap="Document")    

def xmldoc(filename, text=None, bytes=None):
    if text is None:
        text = xmltext(filename=filename, bytes=bytes)
    return lxml.etree.fromstring(text)

def main():
    for filename in sys.argv[1:]:
        if not os.path.exists(filename):
            print('Could not find "%s"' % filename)
        print('File: %s' % filename)
        doc = pyobj(filename)
        with io.open(filename+'.json', 'w', encoding='utf-8') as j:
            json.dump(doc, j, indent=2)
        print('Wrote: %s' % j.name)
        with io.open(filename+'.xml', 'w', encoding='utf-8') as x:
            x.write(xmltext(filename, doc))
        print('Wrote: %s' % x.name)

if __name__ == "__main__":
    main()
