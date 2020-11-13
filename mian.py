import os
import sys
import json
import spotipy
import spotipy.util as util
import spotipy.oauth2 as oauth2
from spotipy import Spotify
import math
from config import CLIENT_ID, CLIENT_SECRET, REDIRECT


'''
work harder, work smarter
but work harder to work smarter
'''
class Connectify(Spotify):

    def __init__(self, auth=None, requests_session=True, client_credentials_manager=None, proxies=None, requests_timeout=None):
        super().__init__( auth, requests_session,
                 client_credentials_manager, proxies,
                 requests_timeout)

    def login(self, username, password):
        pass

    def delete_duplicate(self, list1):
        dict = {}
        for element in list1:
            dict[element] = True
        return list(dict.keys())

    def recommend(self, seed_artists=None, seed_genres=None, seed_tracks=None, limit=20, country=None, **kwargs):
        """
        *** since math.ceil is used, the number of recommended songs will be greater than limit
        Returns:
            this is kinda odd, it returns a list of songs in json notation but they are only the songs in json
        currently can only handle seed_artists or seed_tracks
        rewrite to actually work with Spotify.recommendations

        Purpose: bypasses the 5 input limit on Spotify.recommendations

        make the tracks list more space and time effiecit
        """

        tracks = []
        if seed_artists:
            tracksPerLoop = math.ceil(limit*5/len(seed_artists))
            for i in range(0, len(seed_artists), 5):
                tracks = tracks + self.recommendations(seed_artists = seed_artists[i:i+4], limit = tracksPerLoop)['tracks']

        elif seed_tracks:
            tracksPerLoop = math.ceil(limit * 5 / len(seed_tracks))
            for i in range(0, len(seed_tracks), 5):
                tracks = tracks + self.recommendations(seed_tracks=seed_tracks[i:i + 5], limit=tracksPerLoop)['tracks']

        return tracks

    def create_playlist_from_two_artist(self, list1, list2, type='artist', limit=20, playlistName = None):
        """
                *** make compatable with collabrative play lists
                this is meant for longer playlsit with many songs with two playlists that are simalar

                :param self: current Spotify Obj
                :param list1: playlist id
                :param list2: playlist id
                :param type: type of list to return
                        'artist' or 'track'
                :param limit: number of songs in playlist
                :param playlistName: a str to name the playlist
                :return: none, a fucking play list is made. lets fucking goooo

                PURPOSE: create a playlist from two other playlists
                """
        pl1 = self.playlist(list1)
        pl2 = self.playlist(list2)

        ownerId = [pl1['owner']['id'], pl2['owner']['id']]
        rootOwner = self.me()['id']
        ownerNames = [pl1['owner']['display_name'], pl2['owner']['display_name']]

        if playlistName is None:
            playlistName = 'Connectify between ' + ownerNames[0] + ' and ' + ownerNames[1]

        inCommon = []  # a list of in common factors (artists ext) the list has
        hash = {}
        flaggedhash = {}  # a hash of the songs that were added hash list, stores the song id that wash hashed opn
        """
                hash sub item is using pl1 by defualt but could be improved (time and space) by adding something that detirmins
                which list has less elements and ueses that one 
                i am working fast so i will come back to this 
        """
        rtnKey = 'id'
        for track in pl1['tracks']['items']:
            for artist in track['track']['artists']:
                hash[artist[rtnKey]] = True
                flaggedhash[artist[rtnKey]] = track['track']['id']

        flaggedSongs = []  # songs thayt trigger a match will be added to the new list
        for track in pl2['tracks']['items']:
            try:
                for artist in track['track']['artists']:
                    try:
                        if hash[artist[rtnKey]] == True:
                            inCommon.append(artist[rtnKey])
                            if flaggedhash[artist[rtnKey]] != track['track'][rtnKey]:
                                flaggedSongs.append(flaggedhash[artist[rtnKey]])
                            flaggedSongs.append(track['track'][rtnKey])
                    except KeyError:
                        pass
            except TypeError:
                pass

        flaggedSongs = self.delete_duplicate(flaggedSongs)  # delete duplicates is ineffiect but the lists are small so it does matter
        recommended = self.recommend(seed_artists = inCommon, limit=limit)

        ids = [recommended[x]['id'] for x in range(len(recommended))]  # ids of tracks to be added to the playlist
        ids = flaggedSongs + ids

        pl = self.user_playlist_create(rootOwner, playlistName)

        self.user_playlist_add_tracks(rootOwner, pl['id'], ids[0:limit])

    def create_playlist_from_two_track(self, list1, list2, type='artist', limit=20, playlistName = None):
        """
        *** make compatable with collabrative play lists
        Notes: list1s user

        :param self: current Spotify Obj
        :param list1: playlist id
        :param list2: playlist id
        :param type: type of list to return
                'artist' or 'track'
        :param limit: number of songs in playlist
        :param playlistName: a str to name the playlist
        :return: none, a fucking play list is made. lets fucking goooo

        PURPOSE: create a playlist from two other playlists
        """
        pl1 = self.playlist(list1)
        pl2 = self.playlist(list2)

        ownerId = [pl1['owner']['id'], pl2['owner']['id']]
        rootOwner = self.me()['id']
        ownerNames = [pl1['owner']['display_name'], pl2['owner']['display_name']]

        if playlistName is None:
            playlistName ='Connectify between '+ ownerNames[0] +  ' and ' + ownerNames[1]

        inCommon = []  # a list of in common factors (artists ext) the list has
        hash = {}
        flaggedhash = {} # a hash of the songs that were added hash list, stores the song id that wash hashed opn
        """
                hash sub item is using pl1 by defualt but could be improved (time and space) by adding something that detirmins
                which list has less elements and ueses that one 
                i am working fast so i will come back to this 
        """
        rtnKey = 'id'
        for track in pl1['tracks']['items']:
            try:
                hash[track['track'][rtnKey]] = True
                flaggedhash[track['track'][rtnKey]] = track['track']['id']
                flaggedSongs = [] # songs thayt trigger a match will be added to the new list
                for track in pl2['tracks']['items']:
                    try:
                        if hash[track['track'][rtnKey]] == True:
                            inCommon.append(track['track'][rtnKey])
                            flaggedSongs.append(track['track'][rtnKey])
                    except KeyError:
                        pass

            except TypeError:
                pass


        flaggedSongs = self.delete_duplicate(flaggedSongs) # delete duplicates is ineffiect but the lists are small so it does matter

        recommended = self.recommend(seed_tracks = inCommon, limit = limit)

        ids = [recommended[x]['id'] for x in range(len(recommended))]# ids of tracks to be added to the playlist
        ids = flaggedSongs + ids

        pl = self.user_playlist_create(rootOwner, playlistName)
        self.user_playlist_add_tracks(rootOwner, pl['id'], ids[0:limit])

    def get_user_playlist_names(self, userId, limit = 10):
        """
        :param self: self
        :param userId: id of userhttps://open.spotify.com/playlist/3qxMbjCfMeOE1sk330CzwW?si=VW25orjiR7uhbumulLeOXA
        :return: a list of the users ids and names
        """
        jsonList = self.user_playlists(userId, limit = limit)['items']
        l = len(jsonList)
        lists = [[jsonList[x]['name'] for x in range(l)], [jsonList[x]['id'] for x in range(l)]]
        return lists

    def link_to_id(self, string):
        """
        This only works if the id comes after the forth '/'
        make sure this is alwauys the case before release
        """
        start = 0
        for i in range(4):
            start = string.find('/', start+1)
        end = string.find('?')
        return string[start+1:end]

    def connect_playlists_artist(self, lists, limit = 20, playlistName = None):
        """
        *** to do : add defualt playlist name
        :param lists: a list of playlist ids to refference
        :return: nothing, creates a fucking playlist

        Logic: we will dict hash the lists
        each dictonry entry will have a number (in c i would make this a byte bc i never need more than 30ish scores)
        the number will represent how many times the ARTIST comes up.
        ***NOTICABLE FLAW IN CURRENT ALGORTHEM
            if one user has an artist 5 times but no other user has that artist it will still be scored
            this could potentialy be changed by wieghting each entry ex the forst time an artist is found in a list the
            number is increased by 5 but each subsenent time the number is only increased by 1
        """
        if len(lists) > 5 or len(lists) < 1:
            print('you may input 5 playlists at max')
            pass

        rootOwner = self.me()['id']
        playlists = [] # array of playlists
        ownerId = []
        ownerName = []

        i = 0
        for item in lists:
            playlists.append(self.playlist(item))
            ownerId.append(playlists[i]['owner']['id'])
            ownerName.append(playlists[i]['owner']['display_name'])
            i += 1

        # creating a defualt playlist name
        if playlistName == None:
            playlistName = "Connectify between "
            l = len(ownerName) # temp variable j used to as length of playlists inputed
            for i in range(l-1):
                playlistName = playlistName + ownerName[i]  + ", "
            playlistName = playlistName + "and " + ownerName[l-1]

        hash = {} # hashing dict
        longestHash = {}
        longest = [] # keeps track of witch tracks are longest (index 0 being the longest)
        rtnKey = 'id'

        for playlist in playlists:
            weight = 5
            for trackFile in playlist['tracks']['items']:
                try:
                    for artist in trackFile['track']['artists']:
                        try:
                            hash[artist[rtnKey]] += weight
                            weight = 1
                            index = longestHash[artist[rtnKey]]
                            while index > 0 and hash[longest[index]] > hash[longest[index - 1]]:
                                temp = longest[index]
                                longest[index] = longest[index - 1]
                                longest[index - 1] = temp
                                longestHash[longest[index]] = index
                                longestHash[longest[index - 1]] = index - 1
                                index -= 1
                        except KeyError:
                            hash[artist[rtnKey]] = weight
                            weight = 1
                            longest.append(artist[rtnKey])
                            longestHash[artist[rtnKey]] = len(longest) - 1
                except TypeError:
                    pass
            weight = 5

        recommended = self.recommend(seed_artists = longest[0:limit], limit = limit) # a playlist of recommended songs

        ids = [recommended[x]['id'] for x in range(len(recommended))] # geting a string of id's

        plNew = self.user_playlist_create(rootOwner, playlistName) # creating a new playlist
        self.user_playlist_add_tracks(rootOwner, plNew['id'], ids) # adding tracks to the plalist,

        # plNew['id'] return the id to the playlist, not the ids to the song itself

    def connect_playlists_track(self, lists, limit = 20, playlistName = None):
        """     :param lists: a list of play lit ids to refference
                :return: nothing, creates a fucking playlst

                """
        if len(lists) > 5 or len(lists) < 1:
            print('you may input 5 playlists at max')
            pass
        rootOwner = self.me()['id']
        playlists = [] # array of playlists
        ownerId = []
        ownerName = []
        i = 0
        for item in lists:
            playlists.append(self.playlist(item))
            ownerId.append(playlists[i]['owner']['id'])
            ownerName.append(playlists[i]['owner']['display_name'])
            i+=1

        # creating a defualt playlist name
        if playlistName == None:
            playlistName = "Connectify between "
            l = len(ownerName) # temp variable j used to as length of playlists inputed
            for i in range(l-1):
                playlistName = playlistName + ownerName[i]  + ", "
            playlistName = playlistName + "and " + ownerName[l-1]

        hash = {} # hashing dict
        longestHash = {}
        longest = [] # keeps track of witch tracks are longest (index 0 being the longest)
        rtnKey = 'id'
        for playlist in playlists:
            weight = 5
            for track in playlist['tracks']['items']:
                try:
                    hash[track['track'][rtnKey]] += weight
                    weight = 1
                    index = longestHash[track['track'][rtnKey]]
                    while index > 0 and hash[longest[index]] > hash[longest[index - 1]]:
                        temp = longest[index]
                        longest[index] = longest[index - 1]
                        longest[index - 1] = temp
                        longestHash[longest[index]] = index
                        longestHash[longest[index - 1]] = index - 1
                        index -= 1
                except KeyError:
                    hash[track['track'][rtnKey]] = weight
                    weight = 1
                    longest.append(track['track'][rtnKey])
                    longestHash[track['track'][rtnKey]] = len(longest) - 1
                except TypeError:
                    pass
            weight = 5

        inCommon = longest[0:limit] # id's of the tracks that are in Common

        recommended = self.recommend(seed_tracks = inCommon, limit = limit) # a playlist of recommended songs

        ids = [recommended[x]['id'] for x in range(len(recommended))] # geting a string of id's

        plNew = self.user_playlist_create(rootOwner, playlistName) # creating a new playlist
        self.user_playlist_add_tracks(rootOwner, plNew['id'], ids) # adding tracks to the plalist,
        # plNew['id'] return the id to the playlist, not the ids to the song itself

username = '22brul7byn6y4j7mbf7b3lqni?si=mbEmeKifRma_KPfhvCeJEw'
scope = 'playlist-modify-private, playlist-modify-public'
# token access
try:
    token = util.prompt_for_user_token(username, scope, client_id=CLIENT_ID, client_secret=CLIENT_SECRET, redirect_uri=REDIRECT)
except (AttributeError, JSONDecodeError):
    os.remove(f".cache-{username}")
    token = util.prompt_for_user_token(username, scope, client_id=CLIENT_ID, client_secret=CLIENT_SECRET, redirect_uri=REDIRECT) # add scope


if __name__ == '__main__':
    sp = Connectify(auth = token)
    oliList = sp.link_to_id('https://open.spotify.com/playlist/2qHQAeWodnTIwaBAq2XMFK?si=4XyoD_1SS6SiDwfrCifxVg')
    bradsList = sp.link_to_id('https://open.spotify.com/playlist/5jgWyRgmourpdGKwcJlaVb?si=dP52a-iJQrStZ69yvWAFEg')
    tatumList = '337iuYE8p67CgpYLkxJQAB'
    bradsDailyMix = sp.link_to_id('https://open.spotify.com/playlist/37i9dQZF1E35DWQ5HH0zaM?si=0Uzm2yaxRxqMd9Hv55TH7Q')
    katieList = sp.link_to_id('https://open.spotify.com/playlist/68Femg7qFxcDEqndrJHPek?si=5BFJn2ASSTW8v72oIDUpnw')
    dm2 = sp.link_to_id('https://open.spotify.com/playlist/37i9dQZF1E3ai78NrdudXr?si=qACwzK5VRNeN0ptb9M-Vmw')
    elana = sp.link_to_id('https://open.spotify.com/playlist/58XMVSxtc3XwQfviDelrTX?si=wgMOL-EAQkKXMARRYFi8cg')
    trizz = sp.link_to_id('https://open.spotify.com/playlist/0VBzREMhSP09IJ3rTjhd3O?si=WxZT695bQfWRBBa9L241Og')
    helen = sp.link_to_id('https://open.spotify.com/playlist/5Um4Is3sUnmKRe13pmULDC?si=PfPcdoKJQpCNm1Veh2KGWQ')
    jack = '58nLGY8huHXWPcINIBRDH6'
    shower = '27Pcoi5En5FI9KKIYAdHQ6'
    #sp.createPlaylist(bradsList, oliList)
    #sp.connect_playlists_artist([bradsList, tatumList], limit =19)
    #sp.connect_playlists_track([bradsList, tatumList, oliList], limit =33)
    zach = sp.link_to_id('https://open.spotify.com/playlist/2tyqz4AjNPa3CRXaUIdJyv?si=1Nwi00svSMyBvy4_1tIvcQ')
    rapcav = sp.link_to_id('https://open.spotify.com/user/spotify/playlist/37i9dQZF1DX0XUsuxWHRQd?si=rWDHChIeSzui1G8r4fV3RQ')
    hannahO = sp.link_to_id('https://open.spotify.com/playlist/0q7ec8w5bjEdRBd5FBC86O?si=JOrwoV4KTQSdnkEVdq6eZA')
    mtsnow = sp.link_to_id('https://open.spotify.com/playlist/2NiMMSW7GVKCjpdAFT3hZN?si=qSbwukZGTN-l9h5xuirdxQ')
    sp.create_playlist_from_two_artist(bradsList, zach, limit=30)
