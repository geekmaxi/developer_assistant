# -- coding: utf-8 --**


import datetime
import os
import simplejson
import dotenv
dotenv.load_dotenv(os.path.join(os.environ.get("PYTHONPATH"), ".env"))

from da.ingest.config import load_config, Config
from da.ingest.python import PythonIngester
from da.ingest.fastapi import FastapiIngester
from da.ingest.w3school import W3schoolIngester
from da.ingest.langchain_ingester import LangchainIngester


def do_ingest(config: Config):
    class_name = config.ingester.capitalize() + "Ingester"

    ingester = eval(class_name)(config)
    ingester.invoke()

def lock_file():
    import os
    import fcntl

    filepath = os.path.join(os.getenv("PYTHONPATH"), "ingest.lock")


    try:
        # fcntl.lockf(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
        f = open(filepath, 'rw')

        return f
    except IOError:
        return None

def parser_lock_file(f):
    lock_info = simplejson.load(f)
    return lock_info

def unlock(f, lock_info):
    # import fcntl
    # fcntl.lockf(f, fcntl.LOCK_UN)
    # f.seek(0)
    # f.truncate()
    simplejson.dump(lock_info, f)
    f.close()

if __name__ == "__main__":


    configs = load_config()


    # print(configs.pop())
    # ingest = PythonIngester()
    # ingest.invoke()

    # do_ingest(configs.pop())
    # for config in configs:
    #     do_ingest(config)
    # do_ingest(configs[5])

    # exit()

    def keyname(config: Config):
        return f"{config.ingester}-{config.framework}({config.version})"
    
    lock_file_path = os.path.join(os.getenv("PYTHONPATH"), "ingest.lock")
    with open(lock_file_path, "r") as f:
        lock_file_info = simplejson.load(f)



    for config in configs:
        _keyname = keyname(config)

        if lock_file_info.get(_keyname, ""):
            continue
        do_ingest(config)

        lock_file_info[_keyname] = str(datetime.datetime.now())

        with open(lock_file_path, "w") as f:
            simplejson.dump(lock_file_info, f, indent=4 * ' ')



