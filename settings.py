bindir = 'pictures'
thumbdir = '.thumbnails'
thumbsize = (64,48) # y-value should also be the height of small widgets
wheight = '48dp'    # height of small widgets
Wheight = '64dp'    # larger widgets, such as main controls
sqldb = 'data.sqlite3'
strprefix = (
    b'https://en.gren.ag/e/',
)
presetkeys = {
    'shelf': (
        ( 0, 'Ansuz', 'location'),
    ),
    'set': (
        ( 0, 'Ansuz', 'set_id'),
        ( 0, 'Ansuz', 'vehicle_type'),
    ),
    'box': (
        ( 0, 'Ansuz', 'box_type'),
        ( 0, 'Ansuz', 'tare'),
        #( 0, 'Isaz', 'shelf'),
    ),
    'part': (
        ( 0, 'Ansuz', 'number_in_set'),
        ( 0, 'Ansuz', 'weight'),
        #( 0, 'Isaz', 'set' ),
        #( 0, 'Isaz', 'box' ),
    ),
}
#preset_types = [
#    oType('Box', {'Ansuz': ['Width [m]','Length [m]','Height [m]','Tare [kg]']}),
#    oType('Cup', {'Ansuz': ['Diameter [m]','Height [m]','Volume [m³]','Tare [kg]']}),
#    oType('Battery', {'Ansuz': ['Battery technology','Capacity in Ah','Voltage','Weight']}),
#    oType('Motor, asynchronous', {'Ansuz': ['Number of coils','Max voltage','Power [W]','RPM']}),
#]

known_protocols = (
    b'http://',    b'https://',
    b'ftp://',
    b'sftp://',
    b'ssh://',
    b'smtp://',
    b'telnet://',
    b'pop3://',
    b'imap://',    b'imaps://',
    b'irc://',
    b'torrent://',
    b'rsync://',
)

encoding = 'utf-8'
# general settigs
prefix = b'ch.engrenage'
# UNIX
video_dev = '/dev/video0'
dummy_image_path = '/storage0/naspi/metameta/mtag/data/'
export_dir = '/tmp/'
