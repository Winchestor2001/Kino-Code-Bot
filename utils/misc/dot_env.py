async def edit_env_file(new_value):
    env_file_path = '.env'

    with open(env_file_path, 'r') as file:
        lines = file.readlines()

    for i in range(len(lines)):
        if lines[i].startswith('MOVIES_CHANNEL_LINK='):
            lines[i] = f'MOVIES_CHANNEL_LINK={new_value}\n'
            break

    with open(env_file_path, 'w') as file:
        file.writelines(lines)
