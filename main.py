import os
import asyncio
import random

import discord
from dotenv import load_dotenv
import applemusicpy

import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotipy.oauth2 import SpotifyClientCredentials

# TODO: Add ENV items for Apple Music
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
# CHANNELFOLLOW = os.getenv('DISCORD_CHANNEL_ID')
APPLE_KEY = os.getenv('APPLE_MUSIC_KEY')
APPLE_TEAM = os.getenv('APPLE_MUSIC_TEAM')
APPLE_SECRET = os.getenv('APPLE_MUSIC_SECRET')
SPOTIFYID = os.getenv('SPOTIFY_CLIENT_ID')
SPOTIFYSECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
SPOTIFY_PLAYLIST_ID = os.getenv('SPOTIFY_PLAYLIST_ID')

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

async def getMusicInstance():
    am = applemusicpy.AppleMusic(APPLE_SECRET, APPLE_KEY, APPLE_TEAM)
    return am

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

async def getMusicUrlFromTitleAndArtist(title, artist):
    am = await getMusicInstance()
    searchTerm = title + " " + artist
    returnString = ""
    backupString = ""
    # print(searchTerm)
    results = am.search(searchTerm, types=['songs'], limit=5)
    if len(results) < 1:
        return False
    for item in results['results']['songs']['data']:
        if title.lower() in item['attributes']['name'].lower():
            if artist.lower() in item['attributes']['artistName'].lower():
                returnString = "[BETA] Apple Music: " + item['attributes']['url']
                return returnString
            else:
                backupString = backupString + item['attributes']['name'] + "\n"
    if backupString != "":
        return backupString
    else:
        return False

async def searchMusicFromTerms(terms, types = None):
    am = await getMusicInstance()
    types = "songs" if types is None else types
    returnString = ""
    backupString = ""
    results = am.search(terms, types=[types], limit=5)
    if len(results) < 1:
        return false
    for item in results['results'][types]['data']:
        if terms.lower() in item['attributes']['name'].lower():
            returnString = item['attributes']['name'] + " by " + item['attributes']['artistName'] + ": " + item['attributes']['url']
            return returnString
        else:
            backupString = backupString + "\n" + item['attributes']['name'] + " by " + item['attributes']['artistName']
    return backupString

async def getTrackIdFromUrl(songUrl):
    # Extract the song id from the song url
    songId = songUrl.split('track/')[1]
    trackId = songId.split('?')[0]
    # song_id = ("spotify:track:" + track_id)
    return trackId

async def handleSpotifyLink(songUrl, shouldAddToPlaylist = None):
    # Get Spotify Auth
    sp = await getSpotifyInstance()

    # Get track details
    trackId = await getTrackIdFromUrl(songUrl)
    track = sp.track(trackId)
    trackName = track['name']
    trackArtist = track['artists'][0]["name"]
    trackHipsterRating = await getHipsterScore(track['popularity'])
    tempMessageText = ""
    if shouldAddToPlaylist:
        await add_song_to_playlist(trackId, sp)
        # build the message to return
        tempMessageTextLine1 = trackName + " by " + trackArtist + " has been added to the Discord Playlist."
        tempMessageTextLine2 = await getHipsterRatingText(trackHipsterRating)
        tempMessageText = tempMessageTextLine1 + "\n" + tempMessageTextLine2 + "\n"

    # Attempt to find Apple Music link and append to message
    appleMusicMessage = await getMusicUrlFromTitleAndArtist(trackName,trackArtist)
    if appleMusicMessage:
        tempMessageText = tempMessageText + appleMusicMessage
    else:
        tempMessageText = tempMessageText + "Couldn't find Apple Music track"
    return tempMessageText

async def add_song_to_playlist(trackId, spInstance):
    # add song to playlist
    spInstance.playlist_add_items(playlist_id=SPOTIFY_PLAYLIST_ID, items=[trackId], position=None)




@client.event
async def on_ready():
    print(f'{client.user.name} has connected to Discord!')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith(SPOTIFY_TRACK_URL_HEADER):
        message_text = await handleSpotifyLink(message.content, True)
        embed = discord.Embed(title=message_text, color=0x00ff00)
        await message.channel.send(embed=embed)
    else:
        if client.user in message.mentions:
            # Handle !hipster command request
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
                    print(responseText)
                else:
                    responseText = "Looks like a misformatted request, please make sure to use '!hipster' followed by a space, then the Spotify URL."
                    embed = discord.Embed(title=responseText, color=0xff0000)
                    await message.channel.send(embed=embed)
                    # print(responseText)

            # Handle !command request
            elif "!command" in message.content.lower():
                embed = discord.Embed(title="!hipster: Find hipster rating of Song based on Spotify URL\n\n!applesearch looks for songs in Apple Music\n\n!applify searches the Spotify URL for Apple version; does not add link to the Playlist\n\n!command: Show list of commands", color=0x0000ff)
                await message.channel.send(embed=embed)
                # print("!command fired")
            elif "!applify" in message.content.lower():
                cleanedMessage = message.content.split("!applify ")
                if len(cleanedMessage) < 2:
                    print(cleanedMessage)
                    return
                if cleanedMessage[1].lower().startswith(SPOTIFY_TRACK_URL_HEADER):
                    spotifyUrl = cleanedMessage[1]
                    searchResult = await handleSpotifyLink(spotifyUrl, False)
                    if searchResult:
                        responseText = searchResult
                        responseColor = 0x00ff00
                    else:
                        responseText = "No match detected"
                        responseColor = 0xffff00
                    embed = discord.Embed(title=responseText, color=responseColor)
                    await message.channel.send(embed=embed)
                    # print(responseText)
                else:
                    responseText = "Looks like this is not a properly formatted Spotify URL."
            # Handle !applesearch function
            elif "!applesearch" in message.content.lower():
                cleanedMessage = message.content.split("!applesearch ")
                if len(cleanedMessage) < 2:
                    print(cleanedMessage)
                    return
                if not cleanedMessage[1].lower().startswith("https"):
                    searchQuery = cleanedMessage[1]
                    searchResult = await searchMusicFromTerms(searchQuery, 'songs')
                    if searchResult:
                        responseText = searchResult
                    else:
                        responseText = "No match detected"
                    embed = discord.Embed(title=responseText, color=0x00ff00)
                    await message.channel.send(embed=embed)
                    # print(responseText)
                else:
                    responseText = "Looks like you're trying to send a link instead of a search. I'm still working on that."
                    # print(responseText)
                    embed = discord.Embed(title=responseText, color=0xff0000)
            else:
                embed = discord.Embed(title="Hello, still working on myself; try checking out !command for available functions!", color=0xffff00)
                await message.channel.send(embed=embed)
                print("Failure fired")



client.run(TOKEN)
