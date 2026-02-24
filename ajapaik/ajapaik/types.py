from dataclasses import dataclass, field
from typing import List, Union

from django.db.models import QuerySet

from ajapaik.ajapaik.models import Photo, Video, Album


@dataclass
class UserMini:
    id: int
    name: str


@dataclass
class PaginationParameters:
    start: int
    end: int
    page: int
    total: int
    max_page: int


@dataclass
class GalleryResults:
    fb_share_photos: List[Photo]
    my_likes_only: bool
    rephoto_album_author: Union[UserMini, None]

    photo: Union[Photo, None]
    photos: Union[QuerySet[Photo], None]
    photos_with_comments: Union[QuerySet[Photo], None]
    photos_with_rephotos: Union[QuerySet[Photo], None]
    videos: Union[QuerySet[Video], None]

    # Pages and pagination
    start: int
    end: int
    page: int
    total: int
    max_page: int

    # Debugging
    execution_time: str

    album: Union[Album, None]

    # Sort orders
    order1: str = field(default='time')
    order2: str = field(default='added')
    order3: str = field(default='')
