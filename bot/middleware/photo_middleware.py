import asyncio

from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.middlewares import BaseMiddleware

from asyncio import sleep
from typing import Any, Callable, Awaitable

# from aiogram import BaseMiddleware
from aiogram.types import Message
from cachetools import TTLCache


# class AlbumMiddleware(BaseMiddleware):
#     """This middleware is for capturing media groups."""

#     album_data: dict = {}

#     def __init__(self, latency: Union[int, float] = 0.01):
#         """
#         You can provide custom latency to make sure
#         albums are handled properly in highload.
#         """
#         self.latency = latency
#         super().__init__()

#     async def on_process_message(self, message: types.Message, data: dict):
#         if not message.media_group_id or not message.photo:
#             return
#         print(message)
#         try:
#             # print(message)
#             self.album_data[message.media_group_id].append(message)
#             raise CancelHandler()  # Tell aiogram to cancel handler for this group element
#         except KeyError:
#             self.album_data[message.media_group_id] = [message]
#             await asyncio.sleep(self.latency)

#             message.conf["is_last"] = True
#             data["album"] = self.album_data[message.media_group_id]

#     async def on_post_process_message(self, message: types.Message, result: dict, data: dict):
#         """Clean up after handling our album."""
#         if message.media_group_id and message.conf.get("is_last"):
#             del self.album_data[message.media_group_id]

class AlbumMiddleware(BaseMiddleware):
    def __init__(self, latency: float = 0.1):
        self.latency = latency

    cache = TTLCache(maxsize=10_000, ttl=0.1)

    async def __call__(
        self,
        handler: Callable[[Message, dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: dict[str, Any]
    ) -> Any:
        if event.photo:
            if event.media_group_id in self.cache:
                self.cache[event.media_group_id].append(event.photo)

            else:
                self.cache[event.media_group_id] = [event.photo]
                await sleep(self.latency)
                data["album"] = self.cache[event.media_group_id]

                return await handler(event, data)
    # print('Photo middleware set up')


# @dp.message_handler(is_media_group=True, content_types=types.ContentType.ANY)
# async def handle_albums(message: types.Message, album: List[types.Message]):
#     """This handler will receive a complete album of any type."""
#     media_group = types.MediaGroup()
#     for obj in album:
#         if obj.photo:
#             file_id = obj.photo[-1].file_id
#         else:
#             file_id = obj[obj.content_type].file_id

#         try:
#             # We can also add a caption to each file by specifying `"caption": "text"`
#             media_group.attach({"media": file_id, "type": obj.content_type})
#         except ValueError:
#             return await message.answer("This type of album is not supported by aiogram.")

#     await message.answer_media_group(media_group)