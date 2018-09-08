# -*- encoding: utf-8 -*-

from pysn import generic

from .detect import detect
from .execute import NONMEM7
from .model import Model

__all__ = ['generic', 'detect', 'Model', 'NONMEM7']
