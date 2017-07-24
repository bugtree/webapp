# -*- coding: utf-8 -*-

__author__ = 'Suvan Liu'

import re, time, json, logging, hashlib, base64, asyncio

from webframe import get, post

from model import User, Blog, Comment, next_id

#@get('/')
#async def index(request):
async def xx(request):
    users = await User.find_all()

    return {
            '__template__': 'test.html',
            'users': users
    }

@get('/')
async def index(request):
    summary = 'long long ago, there is a bird, her name is BuGu. One day, she fly to my dream.'
    
    blogs = [
        Blog(id='1', name="Test Blog", summary=summary, created_at=time.time() - 180),           
        Blog(id='2', name="Somethind New", summary=summary, created_at=time.time() - 60*60*5),
        Blog(id='3', name="Learn Python", summary=summary, created_at=time.time() - 60*60*24*3)
    ]
    
    return {
            '__template__': 'blogs.html',
            'blogs': blogs 
    }
