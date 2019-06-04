import os.path
import binascii
import re
import time
import tweepy
import requests
import difflib
import sys
from slackclient import SlackClient


url = 'https://www.eventbrite.co.uk/e/steelcon-2019-tickets-47710394073#tickets'
slack_api_key = 'xoxp-PUT-YOUR-SLACK-KEY-HERE'
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

twitter_cfg = {
    "consumer_key"        : "",
    "consumer_secret"     : "",
    "access_token"        : "",
    "access_token_secret" : ""
}

twitter_target = "GlennPegden"
auth = tweepy.OAuthHandler(twitter_cfg['consumer_key'], twitter_cfg['consumer_secret'])
auth.set_access_token(twitter_cfg['access_token'], twitter_cfg['access_token_secret'])
twitter_api = tweepy.API(auth)


r = requests.get(url, headers)
page = r.content.decode("utf-8")
page = re.sub(r"Fancy seeing you here! Did you know we\'re hiring\?", "", page)
page = re.sub(r"Oh hi there, whatcha looking for\? Wanna chat about joining our team\?", "", page)
page = re.sub(r"Want to be part of the team behind the source code\? We\'re hiring!", "", page)
page = re.sub(r"Like what you see here\? Want to help us build more\? We\'re hiring!", "", page)
page = re.sub(r"Well hi there, like what you see\?.+", "", page)
page = re.sub(r"Come here often\? Wanna make it a thing\? We're hiring!", "", page)

page = re.sub(r"input type=\"hidden\" name=\"source_id\" value=.+", "", page)
page = re.sub(r"=\"https://cdn.evbstatic.com/.+\"", "", page)
page = re.sub(r".+csrfmiddlewaretoken.+", "", page)
page = re.sub(r".+data-event-action=\"SigninAttempt\".+", "", page)
page = re.sub(r".+csrfToken.+", "", page)
page = re.sub(r".+orderStartUuid:.+", "", page)
page = re.sub(r".+orderStartSig:.+", "", page)
page = re.sub(r".+model: \{\"display_date\":.+", "", page)
page = re.sub(r".+window.bugsnag.+", "", page)
page = re.sub(r"\ssessionID: \'.+", "", page)
page = re.sub(r".+correlationID:.+", "", page)
page = re.sub(r"mediator\.set\(\'gaS.+\)", "", page)

CRC = binascii.crc32(page.encode())

if os.path.exists("crc.txt") and os.path.exists("page.txt"):
    file = open("crc.txt", "r")
    CRC2 = int(file.read())
    file.close()

    file = open("page.txt", "r")
    oldPage = file.read()
    file.close()


    if CRC == CRC2:
        print("Files Match")
#        sc = SlackClient(slack_api_key)
#        sc.api_call(
#            "chat.postMessage",
#            channel="@Glenn",
#            text="Dude, nothing has changed on the Steelcon eventbrite page :tada:"
#        )
#        status = twitter_api.send_direct_message(twitter_target,text="Dude, the Steelcon page NOT changed :(") 


    else:
        print("No Match, it might be SteelCon time!")

        sc = SlackClient(slack_api_key)
        sc.api_call(
            "chat.postMessage",
            channel="@Glenn",
            text="Dude, something has changed on the Steelcon eventbrite page :tada: " +str(CRC2) +" != " +str(CRC)
        )
#        status = twitter_api.send_direct_message(twitter_target, text="Dude, the Steelcon page has changed! Hurrah! The new CRC is" + str(CRC))

        edate = str(int(time.time()))

        file = open("page-"+edate+"_old.txt", "w")
        file.write(str(oldPage).replace("\\n", "\n"))
        file.close()
        file = open("page-"+edate+"_new.txt", "w")
        file.write(str(page).replace("\\n", "\n"))
        file.close()

        oldPageArray = str(oldPage).split("\n")
        newPageArray = str(page).split("\n")

        for line in difflib.context_diff(oldPageArray,newPageArray):
            sys.stdout.write(line)  


file = open("page.txt", "w")
file.write(str(page).replace("\\n", "\n"))
file.close()
file = open("crc.txt", "w")
file.write(str(CRC))
file.close()
file = open("old_page.txt", "w")
file.write(str(oldPage).replace("\\n", "\n"))
file.close()
