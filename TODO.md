# Features list

                            Linux   Android IOs     OSX     M$

    QR Scan to open/create      :]      :]
    Take photo                  :]      :]
    Import file                 :|      :S
    QR data for input field     :°      :°
    copy-paste uuids
    object deletion
    preferences dialog (sqlite)
    Workflows (in prefs)[^work]
    bytes_as_braille[^bab]
    Geotagging[^geo]                    :S
    Favourite types[^favt]
    Primary media[^pmedia]
    Additional media[^amedia]
    Recursive tables[^rtab]
    On-/Off-line modes[^onoff]

## Legend
    :] working/done
    :| WIP
    :S WIP with something unexpectedly tricky
    :° was working, but broke ; should be trivial

# Misc missing features

- export popup (confirm save with opt. filename prefix/suffix) ; option to backup-and-keep
- on main screen only, back button to quit (confirm-prompt? in settings)


# Known bugs
- hitting "save" on just a photo (without any property set) will not save anything (except maybe junk in the storage) ; it should at least warn
- cannot delete k/v entries
- geolocation not working


[^bab]: might be tricky because of limited font support in Kivy.
[^work]: Workflows allow a user to follow a specific routine ; see WORKFLOWS keyword in main.py and old_scan_id.py (that was a crappy hack that would deserve some afterthought) ; a workflow is basically a sequence of items that will be processed (in the previous implementation, a set will always be immediately followed by a number of boxes, each followed by a number of parts, until starting with a new set OR adding a new shelf). see branch "sauser" where it sort-of worked (linux, NOT android)
[^geo]: two mechanisms : in preferences, enable/disable geolocation updates (time- and/or distance-based) ; when adding key/value on objects, have a little geotaging button of some sorts that will add the matching k/v pair. if possible, allow full positionning (including orientation from gyros, accel vectors...). value for geodata **CAN** be another object (ie. an uuid)
[^favt]: favourite types : when adding an object (QR scan or uuid4), show popup with types buttons : each button can be enabled/disabled and types will auto-insert k/v fields in EditableEntriesList. There are spcial keys whose value can be auto-inserted (geodata, "where am I", ...). see also AUTOTYPE keyword in main.py ; requested k/v pairs for each type is kept in a list, along with an integer that allows setting a threshold for compulsory values (as well as sorting). ATM, the popup title "Errors detected" is crap and definitely has room for some improvement
[^pmedia]: primary media for an entry (now, a photo) can be : a photo/video/audio recording, an existing file, ... ; use a type-based thumbnail when no preview is available
[^amedia]: in k/v pairs, value can be : a photo/video/audio recording, an existing file, an object in the main list (EntriesScreen), ...
[^rtab]: requires some upstream coding. goes along with predefined POVs. requires careful async coding!
[^onoff]: requires some upstream coding
