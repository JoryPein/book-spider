from aiohttp import ClientSession, ClientTimeout
import utils.aio_cache as aio_cache
import utils.aio_retry as aio_retry
from parsel import Selector
import asyncio
import os
import aiofiles
import traceback
import re

@aio_cache.cache()
@aio_retry.retry_timeout()
async def fetch(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.55 Safari/537.36 Edg/96.0.1054.43",
    }
    async with ClientSession(headers=headers, timeout=ClientTimeout(10)) as session:
        async with session.get(url) as response:
            return await response.read()


def parse_contents(html_content):
    selector = Selector(text=html_content.decode())
    for div in selector.xpath('//*[@id="main"]/div[1]/div'):
        a = div.xpath('h1/a')
        if a:
            yield dict(
                src=a.attrib['href'],
                title=a.xpath('text()').get()
            )

@aio_cache.cache()
async def traversal_contents():
    results = []
    index = 1
    for page in range(1, 4+1):
        url = f'https://www.williamlong.info/xiaoshuo/tag/baijing_{page}.html'
        html_content = await fetch(url)

        for item in parse_contents(html_content):
            item.update(dict(index=index))
            results.append(item)
            index += 1
    return results


def parse_text(html_content):
    selector = Selector(text=html_content.decode())
    return "".join(
        list(
            map(lambda p: p.get()+"\n", selector.xpath('//div[@class="entry-content"]/p/text()'))
        )
    )

async def save_content(title, text):
    path_book_root = "res/moby_dick/text"
    if not os.path.exists(path_book_root):
        os.makedirs(path_book_root)
    path_new = os.path.join(path_book_root, f"{title}.txt")
    if os.path.exists(path_new):
        return
    async with aiofiles.open(path_new, mode='w', encoding="utf-8") as fp:
        await fp.write(text)

class AsyncExecutor:

    def __init__(self, loop, max_workers=300):
        self.loop = loop
        self.sema = asyncio.Semaphore(max_workers)

    @staticmethod
    async def producer():
        pass

    @staticmethod
    async def worker(task, sema):
        pass

    async def run(self):
        tasks = [self.loop.create_task(self.worker(task, self.sema)) for task in await self.producer()]
        asyncio.gather(*tasks)
        print("[Running]")
        while not all([t.done() for t in tasks]):
            await asyncio.sleep(3)
        print("[All tasks finished]")

async def producer():
    return await traversal_contents()

async def worker(task, sema):
    async with sema:
        try:
            html_content = await fetch(task["src"])
            text = parse_text(html_content)
            path_title = re.sub("\[\d+\]", "", task["title"])
            name = f'{task["index"]}.{path_title}'
            print("[+] Parsing", path_title)
            await save_content(name, task["title"]+"\n\n"+text)
        except:
            traceback.print_exc()

async def main(loop):
    ae = AsyncExecutor(loop)
    ae.producer = producer
    ae.worker = worker
    await ae.run()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))
