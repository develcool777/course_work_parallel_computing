import asyncio
import math
import os
import re
from threading import Thread
import time


class Lexema:
  def __init__(self, text, frequence = 0, docIds = [], raiting = 0):
    if type(text) != str or len(text) < 1:
      raise Exception('Lexema(text as not str) undefind')
    if type(frequence) != int:
      raise Exception('Lexema(frequence as not int) undefind')
    if type(docIds) != list:
      raise Exception('LexemaList(docIds as not list) undefind')
    self.text = text
    self.frequence = frequence
    self.docIds = list(set(docIds))
    self.docIds.sort()

  def __repr__(self):
    return 'Lexema( "{0}"/{1}/{2} )'.format(self.text, self.frequence, self.docIds)

  def __add__(self, item):
    if self.text != item.text:
      raise Exception('Lexema(A) + Lexema(B): undefind for diff A and B')
    return Lexema(self.text, self.frequence + item.frequence, [*self.docIds, *item.docIds])


class LexemaList:
  def __init__(self, items = []):
    if type(items) != list:
      raise Exception('LexemaList(not list) undefind')
    self.items = list(filter(lambda item: type(item) == Lexema, items))
    self.items.sort(key = lambda l: l.text)

  def __repr__(self):
    return ', \n'.join([repr(i) for i in self.items])

  def __add__(self, items):
    a = dict([[l.text, l] for l in self.items])
    b = dict([[l.text, l] for l in items.items])
    ka = list(a.keys())
    kb = list(b.keys())
    K = set(ka + kb)
    def merge(k, a, b):
      if k in a and k in b:
        return a[k] + b[k]
      elif k in a:
        return a[k]
      elif k in b:
        return b[k]
      else:
        return None
    return LexemaList([merge(k, a, b) for k in K])

  def __eq__(self, items):
    return str(self) == str(items)

class Doc:
  sequenceId = 1

  def __init__(self, file):
    if type(file) != str:
      raise Exception('Doc(file as not str) undefined')
    try:
      f = open(self.path(file), 'r')
      self.file = file
      self.docId = Doc.sequenceId
      Doc.sequenceId += 1
    except IOError:
      raise Exception('Doc(file not exists)')
    finally:
      f.close()

  def path(self, file):
    return os.path.dirname(__file__) + '/' + file

  def data(self):
    f = open(self.path(self.file), "r")
    fdata = f.read()
    f.close()
    ldata = fdata.lower()
    sdata = re.split('(?:[\s\.\,\!\?\;]|<br[\s]*/>|"|[\d]*/[\d]*)', ldata)
    data = filter(lambda d: len(d), sdata)
    D = dict()
    for d in data:
      if d in D:
        D[d] += 1
      else:
        D[d] = 1        
    data = map(lambda d: Lexema(*d, docIds = [self.docId]), D.items())
    data = list(data)
    data = LexemaList(data)
    return data

  def __repr__(self):
    return 'Doc(id={id}, file={file}, path={path})'.format(file=self.file, id=self.docId, path=self.path(self.file))