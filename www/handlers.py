# -*- coding: utf-8 -*-

__author__ = 'Suvan Liu'

import re, time, json, logging, hashlib, base64, asyncio

from webframe import get, post

from model import User, Blog, Comment, next_id

@get('/')
async def index(request):
    users = await User.find_all()

    return {
            '__template__': 'test.html',
            'users': users
    }
