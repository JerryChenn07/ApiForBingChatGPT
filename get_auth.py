"""
-------------------------------------------------
    FileName  : get_auth.py
    Time      : 2023-03-14 17:35
    Author    : cjr
-------------------------------------------------
"""
import aiohttp
import asyncio


async def get_auth(cookies):
    kwargs = {}
    kwargs['url'] = f'https://www.bing.com/turing/conversation/create'
    # kwargs['url'] = f'https://www.baidu.com'
    kwargs['timeout'] = 30
    kwargs['cookies'] = cookies
    async with aiohttp.ClientSession() as client:
        try:
            response = await client.get(**kwargs)
            if response.status == 200:
                text = await response.text()
                return 200, text
            else:
                return 404, ''

        except Exception as ex:
            return 500, ex


if __name__ == '__main__':
    ret = asyncio.run(get_auth())
    print(ret)
