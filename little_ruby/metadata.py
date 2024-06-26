from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import List
    from dasbus.typing import Structure

from dataclasses import dataclass, field

__all__ = (
    "Metadata", 
)

@dataclass
class Metadata:
    data: Structure = field(repr = False)

    id: str = field(init = False)
    length: int = field(init = False)
    image_url: str = field(init = False)
    album_name: str = field(init = False)
    album_artists: List[str] = field(init = False)
    artists: List[str] = field(init = False)
    rating: float = field(init = False)
    title: str = field(init = False)
    url: str = field(init = False)

    def __post_init__(self):
        self.id = self.data["mpris:trackid"].get_string()
        self.length = self.data["mpris:length"].get_uint64()
        self.image_url = self.data["mpris:artUrl"].get_string()
        self.album_name = self.data["xesam:album"].get_string()
        self.album_artists = self.data["xesam:albumArtist"].get_strv()
        self.artists = self.data["xesam:artist"].get_strv()
        self.rating = self.data["xesam:autoRating"].get_double()
        self.title = self.data["xesam:title"].get_string()
        self.url = self.data["xesam:url"].get_string()