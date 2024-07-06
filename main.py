import os
import asyncio
import random
import sys

import discord
from dotenv import load_dotenv
import applemusicpy

import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotipy.oauth2 import SpotifyClientCredentials

# Set Environment Variables based on path
envPathProd = os.path.join(os.path.dirname(__file__), '.env')
envPathStage = os.path.join(os.path.dirname(__file__), '.env.stage')
# Default Environment is Prod
isProd = True
envPath = envPathProd

# Check if launched with staging argument
if len(sys.argv) > 0:
    print("Arguments fed.")
    if "--staging" in sys.argv:
        isProd = False
        envPath = envPathStage


load_dotenv(envPath)
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
CHANNEL_ID = int(os.getenv('DISCORD_CHANNEL_ID'))
APPLE_KEY = os.getenv('APPLE_MUSIC_KEY')
APPLE_TEAM = os.getenv('APPLE_MUSIC_TEAM')
APPLE_SECRET = os.getenv('APPLE_MUSIC_SECRET')
SPOTIFYID = os.getenv('SPOTIFY_CLIENT_ID')
SPOTIFYSECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
SPOTIFY_PLAYLIST_ID = os.getenv('SPOTIFY_PLAYLIST_ID')

# CONSTANTS
SPOTIFY_TRACK_URL_HEADER = 'https://open.spotify.com/track/'
APPLE_TRACK_URL_HEADER = 'https://music.apple.com/'

# Default intents are now required to pass to Client
intents = discord.Intents.all()
client = discord.Client(intents=intents)

# Default Colors
HEX_RED = 0xff0000
HEX_GREEN = 0x00ff00
HEX_BLUE = 0x0000ff
HEX_YELLOW = 0xffff00

# TODO: Move Command Handles to this function
async def handleCommand(command, message):
    # print("handleCommand fired")
    matchSplit = command + " "
    cleanedMessage = message.content.split(matchSplit)
    match command:
        case "!command":
            print(command)
        case "!applesearch":
            print(command)
        case "!applify":
            print(command)
        case "!hipster":
            print(command)
        case "!playlist":
            if len(cleanedMessage) < 2:
                print(cleanedMessage)
                return
            if cleanedMessage[1].lower().startswith(SPOTIFY_TRACK_URL_HEADER):
                spotifyUrl = cleanedMessage[1]
                duplicate = await playlistCommand(spotifyUrl)
                if duplicate:
                    responseText = duplicate
                    responseColor = HEX_YELLOW
                else:
                    responseText = "Track is not in playlist"
                    responseColor = HEX_GREEN
                embed = discord.Embed(title=responseText, color=responseColor)
                await message.channel.send(embed=embed)
                # print(responseText)
        case "!spotlify":
            if len(cleanedMessage) < 2:
                print(cleanedMessage)
                return
            if cleanedMessage[1].lower().startswith(APPLE_TRACK_URL_HEADER):
                appleUrl = cleanedMessage[1]
                # TODO: Create and add function to get Track ID from URL (similar to Spotify)
                # Format is i=<TrackID> - possibly pull that via split
        case _:
            print("Whoops!")

async def playlistCommand(spotifyUrl):
    trackId = await getTrackIdFromUrl(spotifyUrl)
    sp = await getSpotifyInstance()
    isDuplicate = await checkTrackInSpotifyPlaylist(trackId, sp)
    print("Playlist Command")
    if isDuplicate:
        return "Track is already in the Playlist"
    else:
        return False


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
    results = am.search(searchTerm, types=['songs'], limit=20)
    # Check if any results
    if results['results']:
        print("True")
        for item in results['results']['songs']['data']:
            if title.lower() in item['attributes']['name'].lower():
                if artist.lower() in item['attributes']['artistName'].lower():
                    returnString = "[BETA] Apple Music: " + item['attributes']['url']
                    return returnString
                else:
                    backupString = backupString + item['attributes']['name'] + "\n"
    else:
        return False
    if backupString != "":
        return backupString
    else:
        return False

async def searchMusicFromTerms(terms, types = None):
    am = await getMusicInstance()
    types = "songs" if types is None else types
    returnString = ""
    backupString = ""
    results = am.search(terms, types=[types], limit=10)
    if results['']:
        for item in results['results'][types]['data']:
            if terms.lower() in item['attributes']['name'].lower():
                returnString = item['attributes']['name'] + " by " + item['attributes']['artistName'] + ": " + item['attributes']['url']
                return returnString
            else:
                backupString = backupString + "\n" + item['attributes']['name'] + " by " + item['attributes']['artistName']
        return backupString
    else:
        return False

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
    isDupe = await checkTrackInSpotifyPlaylist(trackId, sp)
    if shouldAddToPlaylist:
        if isDupe:
            tempMessageText = trackName + " is already in the playlist." + "\n"
        else:
            await addSongToPlaylist(trackId, sp)
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

async def checkTrackInSpotifyPlaylist(trackId, spInstance):
    playlistTracks = spInstance.playlist_tracks(SPOTIFY_PLAYLIST_ID, fields="items(track(name,id))")
    for track in playlistTracks["items"]:
        if trackId in track["track"]["id"]:
            return True
    return False


async def addSongToPlaylist(trackId, spInstance):
    # add song to playlist
    spInstance.playlist_add_items(playlist_id=SPOTIFY_PLAYLIST_ID, items=[trackId], position=None)




@client.event
async def on_ready():
    print(f'{client.user.name} has connected to Discord!')

@client.event
async def on_message(message):
    # Check if the message was from the bot -- ignore if so
    if message.author == client.user:
        return
    #  Check if it's in the dedicated channel, then Check for Spotify URL,
    if message.channel.id != CHANNEL_ID:
        print("URL posted outside of dedicated channel")
        return
    if SPOTIFY_TRACK_URL_HEADER in message.content.lower():
        message_text = await handleSpotifyLink(message.content, True)
        embed = discord.Embed(title=message_text, color=HEX_GREEN)
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
                    embed = discord.Embed(title=responseText, color=HEX_GREEN)
                    await message.channel.send(embed=embed)
                    print(responseText)
                else:
                    responseText = "Looks like a misformatted request, please make sure to use '!hipster' followed by a space, then the Spotify URL."
                    embed = discord.Embed(title=responseText, color=0xff0000)
                    await message.channel.send(embed=embed)
                    # print(responseText)

            # Handle !command request
            elif "!command" in message.content.lower():
                embed = discord.Embed(title="Lobot Available Commands", description="Be sure to @Lobot before adding your command!\n\n!hipster: Find hipster rating of Song based on Spotify URL\n\n!playlist: Check if Spotify song (url) is in the playlist without attempting to add.\n\n!applesearch looks for songs in Apple Music\n\n!applify searches the Spotify URL for Apple version; does not add link to the Playlist\n\n!command: Show list of commands", color=0x0000ff)
                await message.channel.send(embed=embed)
                # print("!command fired")
            elif "!playlist" in message.content.lower():
                await handleCommand("!playlist", message)
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
                        responseColor = HEX_GREEN
                    else:
                        responseText = "No match detected"
                        responseColor = HEX_YELLOW
                    embed = discord.Embed(title="[BETA] Applify Results", description=responseText, color=responseColor)
                    await message.channel.send(embed=embed)
                    print(responseText)
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
                    embed = discord.Embed(title="Apple Search Results", description=responseText, color=HEX_GREEN)
                    await message.channel.send(embed=embed)
                    # print(responseText)
                else:
                    responseText = "Looks like you're trying to send a link instead of a search. Try using !applify instead."
                    embed = discord.Embed(title=responseText, color=HEX_RED)
                    await message.channel.send(embed=embed)
            else:
                embed = discord.Embed(title="Hello, still working on myself; try checking out !command for available functions!", color=0xffff00)
                await message.channel.send(embed=embed)
                print("Failure fired")



client.run(TOKEN)
