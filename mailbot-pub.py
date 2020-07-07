import imaplib
import mailparser
import datetime
import telebot

from bs4 import BeautifulSoup

def parse_body_jira(email_message):

    if (email_message.subject.find("[JIRA]") >= 0):

        txt = parse_body(email_message).splitlines()
        if len(txt) < 5:
            return {}
        mydict = {}
        mydict['БЦ'] = txt[2][:-2].split(' ')[-1]
        mydict['Задача'] = txt[3]
        mydict['URL'] = "https://jira.domain.local/browse/" + txt[3]
        mydict['Описание'] = txt[4]
        for i in range(5,len(txt)):
            if txt[i][-1] == ':':
                mydict[txt[i][:-1]] = txt [i+1]
                i +=1
        return mydict

    else:
        return ""


def parse_body( email_message):
   # html = email_message.text_html
    soup = BeautifulSoup(email_message.text_html[0],'html.parser')
    text = soup.get_text()
    # break into lines and remove leading and trailing space on each
    lines = (line.strip() for line in text.splitlines())
    # break multi-headlines into a line each
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    # drop blank lines
    text = '\n'.join(chunk for chunk in chunks if chunk)
    return(text)


def read_unread_mails( sender_of_interest = 'no_reply@domain.local'):

    imap = imaplib.IMAP4_SSL('mail.domain.local')
    imap.login('username', 'password')
    #imap.select("inbox",)
    imap.select()
    
    # Use search(), not status()
    status, response = imap.search(None,  '(UNSEEN)')
    unread_msg_nums = response[0].split()

    # Print the count of all unread messages
    ##print len(unread_msg_nums)

    # Print all unread messages from a certain sender of interest
    status, response = imap.search(None, '(UNSEEN)', '(FROM "%s")' % (sender_of_interest))
    unread_msg_nums = response[0].split()
    da = []
    

    bot = telebot.TeleBot('999999999:AAaaaaaaaaAAAAAaaaaaaAAAAAAAaaaaaAA')

    for e_id in unread_msg_nums:
        #result, data = mail.fetch(latest_email_id, )
        _, response = imap.fetch(e_id, "(RFC822)")
        email_message =  mailparser.parse_from_bytes(response[0][1])
    
        text = parse_body_jira(email_message)
        try:
            if  (text['Приоритет'] == 'Неотложный'):   #(text['Приоритет'] == 'Высокий') |
                  print(text)
                  bot.send_message( -333333333, text["БЦ"] +" (неотложка).\n" + text['Тип запроса'] +': ' +text["Описание"] +'.\n'+ text["URL"] + "\n" + text["Дата создания"],  )
            elif (text['Тип запроса'] == 'Инцидент'):
                  print(text)
                  bot.send_message( -333333333, text["БЦ"] +" (инцидент).\n" + text['Приоритет'] +' приоритет. ' +text["Описание"] +'.\n'+ text["URL"] + "\n" + text["Дата создания"],  )
            da.append(response[0][1])
        except:
            continue
   
read_unread_mails()
