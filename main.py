#!/usr/bin/env python3

import math
from multiprocessing import Process, Queue
import os
import re
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
    self.items = items
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
  DOCId = 1

  def __init__(self, file):
    if type(file) != str:
      raise Exception('Doc(file as not str) undefined')
    try:
      f = open(self.path(file), 'r')
      self.file = file
      self.docId = Doc.DOCId
      Doc.DOCId += 1
    except IOError:
      raise Exception('Doc(file not exists)')
    finally:
      f.close()

  def path(self, file):
    return os.path.dirname(__file__) + '/' + file

  def data(self):
    f = open(self.path(self.file), "r", encoding='utf-8')
    fdata = f.read()
    f.close()
    ldata = fdata.lower()
    sdata = re.split('(?:[\s\.\,\!\?\;\{\}\$*\%\&\:\)\(\+\-\[\]\@]|<br[\s]*/>|"|\'|`|[\d]*/[\d]*)|#[\d]*|[\d]', ldata)
    data = filter(lambda d: len(d) and not(d in []), sdata)
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

def each(pattern, indexes, raitings = range(0, 11)):
  if type(pattern) != str:
    raise Exception('each(pattern as not str) undefined')
  docs = []
  for index in indexes:
    for raiting in raitings:
      try:
        file = pattern.format(index = index, raiting = raiting)
        doc = Doc(file)
        docs += [doc]
      except Exception as e:
        pass
  return docs
 
def testNegEach(indexes = range(3250, 3501)):
  return each('test:neg/{index}_{raiting}.txt', indexes)

def testPosEach(indexes = range(3250, 3501)):
  return each('test:pos/{index}_{raiting}.txt', indexes)

def trainNegEach(indexes = range(3250, 3501)):
  return each('train:neg/{index}_{raiting}.txt', indexes)

def trainPosEach(indexes = range(3250, 3501)):
  return each('train:pos/{index}_{raiting}.txt', indexes)

def trainUnsupEach(indexes = range(13000, 14001)):
  return each('train:unsup/{index}_{raiting}.txt', indexes)

def testAll(indexes = range(0, 10000)):
  return each('test:all/{index}_{raiting}.txt', indexes)


def syncRun(docs):
  L = LexemaList([])
  start = time.time()
  for doc in docs:
    L = L + doc.data()
  end = time.time()
  diff = end - start
  return (L, diff,)

class MyProcess(Process):
  def __init__(self, docs, q):
    Process.__init__(self)
    self.docs = docs
    self.q = q
  
  def run(self):
    L = LexemaList([])
    for doc in self.docs:
      L = L + doc.data()
    self.q.put(L)
    return 0

def asyncRun(docs, CPU = 2):
  L = LexemaList([])
  D = docs
  length = math.ceil(float(len(D))/CPU)
  dd = [D[i*length:(i+1)*length] for i in range(CPU)]
  Q = [Queue() for i in range(len(dd))]
  P = [MyProcess(dd[i], Q[i]) for i in range(len(dd))]
  for t in P:
    t.start()
  for t in P:
    t.join(timeout=0.9)
  for q in Q:
    r = q.get()
    if not(type(r) == LexemaList):
      continue
    L = L + r
  return L

def run(docs, CPU = 2, title = 'run'):
  L1, t1 = syncRun(docs)
  start = time.time()
  L2 = asyncRun(docs, CPU)
  end = time.time()
  t2 = end - start
  format = {
    'title': title,
    't1': t1,
    't2': t2,
    'dt': t1 - t2,
    'L1': L1,
    'L2': L2,
    'eq': [L1 == L2],
  }
  print("{title}: ( sync={t1:0.3f}, async={t2:0.3f}, dt={dt:0.3f}, eq={eq} )".format(**format))
  # print(repr(L1))


def main(CPU = 2):
  docsTestNeg    = testNegEach()
  # docsTestPos    = testPosEach()
  # docsTrainNeg   = trainNegEach()
  # docsHalf       = [*docsTestPos, *docsTestNeg]
  # docsTrainPos   = trainPosEach()
  # docsTrainUnsup = trainUnsupEach()
  # docsAll        = [*docsTestNeg, *docsTestPos, *docsTrainNeg, *docsTrainPos, *docsTrainUnsup]
  # docsReallyAll  = testAll()

  run(docsTestNeg, CPU = CPU, title = 'test:neg')
  # run(docsTestPos, CPU = CPU, title = 'test:pos')
  # run(docsTrainNeg, CPU = CPU, title = 'train:neg')
  # run(docsTrainPos, CPU = CPU, title = 'train:pos')
  # run(docsTrainUnsup, CPU = CPU, title = 'train:unsup')
  # run(docsHalf, CPU = CPU, title = '500')
  # run(docsAll, CPU = CPU, title = 'all 2000')
  # run(docsReallyAll, CPU = CPU, title = 'all 50000')

if __name__ == "__main__":
    main(CPU = 2)