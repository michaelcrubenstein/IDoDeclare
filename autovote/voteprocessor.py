#!/usr/bin/env python
#
# Very basic example of using Python and IMAP to iterate over emails in a
# gmail folder/label.  This code is released into the public domain.
#
# RKI July 2013
# http://www.voidynullness.net/blog/2013/07/25/gmail-email-with-python-via-imap/
#
import sys
import imaplib
import getpass
import email
import email.header
import email.parser
import datetime
 
EMAIL_ACCOUNT = "autovotedev@idodeclare.org"
EMAIL_PASSWORD = "9NQsmDt8"
EMAIL_FOLDER = "INBOX"

class VoteProcessor():
    def process_body(self, fromEmail, body):
        data = [line.strip().split(':') for line in body.split('\n') if line.strip()]
        target = {'email' : "", 'first name' : "", 'last name' : "", 'address' : "", \
                  'zipcode' : "", 'petition' : "", 'vote' : ""}
        print('----------')
        print(data)
        for line in data:
            key = line[0].strip().lower()
            if key in target:
                target[key]=line[1]
            elif key == 'support':
                target['petition'] = line[1]
                target['vote'] = 1
            elif key == 'oppose':
                target['petition'] = line[1]
                target['vote'] = 0
        print('----------')
        print (target)
        
    def process_mailbox(self, M):
        """
        Do something with emails messages in the folder.  
        For the sake of this example, print some headers.
        """
 
        rv, data = M.search(None, "ALL")
        if rv != 'OK':
            print ("No messages found!")
            return
 
        bp = email.parser.BytesParser()
        for num in data[0].split():
            rv, data = M.fetch(num, '(RFC822)')
            if rv != 'OK':
                print ("ERROR getting message", num)
                return
 
            msg = bp.parsebytes(data[0][1])
            #             decode = email.header.decode_header(msg['Subject'])[0]
            #             subject = unicode(decode[0])
            #             print ('Message %s: %s' % (num, subject))
            #             print ('Raw Date:', msg['Date'])
            #             # Now convert to local date-time
            #             date_tuple = email.utils.parsedate_tz(msg['Date'])
            #             if date_tuple:
            #                 local_date = datetime.datetime.fromtimestamp(
            #                     email.utils.mktime_tz(date_tuple))
            #                 print ("Local Date:", \
            #                     local_date.strftime("%a, %d %b %Y %H:%M:%S"))
            
            f = msg['From']
            fromEmail = f[f.index('<')+1:f.index('>')]
            print (fromEmail)
            
            for i in msg.walk():
                print('========')
                print(i.get_content_type())
                if i.get_content_type() == 'text/plain':
                    body=i.get_payload()
                    self.process_body(fromEmail, body)

    def open_mailbox(self):
        M = imaplib.IMAP4_SSL('mail.idodeclare.org')
 
        try:
            rv, data = M.login(EMAIL_ACCOUNT, EMAIL_PASSWORD)
        except imaplib.IMAP4.error:
            raise Exception ("LOGIN FAILED!!! ")
 
        print (rv, data)
 
        rv, mailboxes = M.list()
        if rv == 'OK':
            print ("Mailboxes:")
            print (mailboxes)
            
        return M
    
    def run(self): 
        M = self.open_mailbox()
        rv, data = M.select(EMAIL_FOLDER)
        if rv == 'OK':
            print ("Processing mailbox...\n")
            self.process_mailbox(M)
            M.close()
        else:
            print ("ERROR: Unable to open mailbox ", rv)
 
        M.logout()
