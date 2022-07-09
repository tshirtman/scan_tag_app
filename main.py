# vim: ts=4 number nowrap
from pathlib import Path
from uuid import uuid4
import logging
from os import rename

from kivy.utils import platform
from kivy.app import App
from kivy.factory import Factory as F
from kivy.clock import Clock, mainthread
from kivy.resources import resource_add_path

from xcamera.xcamera import XCamera
from zbarcam.zbarcam import ZBarCam

from db import get_engine, save_entry, get_entry, get_entries
import settings

resource_add_path("./xcamera/")

logging.basicConfig()
logger = logging.getLogger(__name__)


class EntryRow(F.ButtonBehavior, F.BoxLayout):
    id = F.StringProperty()


class TextFieldEditPopup(F.Popup):
    index = F.NumericProperty(allownone=True)
    key = F.StringProperty()
    value = F.StringProperty()

#
# Kivy Application
#
class Application(App):
    target_entry = F.DictProperty()
    entries = F.ListProperty()

    def __init__(self):
        super().__init__()
        self.db = get_engine(Path(self.user_data_dir) / settings.sqldb)
        self.load_entries()
        Path(self.user_data_dir, settings.bindir).mkdir(parents=True, exist_ok=True)
        Path(self.user_data_dir, settings.thumbdir).mkdir(parents=True, exist_ok=True)

    def load_entries(self):
        self.entries = get_entries(self.db)

    def switch_screen(self, target):
        self.root.current = target

    def scan_id(self):
        if platform == 'android':
            F.ZBarCamPopup().open()
        else:
            # temporary hack to simulate scanning a code
            id = str(uuid4())
            Clock.schedule_once(lambda *_: self.edit_entry(id), 2)

    def scan_input(self, field):
        """ TODO set text input field to content of next QR code (open popup) ; set focus to next input field """

    @staticmethod
    def sanitize(image_name):
        for u in settings.strprefix:
            image_name.lstrip(u)
        if image_name.startswith('http'):
            parsed = urlparse(image_name)
            return f"{parsed.netloc}_{parsed.path.replace('/', '_')}_{parsed.params}_{parsed.query.quote()}"
        else:
            return image_name.replace('/', '_')


    def picture_for(self, target_id, thumbnail = False):
        if thumbnail:
            return str(
                Path(
                    self.user_data_dir,
                    settings.thumbdir,
                    self.sanitize(target_id) if target_id else '_'
                ).with_suffix(".jpeg")
            )
        else:
            return str(
                Path(
                    self.user_data_dir,
                    settings.bindir,
                    self.sanitize(target_id) if target_id else '_'
                ).with_suffix(".jpeg")
            )

    def user_dir_do_something(self):
        pass

    @mainthread
    def save_picture(self, camera, filename):
        rename(filename, self.picture_for(self.target_entry["id"]))

        # thumbnail generation
        from PIL import Image
        im = Image.open(filename)
        im = im.resize(settings.thumbsize)
        im.save(filename.replace(bindir,thumbdir))
        im.close()

        self.root.get_screen("editor").ids.picture.reload()

    def snap_picture(self):
        target_id = self.target_entry["id"]
        if platform == 'android':
            F.XCameraPopup().open()

    def edit_entry(self, entry_id):
        self.target_entry = get_entry(self.db, entry_id)
        self.switch_screen("editor")

    def edit_text_field(self, index=None):
        data = self.target_entry["text_fields"][index] if index is not None else {}
        p = F.TextFieldEditPopup(
            index=index,
            key=data.get("key", ""),
            value=data.get("value", ""),
        )
        p.open()

    def save(self):
        save_entry(self.db, self.target_entry)
        self.load_entries()
        self.switch_screen("entries")

    def save_text_field(self, index=None, key="", value=""):
        data = {"key": key, "value": value}
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
