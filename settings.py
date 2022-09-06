bindir = 'pictures'
thumbdir = '.thumbnails'
thumbsize = (64,48) # y-value should also be the height of small widgets
wheight = '48dp'    # height of small widgets
Wheight = '64dp'    # larger widgets, such as main controls
sqldb = 'data.sqlite3'
strprefix = (
    'https://en.gren.ag/e/',
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
