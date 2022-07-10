#!/usr/bin/python
# vim: ts=4 number nowrap
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
import settings

from urllib.parse import urlparse

THUMBNAILS = True

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
class mTag(App):
    target_entry = F.DictProperty()
    entries = F.ListProperty()

    def __init__(self):
        super().__init__()
        self.db = get_engine(self.db_path)
        self.load_entries()
        self.pictures_path.mkdir(parents=True, exist_ok=True)
        if THUMBNAILS:
            #Path(self.user_data_dir, settings.thumbdir).mkdir(parents=True, exist_ok=True)
            self.thumbnails_path.mkdir(parents=True, exist_ok=True)

    @property
    def db_path(self) -> Path:
        return Path(self.user_data_dir, settings.sqldb)
 
    @property
    def pictures_path(self) -> Path:
        return Path(self.user_data_dir, settings.bindir)

    @property
    def thumbnails_path(self) -> Path:
        return Path(self.user_data_dir, settings.thumbdir)

    def load_entries(self):
        self.entries = get_entries(self.db)

    def switch_screen(self, target):
        self.root.current = target

    def scan_id(self):
        if platform == 'android':
            F.ZBarCamPopup().open()
        else:
            # temporary hack to simulate scanning a code
            # TODO allow webcam input or manual entry
            id = str(uuid4())
            #id = self.sanitize('https://en.gren.ag/e?'+str(uuid4()))
            Clock.schedule_once(lambda *_: self.edit_entry(id), 2)

    def scan_input(self, field):
        """ TODO set text input field to content of next QR code (open popup) ; set focus to next input field """

    @staticmethod
    def sanitize(image_name):
        for u in settings.strprefix:
            image_name = image_name.lstrip(u)
        #print('###',image_name)
        if image_name.startswith('http'):
            parsed = urlparse(image_name)
            #print( f">>> {parsed.netloc}_{parsed.path.replace('/', '_')}_{parsed.params}_{parsed.query}" )
            return f"{parsed.netloc}_{parsed.path.replace('/', '_')}_{parsed.params}_{parsed.query}"
        else:
        #    print('%%%',image_name.replace('/', '_'))
            return image_name.replace('/', '_')

    def export_db(self, *args, button):
        """ TODO this should not exist ; not in this form at least """
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
                #print(", ".join(zf.namelist()))

            print(f"export complete: {zip_file} {zip_file.exists()}")
            shared_path = ss.copy_to_shared(zip_file.as_uri())
            #print("before sharing")
            # request_permissions([Permission.WRITE_EXTERNAL_STORAGE])
            ShareSheet().share_file_list([shared_path])
            #print("after sharing")
            button.text = str(zip_file)
            button.background_color = (0,1,0)
        else:
            print("Error: platform support uncomplete")
            button.background_color = (.2,.2,.2)


    def picture_for(self, target_id, thumbnail = False):
        #print('TARGET',target_id)
        if THUMBNAILS and thumbnail:
            path = Path(
                self.user_data_dir,
                settings.thumbdir,
                target_id or '_'
            ).with_suffix(".jpeg")
        else:
            path = Path(
                self.user_data_dir,
                settings.bindir,
                target_id or '_'
            ).with_suffix(".jpeg")

        if path.exists():
            return str(path)
        else:
            # TODO this file doesn't exist by default... manual copy needed at this stage ; ideally it's compiled in-app
            return str(
                Path(
                    self.user_data_dir,
                    settings.thumbdir,
                    '_'
                ).with_suffix(".jpeg")
            )

    @mainthread
    def save_picture(self, camera, filename):
        rename(filename, self.picture_for(self.target_entry["id"]))

        if THUMBNAILS:
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
        else:
            print("Error: platform supported for photo not implemented")
        # TODO allow other platforms ; ie for linux
        # https://github.com/ValentinDumas/KivyCam

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
    mTag().run()
