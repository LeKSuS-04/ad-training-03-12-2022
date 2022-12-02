#!/usr/bin/env python3
import asyncio
import logging

from asyncio import StreamReader, StreamWriter
from socket_utils import send_message
from actions import prompt_for_action, create_secret, read_secret, feedback


log = logging.getLogger(__name__)


async def handle_client(reader: StreamReader, writer: StreamWriter):
    await send_message(writer,
        "Welcome to Shizika, the most secure secrets vault! "
        "We store all kinds of things, ranging from your "
        "passwords to the darkest secrets of the universe!\n\n"
    )

    while True:
        action = await prompt_for_action(reader, writer, 1, 3)
        if action == 1:
            await create_secret(reader, writer)
        elif action == 2:
            await read_secret(reader, writer)
        elif action == 3:
            await feedback(reader, writer)
            break

    await send_message(writer, 'Bye!\n')
    writer.close()
    await writer.wait_closed()


def handle_exception(loop, context):
    msg = context.get("exception", context["message"])
    log.error(msg)
    return


async def init():
    loop = asyncio.get_running_loop()
    loop.set_exception_handler(handle_exception)
    server = await asyncio.start_server(handle_client, '0.0.0.0', 1337)
    async with server:
        await server.serve_forever()


if __name__ == '__main__':
    asyncio.run(init())
