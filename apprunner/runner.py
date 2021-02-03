
import os
import sys
import signal
import asyncio
import inspect
import contextlib
import multiprocessing
from pathlib import Path
from watchgod import awatch
from .factory import get_app_factory
from .exceptions import RunnerException

import logging
logger = logging.getLogger('apprunner')


class Runner:
    __slots__ = (
        "_app_factory",
        "_reload_count",
        "_server_task",
        "_awatch",
        "_awatch_stopped_event",
        "_process")

    def __init__(self, work_dir: dir, factory_loader):
        self._reload_count = 0
        self._server_task = None

        self._app_factory = factory_loader

        self._awatch_stopped_event = asyncio.Event()
        self._awatch = awatch(work_dir, stop_event=self._awatch_stopped_event)

    async def start(self):
        self._server_task = asyncio.get_running_loop().create_task(self._run())

    async def close(self, *args):
        self._awatch_stopped_event.set()
        self._stop_server()

        if self._server_task:
            self._awatch_stopped_event.set()
            async with self._awatch.lock:
                if self._server_task.done():
                    self._server_task.result()
                self._server_task.cancel()

    async def _run(self):
        try:
            self._start_server()

            async for changes in self._awatch:
                self._reload_count += 1
                if any(f.endswith(".py") for _, f in changes):
                    logger.debug('%d changes, restarting server', len(changes))
                    self._stop_server()
                    self._start_server()

        except Exception as exc:
            logger.exception(exc)
            raise RunnerException('error running server')

    def _start_server(self):

        self._process = multiprocessing.Process(
            target=serve_main_app, args=(self._app_factory,))

        self._process.start()

    def _stop_server(self):
        if self._process.is_alive():
            print(f"reload count: {self._reload_count}")
            logger.debug('stopping server process...')
            os.kill(self._process.pid, signal.SIGINT)
            self._process.join(5)
            if self._process.exitcode is None:
                logger.warning('process has not terminated, sending SIGKILL')
                os.kill(self._process.pid, signal.SIGKILL)
                self._process.join(1)
            else:
                logger.debug('process stopped')
        else:
            logger.warning(
                'server process already dead, exit code: %s', self._process.exitcode)


def serve_main_app(app_factory):
    print("serve_main_app")

    app = app_factory()

    loop = asyncio.get_event_loop()
    loop.run_until_complete(app.start())

    try:
        loop.run_forever()
    except KeyboardInterrupt:  # pragma: no cover
        pass
    finally:
        with contextlib.suppress(asyncio.TimeoutError, KeyboardInterrupt):
            loop.run_until_complete(app.stop())


def run(app_or_factory):
    print("run")

    # this must be called only once
    multiprocessing.set_start_method('spawn')

    import sys
    print(sys.path)

    app_factory = get_app_factory(app_or_factory)

    server = Runner(".", app_factory)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(server.start())

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    except RunnerException as e:
        logger.error('Error: %s', e)
        sys.exit(2)
    finally:
        logger.info('shutting down server...')
        start = loop.time()
        with contextlib.suppress(asyncio.TimeoutError, KeyboardInterrupt):
            loop.run_until_complete(server.close())
        logger.info('shutdown took %0.2fs', loop.time() - start)
