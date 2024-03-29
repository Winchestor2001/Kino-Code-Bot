from environs import Env

env = Env()
env.read_env()
BOT_TOKEN = env.str("BOT_TOKEN")
ADMINS = list(map(int, env.list("ADMINS")))
CHANNELS_STATUS = env.list("CHANNELS_STATUS")
DB_NAME = env.str("DB_NAME")
DB_PASSWORD = env.str("DB_PASSWORD")
DB_USER = env.str("DB_USER")
DB_HOST = env.str("DB_HOST")
DB_PORT = env.str("DB_PORT")
POSTER_IMAGE = env.str("POSTER_IMAGE")
SEND_POSTER_IMAGE = env.str("SEND_POSTER_IMAGE")
