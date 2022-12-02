import os
import random
from string import ascii_letters, digits
from asyncio import StreamReader, StreamWriter
from socket_utils import send_message, read_with_message


ACTIONS_PROMPT = '''What do you want to do?
1. Create new secret
2. View existing secret
3. Exit
> '''


def random_string(length: int) -> str:
    return ''.join(random.choice(ascii_letters + digits) for _ in range(length))


async def prompt_for_action(reader: StreamReader, writer: StreamWriter, min_option: int, max_option: int) -> int:
    available_options = [str(i) for i in range(min_option, max_option + 1)]
    while True:
        client_choice = await read_with_message(reader, writer, ACTIONS_PROMPT)
        if client_choice in available_options:
            return int(client_choice)
        else:
            await send_message(writer, 'Oh-oh, bad option! Number expected, try again:\n')


async def create_secret(reader: StreamReader, writer: StreamWriter):
    secret = await read_with_message(reader, writer, 'Enter your secret: ')
    password = await read_with_message(reader, writer, 'Enter password for your secret: ')

    secret_id = random_string(20)

    with open(f'secrets/{secret_id}:{password}', 'w') as f:
        f.write(secret)

    await send_message(writer, 
        f'Done! ID of your secret is {secret_id}\n'
        f'You can access your secret at any time using this ID and your password\n\n'
    )


async def read_secret(reader: StreamReader, writer: StreamWriter):
    secret_id = await read_with_message(reader, writer, 'Enter id of your secret: ')
    password = await read_with_message(reader, writer, 'Enter password for your secret: ')

    if not secret_id or not password:
        await send_message(writer, f"Secret id and password can't be empty\n\n")
        return

    for secret in os.listdir('secrets'):
        if secret.startswith(secret_id) and secret.endswith(password):
            with open(f'secrets/{secret}', 'r') as f:
                secret_data = f.read()
            await send_message(writer, f"Here's your secret: {secret_data}\n\n")
            return
    
    await send_message(writer, 'Unable to find secret with provided id/password :(\n\n')


async def feedback(reader: StreamReader, writer: StreamWriter):
    leave_feedback = await read_with_message(reader, writer, 'Would you like to leave feedback (yes/no)?: ')
    if leave_feedback.lower() not in ['y', 'yes']:
        return

    feedback = await read_with_message(reader, writer, 'Enter your feedback in one line: ')
    if '\n' in feedback:
        await send_message(writer, 'Invalid feedback, but thank you anyways!\n')
        return

    os.system(f'echo "{feedback}" >> feedback/feedback-db.txt')
    await send_message(writer, 'Thank you for your feedback!\n')
