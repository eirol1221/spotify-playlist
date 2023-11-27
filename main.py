import os
import requests
from bs4 import BeautifulSoup
import spotipy
from spotipy.oauth2 import SpotifyOAuth

CLIENT_ID = os.environ["CLIENT_ID"]
CLIENT_SECRET = os.environ["CLIENT_SECRET"]
REDIRECT_URI = "http://example.com"
SCOPE = "playlist-modify-private"
USERNAME = os.environ["USERNAME"]

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    scope=SCOPE,
    cache_path="token.txt",
    username=USERNAME,
))

user_id = sp.current_user()["id"]

date_input = input("Which year do you want to travel to? Type the data in the format YYYY-MM-DD:\n")
year = date_input.split("-")[0]

url = f"https://www.billboard.com/charts/hot-100/{date_input}"

response = requests.get(url)
html_data = response.text

soup = BeautifulSoup(html_data, "html.parser")
top_1_list = [item.findNext(name="h3", attrs={"class": "c-title", "id": "title-of-a-story"}) for item in soup.find_all(name="li", attrs={"class": "o-chart-results-list__item // lrv-u-flex-grow-1 lrv-u-flex lrv-u-flex-direction-column lrv-u-justify-content-center lrv-u-border-b-1 u-border-b-0@mobile-max lrv-u-border-color-grey-light lrv-u-padding-l-1@mobile-max"})]
top_99_list = [item.findNext(name="h3", attrs={"class": "c-title", "id": "title-of-a-story"}) for item in soup.find_all(name="li", attrs={"class": "o-chart-results-list__item // lrv-u-flex-grow-1 lrv-u-flex lrv-u-flex-direction-column lrv-u-justify-content-center lrv-u-border-b-1 u-border-b-0@mobile-max lrv-u-border-color-grey-light lrv-u-padding-l-050 lrv-u-padding-l-1@mobile-max"})]
top_100 = top_1_list + top_99_list

song_ids = []
for list in top_100:
    song_title = list.text.strip()
    results = sp.search(q=f"track:{song_title} year:{year}", limit=1, offset=0, type="track")
    try:
        song_uri = results["tracks"]["items"][0]["uri"]
    except IndexError:
        print(f"{song_title} does not exist in Spotify.")
    else:
        song_ids.append(song_uri)

playlist = sp.user_playlist_create(user=user_id, name=f"{date_input} Billboard 100", public=False, description="")
playlist_items = sp.playlist_add_items(playlist_id=playlist["id"], items=song_ids)