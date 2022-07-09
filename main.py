from pathlib import Path
from uuid import uuid4
import logging
from os import rename
from os.path import join
from zipfile import ZipFile
from datetime import datetime

from kivy.utils import platform
from kivy.app import App
from kivy.factory import Factory as F
from kivy.clock import Clock, mainthread
from kivy.resources import resource_add_path

from xcamera.xcamera import XCamera
from zbarcam.zbarcam import ZBarCam

from db import get_engine, save_entry, get_entry, get_entries

resource_add_path("./xcamera/")

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
        self.db = get_engine(self.db_path)
        self.load_entries()
        self.pictures_path.mkdir(parents=True, exist_ok=True)

    @property
    def db_path(self) -> Path:
        return Path(self.user_data_dir) / 'data.sqlite3'

    @property
    def pictures_path(self) -> Path:
        return Path(self.user_data_dir, 'pictures')

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

    def export_db(self, *args):
        if platform == 'android':
            from androidstorage4kivy import SharedStorage, ShareSheet
            from androidstorage4kivy.sharedstorage import MediaStoreDownloads
            from android.permissions import Permission, request_permissions

            ss = SharedStorage()
            zip_file = Path(ss.get_cache_dir(), f'export-{datetime.now().isoformat()}.zip')
            with ZipFile(zip_file, mode="w") as zf:
                zf.write(self.db_path)
                for picture in self.pictures_path.rglob('*.jpeg'):
                    zf.write(picture)
                print(", ".join(zf.namelist()))

            print(f"export complete: {zip_file} {zip_file.exists()}")
            shared_path = ss.copy_to_shared(zip_file.as_uri())
            print("before sharing")
            # request_permissions([Permission.WRITE_EXTERNAL_STORAGE])
            ShareSheet().share_file_list([shared_path])
            print("after sharing")

    def picture_for(self, target_id):
        return str(
            Path(
                self.user_data_dir,
                "pictures",
                target_id or ""
            ).with_suffix(".jpeg")
        )

    @mainthread
    def save_picture(self, camera, filename):
        rename(filename, self.picture_for(self.target_entry["id"]))
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
