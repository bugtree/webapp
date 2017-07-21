# -*- coding:UTF-8 -*-
# ORM -- Object Relational Mapping

import logging, aiomysql, asyncio

logging.basicConfig(level=logging.INFO)

def log_sql(sql, argvs):
    logging.info("SQL: %s(arg:%s)" % (sql, argvs))

async def create_pool(loop, **kw):
    logging.info("create database connection pool....")
    global __pool
    __pool = await aiomysql.create_pool(

#        host = kw.get("host", "localhost")
#            ||
#           \||/
#            \/
#        host = kw["host"]
#        if host == None
#            host = "localhost"

        host = kw.get("host", "localhost"),
        port = kw.get("port", 3306),
        user = kw["user"],
        password = kw["password"],
        db = kw["db"],
        charset = kw.get("charset", "utf8"),
        autocommit = kw.get("autocommit", True),
        maxsize = kw.get("maxsize", 10),
        minsize = kw.get("minsize", 1),
        loop = loop
     )

async def select(sql, args, size=None):
    log_sql(sql, args)
    global __pool

    with (await __pool) as conn:
        cur = await conn.cursor(aiomysql.DictCursor)
        await cur.execute(sql.replace("?", "%s"), args or ())
        if size:
            rs = await cur.fetchmany(size)
        else:
            rs = await cur.fetchall()
        await cur.close()
        logging.info("rows returned: %s" % len(rs))
        return rs

async def execute(sql, args):
    log_sql(sql, args)
    # 此处是否是必须的？
    global __pool

    with await __pool as conn:
        try:
            cur = await conn.cursor()
            #str_sql = sql.replace("?", "%s")
            #print(str_sql)
            await cur.execute(sql.replace("?", "%s"), args)
            affected = cur.rowcount
            await cur.close()
        except BaseException as e:
            raise
        finally:
            conn.close()
        return affected

class Field(object):

    def __init__(self, name, ddl, pkey, deft):
        self.name = name
        self.ddl = ddl 
        self.pkey = pkey
        self.deft = deft
    
    def __str__(self):
        return "<%s, %s:%s>" % (self.__class__.__name__, self.ddl, self.name)

class StrField(Field):
    def __init__(self, name=None, ddl="varchar(100)", pkey=False, deft=None):
        super(StrField, self).__init__(name, ddl, pkey, deft)

class IntField(Field):
    def __init__(self, name=None, ddl="bigint", pkey=False, deft=None):
        super(IntField, self).__init__(name, ddl, pkey, deft)

class BoolField(Field):
    def __init__(self, name=None, ddl="boolean", pkey=False, deft=False):
        super(BoolField, self).__init__(name, ddl, pkey, deft)

class FltField(Field):
    def __init__(self, name=None, ddl="real", pkey=False, deft=None):
        super(FltField, self).__init__(name, ddl, pkey, deft)

class TextField(Field):
    def __init__(self, name=None, ddl="Text", pkey=False, deft=None):
        super(TextField, self).__init__(name, ddl, pkey, deft)




def create_args_string(num):
    L = []
    for x in range(num):
        L.append("?")
    return ",".join(L)

class ModelMetaClass(type):
    def __new__(cls, name, bases, attrs):
        if name == "Model":
            return super(ModelMetaClass, cls).__new__(cls, name, bases, attrs)

        table_name = attrs.get("__table__", None) or name
        logging.info("found model: %s (table: %s)" %(name, table_name))

        mappings = dict()
        pkey = None
        fields = []

        for k, v in attrs.items():
            if isinstance(v, Field):
                mappings[k] = v
                logging.info("found mapping: %s ==> %s" %(k, v))

                if v.pkey:
                    if pkey:
                        raise RuntimeError("Duplicate primary key for field: %s" % k)
                    pkey = k 
                else:
                    fields.append(k)

        if pkey == None:
            raise RuntimeError("Primary key not found")

        for k in mappings:
            attrs.pop(k)
        escaped_fields = list(map(lambda f: "`%s`" %f, fields))

        attrs["__mappings__"] = mappings
        attrs["__table__"] = table_name
        attrs["__primary_key__"] = pkey
        attrs["__field__"] = fields
        attrs["__select__"] = "select `%s`, %s from `%s`" % (pkey, ",".join(escaped_fields), table_name)
        attrs["__insert__"] = "insert into `%s` (%s, `%s`) values (%s)" % (table_name, ",".join(escaped_fields), pkey, create_args_string(len(escaped_fields) + 1)) 
        attrs["__update__"] = "update `%s` set %s where `%s`=?" % (table_name, ",".join(map(lambda f: "%s=?" %(mappings.get(f).name or f), fields)), pkey)
        attrs["__delete__"] = "delete from `%s` where `%s`=?" % (table_name, pkey)

        return super(ModelMetaClass, cls).__new__(cls, name, bases, attrs)

class Model(dict, metaclass=ModelMetaClass):

    def __init__(self, **kw):
        super(Model, self).__init__(**kw)

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError("Model ojbect has no attribute: %s"%key)

    def __setattr__(self, key, val):
        self[key] = val 

    def get_value(self, key):
        return getattr(self, key, None)

    def get_value_or_deflt(self, key):
        value = getattr(self, key, None)
        if value is None:
            field = self.__mappings__[key]
            if field.deft is not None:
                value = field.deft() if callable(field.deft) else field.deft
                logging.debug("using deft value for %s:%s", key, str(value))
                setattr(self, key, value)
        return value

    @classmethod
    async def find_all(cls, where=None, args=None, **kw):

        sql = [cls.__select__]

        if where:
            sql.append("where")
            sql.append(where)
        
        if args is None:
            args = []
        
        order_by = kw.get("order_by", None)
        if order_by:
            sql.append("order by")
            sql.append(order_by)
        
        limit = kw.get("limit", None)
        if limit:
            sql.append("limit")
            if isinstance(limit, int):
                sql.append("?")
                args.append(limit)
            elif isinstance(limit, tuple) and len(limit) == 2:
                sql.append("?, ?")
                # tuple融入list
                sql.extend(limit)
            else:
                raise ValueError("Invalid limit value:%s" % str(limit))

        logging.info("sql: %s" % sql)            
        logging.info("args: %s" % args)
        rs = await select(" ".join(sql), args)

        #__TODO:此处没搞明白，需要查资料
        return [cls(**r) for r in rs]

    @classmethod
    async def find_number(cls, col, where=None, args=None):

        sql = ["select count(%s) _num_ from `%s`" % (col, cls.__table__)]
        
        if where:
            sql.append("where")
            sql.append(where)

        rs = await select(" ".join(sql), args, 1)
        if len(rs) == 0:
            return None
        return rs[0]["_num_"]

    @classmethod
    async def find(cls, primary_key):
        rs = await select("%s where `%s`=?" % (cls.__select__, cls.__primary_key__), [primary_key], 1)
        if len(rs) == 0:
            return None
        return cls(**rs[0])

    async def save(self):
        args = list(map(self.get_value_or_deflt, self.__field__))
        args.append(self.get_value_or_deflt(self.__primary_key__))
        rows = await execute(self.__insert__, args)

        if rows != 1:
            logging.warn("failed to insert record: affcected rows:%s" % rows)

    async def update(self):
        args = list(map(self.get_value, self.__field__))
        args.append(self.get_value(self.__primary_key__))
        rows = await execute(self.__update__, args)

        if rows != 1:
            logging.warn("failed to update by primary: affcected rows:%s" % rows)

    async def remove(self):
        args = [self.get_value(self.__primary_key__)]
        rows = await execute(self.__delete__, args)

        if rows != 1:
            logging.warn("failed to remove by primary key: affcected rows:%s" % rows)

        

         
        



        
        





        







    








