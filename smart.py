from pySMART import Device
from pySMART import DeviceList
from pySMART.utils import smartctl_type

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
    
def print_to_log(dev):
    summary_text = ""
    if(not dev.supports_smart):
        summary_text += "O dispositivo %s nao possui SMART \n" % dev.__str__() 
        return
    summary_text += attributes_to_string(dev)
    summary_text += "Dispositivo: %s\n" % dev.__str__()
    summary_text += "Avaliacao: %s\n" % dev.assessment
    for i, message in enumerate(dev.messages):
        summary_text += "Mensagem %d: %s\n" %i %message 
    summary_text += selftests_to_string(dev)
    return summary_text


def email_summary(summary_text):
    print("test email")


devlist = DeviceList()
for dev in devlist.devices:
    summary_text = print_to_log(dev)
    print(summary_text)
    email_summary(summary_text)

