"""
Smart ThrowAway Email v0.1

A script to use on a throwaway email address.

It will poll for new mails and tries to click on the request links.
So you do not have to log in to your temp email to activate the account.

Use a Smart ThrowAway Email which will process the email
for you such as clicking activation links

TODO: Implement IDLE instead of pinging
TODO: Smooth the encoding out
Obstacle: Some websites require you to be logged in before you can activate
"""
import quopri
import re
import requests
import imaplib
import email
import time
from urllib import parse

# Email Login settings
email_login = 'username@gmail.com'
email_password = 'password'
email_server = 'imap.gmail.com'
email_port = '993'

poll_time = 10


#Activate URL's containing
wordlist = ['conf','activ','subscr','verif']

#Discard URL's containing
banned_word_list = ['unsub']

print("Starting SmartMail v0.1...")

#Connect and Fetch email
def connect_mail():
    m = imaplib.IMAP4_SSL(email_server, email_port)  # Connect to an IMAP4 sever over SSL, port 993
    m.login(email_login, email_password)  # Identify the client user and password
    m.select()  # Select a the 'INBOX' mailbox (default parameter)

    result, data = m.uid('search', None, "UnSeen") # Search for Unseen Messages, return Unique ID's
    ids = data[0] # data is a list.
    id_list = ids.split() # ids is a space separated string

    try:
        latest_email_id = id_list[-1] # Check for the latest unread email
    except:
        print("No New messages")
        return

    for email_id in latest_email_id: # Iteration not doing antything, because Latest_email is selected above as static
        result, data = m.fetch(latest_email_id, "(RFC822)") # fetch the email body (RFC822) for the given UID
        raw_email = data[0][1] # including headers and alternate payload
        raw_email = quopri.decodestring(raw_email)#.decode('utf-8')
        email_message = email.message_from_bytes(raw_email) # Convert the RAW Email Bytes object to an Email object

        print ('Email Subject Found: ' + str(email_message['Subject']))
        
        maintype = email_message.get_content_maintype() # Check the content type of the mail body
        if maintype == 'multipart': # Text and HTML
            for part in email_message.get_payload(): # If multiple payloads, iterate until Text is found
                if part.get_content_maintype() == 'text':
                    email_content_cleaned = part.get_payload()
                    activate_email(email_content_cleaned)
        elif maintype == 'text':
            #Search and replace all newline characters before parsing
            email_content = email_message.get_payload()
            email_content_cleaned = email_content #.rstrip('\n\r')
            activate_email(email_content_cleaned)

def activate_email(content):

    url_list = re.findall('\"(http[\s\S]*?)\"', content, re.M) # Search for links, Multi Line

    activation_links = []
    for url in url_list:
        if any(word in url for word in wordlist): # Check if URL contains words from the words list
            if not any(word in url for word in banned_word_list ): # Check if URL does not contain banned words
                url = parse.unquote(url)
                url = url.replace("&amp;","&")
                activation_links.append(url.replace('\r\n', '')) # Remove all the newline characters before appending link
                print(str(activation_links)) # Print for DEBUG
                
    headers = {
        'Accept-Encoding': 'gzip, deflate, sdch',
        'Accept-Language': 'da-DK,da;q=0.8,en-US;q=0.6,en;q=0.4',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.94 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Connection': 'keep-alive',
    }

    for link in activation_links:
        try:
            requests.get(link, headers = headers)
            print("Requested Link: " + link)
        except Exception as e:
            print("Request Failed: " + str(e) + " " + link)

while True:
    connect_mail()
    time.sleep(poll_time)
