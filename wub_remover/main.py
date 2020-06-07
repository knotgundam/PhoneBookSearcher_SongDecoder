import re


def song_decoder(song: str):
    return re.sub(r'(WUB)+', ' ', song).strip()
