import os
import asyncio
import random

import discord
from dotenv import load_dotenv

import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotipy.oauth2 import SpotifyClientCredentials

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
# CHANNELFOLLOW = os.getenv('DISCORD_CHANNEL_ID')
SPOTIFYID = os.getenv('SPOTIFY_CLIENT_ID')
SPOTIFYSECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
PLAYLISTID = os.getenv('SPOTIFY_PLAYLIST_ID')

# Default intents are now required to pass to Client
intents = discord.Intents.all()
client = discord.Client(intents=intents)

# CONSTANTS
SPOTIFY_TRACK_URL_HEADER = 'https://open.spotify.com/track/'

async def getHipsterScore(trackPopularity):
    return 100 - trackPopularity

async def getHipsterRatingText(popularity):
    hipsterScore = await getHipsterScore(popularity)
    hipsterRatingText = "This Track has a hipster score of " + str(hipsterScore) + " out of 100."
    return hipsterRatingText

async def getTrackTitleAndArtist(track):
    trackTitle = await getAttributeFromTrack(track, 'name')
    trackArtist = await getAttributeFromTrack(track, "artists")
    trackTitleAndArtist = trackTitle + " by " + trackArtist
    return trackTitleAndArtist

async def getTrackDetails(trackId):
    track_detail_string = "Track: "
    return track_detail_string

async def getAttributeFromTrack(track, attribute):
    if attribute == 'artists':
        return track['artists'][0]["name"]
    else:
        return track[attribute]

async def getSpotifyInstance():
    # Replace <client_id> and <client_secret> with your own Spotify API credentials
    auth = SpotifyOAuth(client_id=SPOTIFYID,
                         client_secret=SPOTIFYSECRET,
                         redirect_uri='http://localhost:8888/callback',
                         open_browser=True,
                         scope=['playlist-modify-public'])
    sp = spotipy.Spotify(auth_manager=auth)
    return sp

async def getTrackFromId(trackId):
    sp = await getSpotifyInstance()
    track = sp.track(trackId)
    return track

async def getTrackIdFromUrl(songUrl):

    # Extract the song id from the song url
    songId = songUrl.split('track/')[1]
    trackId = songId.split('?')[0]
    # song_id = ("spotify:track:" + track_id)
    return trackId

async def add_song_to_playlist(songUrl, playlistId):
    sp = await getSpotifyInstance()

    # print(song_id)

    # Getting the song name for message formatting
    trackId = await getTrackIdFromUrl(songUrl)
    track = sp.track(trackId)
    track_name = track['name']
    track_artist = track['artists'][0]["name"]
    track_hipster_rating = await getHipsterScore(track['popularity'])
    tmp_message_text_line_one = track_name + " by " + track_artist + " has been added to the Discord Playlist."
    tmp_message_text_line_two = await getHipsterRatingText(track_hipster_rating)
    tmp_message_text = tmp_message_text_line_one + "\n" + tmp_message_text_line_two
    # print(track_name)
    # print(track_artist)
    # print(tmp_message_text)


    return tmp_message_text




@client.event
async def on_ready():
    print(f'{client.user.name} has connected to Discord!')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith(SPOTIFY_TRACK_URL_HEADER):
        message_text = await add_song_to_playlist(message.content, PLAYLISTID)
        embed = discord.Embed(title=message_text, color=0x00ff00)
        await message.channel.send(embed=embed)
    else:
        if client.user in message.mentions:
            if "!hipster" in message.content.lower():
                cleanedMessage = message.content.split("!hipster ")
                if len(cleanedMessage) < 2:
                    # print(cleanedMessage)
                    return
                if cleanedMessage[1].startswith(SPOTIFY_TRACK_URL_HEADER):
                    trackUrl = cleanedMessage[1]
                    trackId = await getTrackIdFromUrl(trackUrl)
                    track = await getTrackFromId(trackId)
                    trackTitleAndArtist = await getTrackTitleAndArtist(track)
                    popularityRating = await getAttributeFromTrack(track, 'popularity')
                    hipsterText = await getHipsterRatingText(popularityRating)
                    responseText = trackTitleAndArtist + ": " + hipsterText
                    embed = discord.Embed(title=responseText, color=0x00ff00)
                    await message.channel.send(embed=embed)
                    # print(message.content)
                else:
                    responseText = "Looks like a misformatted request, please make sure to use '!hipster' followed by a space, then the Spotify URL."
                    embed = discord.Embed(title=responseText, color=0xff0000)
                    await message.channel.send(embed=embed)
                    print(message.content)
            elif "!command" in message.content.lower():
                embed = discord.Embed(title="!hipster: Find hipster rating of Song based on Spotify URL\n!command: Show list of commands", color=0x0000ff)
                await message.channel.send(embed=embed)
                # print("!command fired")
            else:
                embed = discord.Embed(title="Hello, still working out some kinks (no shame)", color=0xffff00)
                await message.channel.send(embed=embed)
                # print("Failure fired")



client.run(TOKEN)
