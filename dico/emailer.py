from django.core.mail import send_mail

class Emailer():
    # Sends a reset password message to the specified email recipient.
    def sendResetPasswordEmail(recipientEMail, resetURL):
        htmlMessage = """\
<p>There has been a request to reset your password for I Do Declare.</p>
<p>Click <a href="%s">here</a> to reset your password.</p>

<b>The I Do Declare Team</b>
""" % resetURL

        message = """\
There has been a request to reset your password for I Do Declare.
Open the following link in your web browser to reset your password:

%s

Thanks.
The I Do Declare Team
""" % resetURL
        
        send_mail('Password Reset', message, 'feedback@idodeclare.org',
            [recipientEMail], fail_silently=False, html_message=htmlMessage)
    
    def merge(html, dir):
		p = re.compile(r'{{\s*([^}\s]+)\s*}}')
		def f(match):
			s = match.group(1)
			if s in dir:
				return dir[s]
			else:
				return s
		return p.sub(f, html)