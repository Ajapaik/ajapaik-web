from dataclasses import dataclass, field

from django.db.models import QuerySet

from ajapaik.ajapaik.models import Album, Photo, Video


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
    my_likes_only: bool
    rephoto_album_author: UserMini | None

    photo: Photo | None
    photos: QuerySet[Photo] | None
    photos_with_comments: QuerySet[Photo] | None
    photos_with_rephotos: QuerySet[Photo] | None
    videos: QuerySet[Video] | None

    # Pages and pagination
    start: int
    end: int
    page: int
    total: int
    max_page: int

    # Debugging
    execution_time: str

    album: Album | None

    # Sort orders
    order1: str = field(default="time")
    order2: str = field(default="added")
    order3: str = field(default="")
