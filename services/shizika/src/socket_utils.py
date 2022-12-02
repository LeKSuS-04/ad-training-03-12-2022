from asyncio import StreamReader, StreamWriter


async def send_message(writer: StreamWriter, message: str):
    writer.write(message.encode())
    await writer.drain()


async def read_message(reader: StreamReader) -> str:
    return (await reader.read(4096)).strip().decode()


async def read_with_message(reader: StreamReader, writer: StreamWriter, message: str) -> str:
    await send_message(writer, message)
    return await read_message(reader)
