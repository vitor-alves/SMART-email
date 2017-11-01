import os
import sys
import smtplib
import email.message
sys.path.append(os.getcwd())
from pySMART import Device
from pySMART import DeviceList
from pySMART.utils import smartctl_type
from configparser import ConfigParser

def attributes_to_string(dev):
    attributes_text = ""
    header_printed = False
    for attr in dev.attributes:
        if attr is not None:
            if not header_printed:
                attributes_text += "{0:>3} {1:24}{2:4}{3:4}{4:4}{5:9}{6:8}{7:12}" \
                      "{8}".format( 'ID#', 'ATTRIBUTE_NAME', 'CUR', 'WST', 'THR', 'TYPE', 'UPDATED', 'WHEN_FAIL', 'RAW') +"\n"
                header_printed = True
            attributes_text += attr.__str__() + "\n"
    if not header_printed:
        attributes_text += ("This device does not support SMART attributes.\n")
    return attributes_text

def selftests_to_string(dev):
    selftests_text = ""
    if dev.tests is not None:
        if smartctl_type[dev.interface] == 'scsi':
            selftests_text += "{0:3}{1:17}{2:23}{3:7}{4:14}{5:15}".format(
                'ID', 'Test Description', 'Status', 'Hours',
                '1st_Error@LBA', '[SK  ASC  ASCQ]') + "\n"
        else:
            selftests_text += "{0:3}{1:17}{2:30}{3:5}{4:7}{5:17}".format(
                'ID', 'Test_Description', 'Status', 'Left', 'Hours',
                '1st_Error@LBA') + "\n"
        for test in dev.tests:
            selftests_text += test.__str__() + "\n"
    else:
        selftests_text += "No self-tests have been logged for this device.\n"
    return selftests_text
    
def get_SMART_summary(dev):
    summary_text = ""
    if(not dev.smart_capable):
        print("O dispositivo %s nao possui SMART \n" % dev.__str__())
        return None
    summary_text += "Dispositivo: %s\n\n" % dev.__str__()
    summary_text += "Avaliacao: %s\n\n" % dev.assessment
    summary_text += attributes_to_string(dev)
    for i, message in enumerate(dev.messages):
        summary_text += "Mensagem %d: %s\n" % (i, message)
    summary_text += "\n%s" % selftests_to_string(dev)
    return summary_text

def send_email(user, password, recipient, subject, body):
    to = recipient if type(recipient) is list else [recipient]
    
    m = email.message.Message()
    m['From'] = user
    m['To'] = recipient
    m['Subject'] = subject
    m.set_payload(body);
    message = m.as_string()
    
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo()
        server.starttls()
        server.login(user, password)
        server.sendmail(user, to, message)
        server.close()
        print('Email enviado')
    except Exception as e:
        print('problema ao enviar o email: '+ str(e))

devlist = DeviceList()
config = ConfigParser()
config.read("config.ini")
sender_email = config.get('remetente', 'email')
sender_pass = config.get('remetente', 'senha')
receivers = config.get('destinatarios', 'emails')

if(min(len(sender_email), len(sender_pass), len(receivers)) == 0):
    print('configure o arquivo config.ini')
    sys.exit()

for dev in devlist.devices:
    summary_text = get_SMART_summary(dev)

    most_important_values = []
    for i in (5, 187, 197, 198, 188):
        if(dev.attributes[i] is not None):
            most_important_values.append(dev.attributes[i].raw)
    subject = "SMART: [%s] [%s] [%s]" % (dev.assessment, ",".join(most_important_values), os.uname()[1])

    if(summary_text is not None):
        print("%s\n%s" % (subject, summary_text))
        send_email(sender_email, sender_pass, receivers, subject, summary_text)
