from kivy.factory import Factory as F
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import ObjectProperty


class EntryRow(F.ButtonBehavior, F.BoxLayout):
    id = F.ObjectProperty()


#class TypeRow(F.ButtonBehavior, F.BoxLayout):
#    otype = F.StringProperty()
#    otype_bytes = F.ObjectProperty()


class TextFieldEditPopup(F.Popup):
    index = F.NumericProperty(allownone=True)
    rune = F.StringProperty()   # TODO not shown nor editable!
    key = F.ObjectProperty()
    value = F.ObjectProperty()


class TypeSelPopup(F.Popup):
    otypes = F.DictProperty()


class ImportDialog(FloatLayout):
    callback = ObjectProperty(None)
    button = ObjectProperty(None)
    popup = ObjectProperty(None)


#class SaveDialog(FloatLayout):
#    save = ObjectProperty(None)
#    text_input = ObjectProperty(None)
#    cancel = ObjectProperty(None)

