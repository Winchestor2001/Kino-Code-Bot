from database.models import *
from playhouse.shortcuts import model_to_dict
from data.config import ADMINS


async def add_user(user_id: int):
    with db:
        if not Users.select().where(Users.user_id == user_id).exists():
            Users.create(user_id=user_id)


async def get_all_users():
    with db:
        users = [model_to_dict(item).get('user_id') for item in Users.select()]
        return users


async def get_channels():
    with db:
        data = Channels.select()
        channels = [model_to_dict(item) for item in data]
        count_channels = data.count()
        return channels, count_channels


async def get_admins(all_admins=True):
    with db:
        if all_admins:
            admins = [model_to_dict(item).get('admin_id') for item in Admins.select()]
            users = Users.select().count()
            admins.extend(ADMINS)
            return admins, users
        else:
            admins = [model_to_dict(item) for item in Admins.select()]
            return admins


async def delete_movie_code(code):
    with db:
        if Movies.select().where(Movies.movie_code == code).exists():
            Movies.delete().where(Movies.movie_code == code).execute()
            return True
        else:
            return False


async def get_movies_list():
    with db:
        movies = [model_to_dict(item) for item in Movies.select().order_by(Movies.movie_code.asc())]
        movies_count = Movies.select().count()

        return movies, movies_count


async def delete_all_movies():
    with db:
        Movies.delete().execute()


async def get_movie(code):
    with db:
        movie_info = [model_to_dict(item) for item in Movies.select().where(Movies.movie_code == code)]

        return movie_info


async def add_new_channel(channel_name, channel_id, channel_link):

    with db:
        Channels.get_or_create(
            channel_name=channel_name,
            channel_id=channel_id,
            channel_link=channel_link
        )


async def get_channel_by_id(channel_id):
    with db:
        channel = [model_to_dict(item) for item in Channels.select().where(Channels.channel_id == channel_id)]
        return channel[0]


async def delete_channel(channel_id):
    with db:
        Channels.delete().where(Channels.channel_id == channel_id).execute()


async def add_new_admin(admin_name, admin_id):
    with db:
        Admins.get_or_create(admin_id=admin_id, admin_name=admin_name)


async def delete_admin(admin_id):
    with db:
        Admins.delete().where(Admins.admin_id == admin_id).execute()


async def add_new_movie(movie_code, movie_title, movie_id):
    with db:
        Movies.get_or_create(movie_code=movie_code, movie_title=movie_title, movie_id=movie_id)


async def update_movie_views(movie_code):
    with db:
        Movies.update(views=Movies.views + 1).where(Movies.movie_code == movie_code).execute()
        views = [model_to_dict(item) for item in Movies.select().where(Movies.movie_code == movie_code)]
        return views[0]['views']


async def get_default_channel_link():
    with db:
        link = UtilsModel.select()
        return [model_to_dict(item) for item in link][0]['default_channel_link']


async def update_default_channel_link(link):
    with db:
        check_item = UtilsModel.select(UtilsModel.default_channel_link).exists()
        if check_item:
            UtilsModel.update(default_channel_link=link).execute()
        else:
            UtilsModel.insert(default_channel_link=link).execute()

