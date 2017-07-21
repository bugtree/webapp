# -*- coding: UTF-8 -*-

import time
import uuid
from orm import Model, StrField, IntField, FltField, BoolField, TextField

def next_id():
    return "%015d%s000" % (int(time.time() * 1000), uuid.uuid4().hex)

class User(Model):
    __table__  = "users"

    id = StrField(ddl="varchar(50)", pkey=True, deft=next_id)
    email = StrField(ddl="varchar(50)")
    password = StrField(ddl="varchar(50)")
    admin = BoolField()
    name = StrField(ddl="varchar(50)")
    image = StrField(ddl="varchar(500)")
    created_at = FltField(deft=time.time)

class Blog(Model):
    __table__ = "blogs"

    id = StrField(ddl="varchar(50)", pkey=True, deft=next_id)
    user_id = StrField(ddl="varchar(50)")
    user_name = StrField(ddl="varchar(50)")
    user_image = StrField(ddl="varchar(500)")
    name = StrField(ddl="varchar(50)")
    summary = StrField(ddl="varchar(200)")
    content = TextField()
    created_at = FltField(deft=time.time)

class Comment(Model):
    __table__ = "comments"

    id = StrField(ddl="varchar(50)", pkey=True, deft=next_id)
    blog_id = StrField(ddl="varchar(50)")
    user_id = StrField(ddl="varchar(50)")
    user_name = StrField(ddl="varchar(50)")
    user_image = StrField(ddl="varchar(500)")
    content = TextField()
    created_at = FltField(deft=time.time)
