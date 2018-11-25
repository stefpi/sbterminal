#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import re
import time
import json
import psutil
import requests
from slackclient import SlackClient

slackClient = SlackClient('Replace this with bot token from slack')
token = 'Replace this with bot token taken from slack'

cwd = os.getcwd()

userList = slackClient.api_call('users.list')
for user in userList.get('members'):
    if user.get('name') == 'Replace this with bot name':
        slackUserID = user.get('id')
        print slackUserID
        print 'User id retrieved'
        break

if slackClient.rtm_connect():
    print 'Connected!'

    while True:
        for message in slackClient.rtm_read():
            if 'text' in message and message['text'].startswith('<@%s>'
                    % slackUserID):
                print 'Message received: %s' % json.dumps(message, indent=2)

                messageText = message['text'].split('<@%s>'% slackUserID)[1].strip()

                if re.match(r'.*(cpu).*', messageText, re.IGNORECASE):
                    cpuPct = psutil.cpu_percent(interval=1, percpu=False)

                    slackClient.api_call('chat.postEphemeral',
                        channel=message['channel'],
                        text='My Cpu is at %s%%' % cpuPct,
                        as_user=True)

                if re.match(r'.*(cmd:).*', messageText, re.IGNORECASE):
                    msg = messageText
                    cmd = msg.replace('cmd:','')
                    os.system("%s > output.txt" % cmd)

                    auth_output_payload = {
                        "text": "please enter your password",
                        "attachments": [
                            {
                                "text": "Please authenticate yourself",
                                "fallback": "you were unable to be authenticated",
                                "callback_id": "bot_auth",
                                "color": "#3AA3E3",
                                "attachment_type": "default",
                                "actions": [
                                    {
                                        "name": "auth",
                                        "text": "Enter Password",
                                        "type": "button",
                                        "value": "enter password"
                                    }
                                ]
                            }
                        ]
                    }

                    #output_file = {
                        #’file' : ('/home/pi/ws/slackbots/rpi0/output.txt', open('/home/pi/ws/slackbots/rpi0/output.txt', 'rb'), 'txt')
                    #}

                    output_file = {
                        "file" : ("/" + cwd  + "/output.txt", open("/" + cwd  + "/output.txt", "rb"), "txt")
                    }

                    cmd_output_payload = {
                        "filename":"output.txt",
                        "token":token,
                        "channels":message['channel']
                    }

                    req = requests.post("https://slack.com/api/files.upload", params=cmd_output_payload, files=output_file)
                else:
                    print "command not detected"
