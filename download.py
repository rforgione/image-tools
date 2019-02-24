import cv2
import requests
import os
import argparse
from typing import Union
from pathlib import Path
from multiprocessing.dummy import Pool as ThreadPool
import multiprocessing
from timeit import default_timer as timer
import re


class ImageDownloader(object):

    @staticmethod
    def _valid_image(path: Union[Path, str]) -> bool:
        try:
            img = cv2.imread(path)
            if img is None:
                return False
            return True
        except Exception:
            return False

    @staticmethod
    def download_image(url, output, idx):
        pat = re.compile(r"(\.(jpeg|png|jpg|JPEG|PNG|JPG))")
        pre_args = url.split("?")[0]
        m = pat.match(pre_args[pre_args.rfind("."):])
        if not m:
            print("[INFO] Image is not a valid filetype, skipping")
            return
        path = os.path.sep.join([output, "{}{}".format(str(idx).zfill(8), m[1])])
        try:
            with open(path, 'wb') as f:
                f.write(requests.get(url).content)

            if not ImageDownloader._valid_image(path):
                print("[INFO] Image is not valid, removing.")
                os.remove(path)
            else:
                print("[INFO] Wrote image {}".format(path))
        except Exception:
            print("[INFO] Unable to download image")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("-u", "--urls", required=True, help="Path to file containing URLs to download.")
    ap.add_argument("-o", "--output", required=True, help="Directory to download images to.")
    ap.add_argument("-s", "--single", action='store_true', help="Run single-threaded.")
    args = ap.parse_args()

    with open(args.urls) as f:
        rows = [i.strip() for i in f.readlines()]

    start = timer()
    if args.single:
        print("[INFO] Running single-threaded...")
        for idx, img_url in enumerate(rows):
            ImageDownloader.download_image(img_url, args.output, idx)
    else:
        cpus = multiprocessing.cpu_count()
        print("[INFO] Running multithreaded across {} threads...".format(cpus))
        pool = ThreadPool(cpus)
        arr = [(url, args.output, idx) for (idx, url) in list(enumerate(rows))]
        print(arr)
        pool.map(lambda tup: ImageDownloader.download_image(*tup), arr)
    end = timer()
    print(end - start)

