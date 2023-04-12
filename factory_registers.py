from kivy.factory import Factory as F


def register():
    F.register('EntryRow', mod='widgets')
    F.register('TypeRow', mod='widgets')
    F.register('TextFieldEditPopup', mod='widgets')
    F.register('TypeSelPopup', mod='widgets')
    F.register('ImportDialog', mod='widgets')
    F.register('SaveDialog', mod='widgets')
