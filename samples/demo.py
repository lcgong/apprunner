import asyncio
import apprunner
import logging

import sys
import os

sys.path.append(os.getcwd())

class Application:

    async def start(self):
        print("started")
        pass

    async def stop(self):
        print("stopped")

def create_app():
    app = Application()
    return app

import sys
print(sys.path)

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    apprunner.run(Application())
