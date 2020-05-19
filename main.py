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

  def __eq__(self, item):
    return str(self) == str(item)