import sys
import json
import logging
import asyncio
import requests
import functools
from bs4 import BeautifulSoup

BASE_URL = "http://172.27.102.252"

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
    stream=sys.stdout)


def get_file_folder(url):
    logging.info("Getting url: %s", url)
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    items = []
    try:
        list_items = [(item.text, item.attrs['href']) for item in soup.table.findAll('a')]

        for name, link in list_items:
            if name not in ["Name", "Last modified", "Size", "Description", "Parent Directory", 'hls/', 'webbackup/']:
                items.append((name, link))

    except AttributeError:
        items = [soup.title.text]

    return items


def add_to_tree(base_object, key, future):
    result = future.result()
    logging.debug("Result received: key: %s value: %s", key, result)
    base_object[key] = result


async def generate_tree(base_path, folder_path, previous_future):
    logging.debug("New Task: Path: %s", base_path + folder_path)

    file_folders = get_file_folder(base_path + folder_path)

    futures = []
    current_folder = {}
    current_path = base_path + folder_path

    for file_folder in file_folders:

        if file_folder[0][-1] is '/':
            future = asyncio.Future()
            future.add_done_callback(functools.partial(add_to_tree, current_folder, file_folder[0]))

            futures.append(generate_tree(current_path, file_folder[1], future))

        else:
            current_folder[file_folder[0]] = "%s%s/%s" % (base_path, folder_path, file_folder[1])

    await asyncio.gather(*futures)

    previous_future.set_result(current_folder)
    logging.debug("Task Finished: Path: %s", base_path + folder_path)


async def main():
    future = asyncio.Future()
    await generate_tree(BASE_URL, '/', future)

    data = future.result()
    with open('data.json', 'w') as target:
        json.dump(data, target, indent=4)

    print("Finished")
    # await get_file_folder(BASE_URL)


if __name__ == '__main__':
    asyncio.run(main())
