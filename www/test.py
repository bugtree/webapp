# -*- coding: UTF-8 -*-

import asyncio
import orm
from model import User, Blog, Comment

async def test(loop):
    await orm.create_pool(loop=loop, user="bugtree", password="bugtree", db ="webapp")
    #await orm.create_pool(loop=loop, user="xx", password="xx", db="webapp")

    u = User(name="test", password="123", email="xxx@qqx.com", image="about:blank")

    await u.save()


if __name__ == "__main__":
    print("beging test")

    # 获取EventLoop:
    loop = asyncio.get_event_loop()
    # 执行coroutine
    loop.run_until_complete(test(loop))
    loop.close()



