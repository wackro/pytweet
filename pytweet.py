"""Posts stuff to twitter"""

from urllib import request
import tweepy
import base64
import re
import traceback
import constants
import sys
from Crypto.Cipher import AES

class Tweeter:
    """Standard tweeter"""
    def __init__(self):
        """Initialises the API with constants from constants.py	"""
        try:
            auth = tweepy.OAuthHandler(constants.API_KEY, constants.API_SECRET)
            auth.set_access_token(constants.ACCESS_TOKEN,
                                    constants.ACCESS_TOKEN_SECRET)
            self.api = tweepy.API(auth)
        except:
            print("Failed to establish API connection!")
            raise
        
    def tweet(self, message):
        """Posts an update to the remote twitter app.

        :param message: the message to tweet
        """
        if len(message) > 140:
            raise ValueError("Your tweet is too long!")
        
        try:
            response = self.api.update_status(status=message)
            print("Tweeted '" + message + "'!")
            return response
        except:
            print("Failed to tweet message!")
            raise

class AESEncryptedTweeter(Tweeter):
    """Encrypted tweeter.

    Tweets base64-encoded AES-encrypted messages
    """
    def __init__(self):
        """Calls the parent constuctor and sets the character set for
         byte-conversion to latin-1
        """
        super().__init__()
        self._CHARSET = "latin-1"

    def encrypt(self, string):
        """Takes a plaintext string and returns encrypted bytes

        :param: srting the input string
        """
        try:
            e = AES.new(constants.CRYPTO_KEY,
                    AES.MODE_CBC,
                    constants.CRYPTO_VECTOR)
            
            # AES is a block cypher that works on input strings that are
            # multiples of 16 only, so pad the input with 0s if needs be.
            l = len(string)
            encrypted = e.encrypt(string.zfill(l + 16 - (l % 16)))
            return encrypted
        except:
            print("Failed to encrypt string!")
            raise

    def tweet(self, message, plaintext=None):
        """Tweets a base64-encoded AES-encrypted message.
        
        Plaintext such as hashtags can be provided too, which is appended to the
        encrypted message.
        
        :param toEncrypt: the first part of the tweet, to be encrypted
        :param plaintext: the optional, second part of the tweet, to be
        appended (hashtags, for example)
        """
        # encrypt and encode our stuff
        m = base64.b64encode(self.encrypt(message)).decode(self._CHARSET)
       
        # optionally stick plaintext on the end
        if plaintext is not None:
            m += " " + plaintext
        
        # ...and yield to our superclass to tweet() the mesage.
        return super().tweet(m)

class TweeterFactory:
    """Generates the required Tweeter type"""
    def createTweeter(args):
        if("-e" in args):
            return  AESEncryptedTweeter()
        
        return Tweeter()

def printUsage():
    print("Usage: pytweet.py message [-e [plaintext]]")

def main():
    # if they are playing silly buggers with the amount of args, tell them so
    if(len(sys.argv) == 1 or len(sys.argv) > 4):
        printUsage()
        return
    
    # if they are playing silly buggers with argv[2], tell them so
    if(len(sys.argv) > 2 and sys.argv[2] != "-e"):
        printUsage()
        return
	
    # create the appropriate Tweeter
    t = TweeterFactory.createTweeter(sys.argv)
    	
    # the encrypted tweeter takes argv[3] as a parameter if it exists
    try:
        if len(sys.argv) == 4:
            t.tweet(sys.argv[1], sys.argv[3])
        else:
            t.tweet(sys.argv[1])
    except Exception as e:
        print(e)
        traceback.print_stack()
		
if __name__ == "__main__":
    main()
