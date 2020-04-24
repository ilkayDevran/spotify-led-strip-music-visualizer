#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# @author: Ilkay Tevfik Devran
# @Date: 23.04.2020
#

import os
import json
from datetime import datetime
import spotipy
import spotipy.util as util
from spotipy.oauth2 import SpotifyOAuth


class SpotifyConnector:
    def __init__(self, SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, SPOTIPY_REDIRECT_URI, USERNAME):        
        self.SPOTIPY_CLIENT_ID = SPOTIPY_CLIENT_ID
        self.SPOTIPY_CLIENT_SECRET = SPOTIPY_CLIENT_SECRET
        self.SPOTIPY_REDIRECT_URI = SPOTIPY_REDIRECT_URI
        self.USERNAME = USERNAME
        self.permission_scopes = 'user-modify-playback-state user-read-currently-playing user-read-playback-state'
        self.token = ''
        self.lastRefreshedTimeOfToken = ''
                
    # --- * Private Methods * ----
    def __authorize(self):
        """
            Handle the authorization workflow for the Spotify API.
        """
        try:
            self.token = util.prompt_for_user_token(self.USERNAME,
                                                    self.permission_scopes,
                                                    self.SPOTIPY_CLIENT_ID,
                                                    self.SPOTIPY_CLIENT_SECRET,
                                                    self.SPOTIPY_REDIRECT_URI
                                                    )
            # Instantiate multiple Spotify objects because sharing a Spotify object can block threads
            self.sp_gen = spotipy.Spotify(auth=self.token)
            self.sp_vis = spotipy.Spotify(auth=self.token)
            self.sp_sync = spotipy.Spotify(auth=self.token)
            self.sp_load = spotipy.Spotify(auth=self.token)
            self.sp_skip = spotipy.Spotify(auth=self.token)
            text = "Successfully connected to {}'s account.".format(self.sp_gen.me()["display_name"])
            print(SpotifyConnector._make_text_effect(text, ["green"]))
        except:
            raise Exception("Unable to authenticate Spotify user.")
    
    def __setup(self):
        if not os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cache')):
            os.makedirs('cache')
        if not os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cache/access_token.json')):
            with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cache/access_token.json'), 'w') as outfile:
                self.lastRefreshedTimeOfToken = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                json.dump({'TOKEN': self.token,
                            'LastRefreshedTime': self.lastRefreshedTimeOfToken
                            }, outfile)
            outfile.close()
        else:
            with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cache/access_token.json'), 'r') as infile:
                cachedData = json.load(infile)
            infile.close()
            #print cachedData['TOKEN'], cachedData['LastRefreshedTime']
            self.lastRefreshedTimeOfToken = datetime.strptime(cachedData['LastRefreshedTime'], '%Y-%m-%d %H:%M:%S')
            if (datetime.now() - self.lastRefreshedTimeOfToken).total_seconds() >= 3600:
                self.__refresh_user_token()

    def __refresh_user_token(self):
        self.__authorize()
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cache/access_token.json'),'w') as outfile:
            self.lastRefreshedTimeOfToken = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            json.dump({'TOKEN': self.token,
                        'LastRefreshedTime': self.lastRefreshedTimeOfToken
                        }, outfile)
        outfile.close()
        print(SpotifyConnector._make_text_effect("Access Token has been refreshed.", ["blue"]))


    # --- * Getter Methods * ---
    def get_available_devices(self):
        """
            Returns a list of user’s available devices
        """
        try:
            return self.sp_gen.devices()
        except:
            return None

    def get_currently_playing_track_info(self):
        """
            Returns a dictionary data of currently playing track on Spotify
        """
        try:
            response = self.sp_gen.current_user_playing_track()
            return {
                        "progress_ms": response["progress_ms"],
                        "uri": response["item"]["uri"],
                        "id": response["item"]["id"],
                        "duration_ms": response["item"]["duration_ms"],
                        "caption": "{} - {}".format(response["item"]["name"].encode('utf-8'), 
                                                    ', '.join((artist["name"].encode('utf-8') for artist in response["item"]["artists"])))
                    }
        except Exception as e:
            print(e.__str__())
            return None

    def get_audio_analysis_for_track(self, track_id):
        """
            Returns audio analysis for a track based upon its Spotify ID Parameters:
                * track_id - a track URI, URL or ID
        """
        response = self.sp_gen.audio_analysis(track_id)
        try:
            return {
                        "duration_sec": response["track"]["duration"],
                        "end_of_fade_in_sec": response["track"]["end_of_fade_in"],
                        "start_of_fade_out_sec": response["track"]["start_of_fade_out"],
                        "analysis_sample_rate": response["track"]["analysis_sample_rate"],
                        "tempo": response["track"]["tempo"],
                        "segments": response["segments"]
                    }
        except:
            return None



    @staticmethod
    def _make_text_effect(text, text_effects):
        """"Applies text effects to text and returns it.
        Supported text effects:
            "green", "red", "blue", "bold"
        Args:
            text (str): the text to apply effects to.
            text_effects (list): a list of str, each str representing an effect to apply to the text.
        Returns:
            text (str) with effects applied.
        """
        effects = {
            "green": "\033[92m",
            "red": "\033[91m",
            "blue": "\033[94m",
            "bold": "\033[1m"
        }
        end_code = "\033[0m"
        msg_with_fx = ""
        for effect in text_effects:
            msg_with_fx += effects[effect]
        msg_with_fx += text
        msg_with_fx += end_code * len(text_effects)
        return msg_with_fx


    def run(self):
        self.__authorize()
        self.__setup()


