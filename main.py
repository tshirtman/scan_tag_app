from pathlib import Path
from uuid import uuid4
import logging

from kivy.app import App
from kivy.factory import Factory as F
from kivy.clock import Clock

from db import get_engine, save_entry, get_entry, get_entries

logging.basicConfig()
logger = logging.getLogger(__name__)


class EntryRow(F.ButtonBehavior, F.BoxLayout):
    id = F.StringProperty()


class TextFieldEditPopup(F.Popup):
    index = F.NumericProperty(allownone=True)
    name = F.StringProperty()
    value = F.StringProperty()


class Application(App):
    target_entry = F.DictProperty()
    entries = F.ListProperty()

    def __init__(self):
        super().__init__()
        self.db = get_engine(Path(self.user_data_dir) / 'data.sqlite3')
        self.load_entries()

    def load_entries(self):
        self.entries = get_entries(self.db)

    def switch_screen(self, target):
        self.root.current = target

    def scan_id(self):
        # temporary hack to simulate scanning a code
        id = str(uuid4())
        Clock.schedule_once(lambda *_: self.edit_entry(id), 2)

    def snap_picture(self, target):
        ...

    def edit_entry(self, entry_id):
        self.target_entry = get_entry(self.db, entry_id)
        self.switch_screen("editor")

    def edit_text_field(self, index=None):
        data = self.target_entry["text_fields"][index] if index is not None else {}
        p = F.TextFieldEditPopup(
            index=index,
            name=data.get("name", ""),
            value=data.get("value", ""),
        )
        p.open()

    def save(self):
        save_entry(self.db, self.target_entry)
        self.load_entries()
        self.switch_screen("entries")

    def save_text_field(self, index=None, name="", value=""):
        data = {"name": name, "value": value}
        text_fields = self.target_entry["text_fields"][:]
        if index is not None:
            text_fields[index] = data
        else:
            text_fields.append(data)

        self.target_entry["text_fields"] = text_fields

    def remove_text_field(self, index):
        text_fields = self.target_entry["text_fields"][:]
        text_fields.pop(index)
        self.target_entry["text_fields"] = text_fields

if __name__ == '__main__':
    Application().run()
