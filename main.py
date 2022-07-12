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

#gi.require_version('Gst', '1.0')   TODO should be done inside XCamera, so as to avoid warning
from xcamera.xcamera import XCamera
from zbarcam.zbarcam import ZBarCam

from db import get_engine, save_entry, get_entry, get_entries
import settings

from urllib.parse import urlparse

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
        if target == 'entries':
            self.load_entries()
        self.root.current = target

    def scan_id(self):
        if platform == 'android':
            F.ZBarCamPopup().open()
        else:
            # temporary hack to simulate scanning a code
            # TODO allow webcam input or manual entry
            id = str(uuid4())
            Clock.schedule_once(lambda *_: self.edit_entry(id), 2)
        #print('EDITED:',self.target_entry['id'], '(previous value ; this is WRONG!)') # TODO this is the _previous_ id!
        #self.target_entry = get_entry(self.db, entry_id)

    @property
    def value(self):
        return None

    @value.setter
    def value(self, value):
        #self._value = value
        self.qr_content_to.text = value

    def scan_value(self, inputfield):
        self.qr_content_to = inputfield
        if platform == 'android':
            F.ZBarCamValuePopup().open()
        else:
            # temporary hack to simulate scanning a code
            # TODO allow webcam input
            id = str(uuid4())
            self.value = id

    def scan_input(self, field):
        """ TODO set text input field to content of next QR code (open popup) ; set focus to next input field """

    def delete_entry(self):
        print(self.target_entry)

    @staticmethod
    def sanitize(qrcontent):
        for u in settings.strprefix:
            qrcontent = qrcontent.lstrip(u)
        if qrcontent.startswith('http'):
            parsed = urlparse(qrcontent)
            return f"{parsed.netloc}_{parsed.path.replace('/', '_')}_{parsed.params}_{parsed.query}"
        else:
            return qrcontent.replace('/', '_')

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
                    Path(picture).unlink()

            print(f"export complete: {zip_file} {zip_file.exists()}")
            shared_path = ss.copy_to_shared(str(zip_file))
            ShareSheet().share_file(shared_path)

            Path(self.db_path).unlink()
            self.db = get_engine(self.db_path)
        else:
            print("Error: platform support uncomplete")
            print(self.db_path)
            print(self.pictures_path)
            zip_file = Path('/tmp', f'export-{datetime.now().isoformat()}.zip')
            with ZipFile(zip_file, mode="w") as zf:
                zf.write(self.db_path)
                for picture in self.pictures_path.rglob('*.jpeg'):
                    zf.write(picture)
                    Path(picture).unlink()
            Path(self.db_path).unlink()
            self.db = get_engine(self.db_path)
            button.background_color = (.2,.2,.2)
        self.load_entries()

    def call_app(self, button):
        print("Not implemented : call_app()")

    def choose_file(self, button):
        if platform == 'android':
            from androidstorage4kivy import Chooser
            file_sel = Chooser()
        else:
            print("File chooser not implemented on this platform")

    def picture_for(self, target_id, thumbnail = False):
        #print('PICTURE TARGET',target_id, thumbnail)
        if thumbnail:
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

        # thumbnail generation
        from PIL import Image
        im = Image.open(filename)
        im = im.resize(settings.thumbsize)
        im.save( str(filename).replace(settings.bindir,settings.thumbdir) )
        im.close()

        self.root.get_screen("editor").ids.picture.source = self.picture_for(self.target_entry["id"])
        self.root.get_screen("editor").ids.picture.reload()

    def snap_picture(self, force = True):
        ''' snaps a picture ; TODO may be used to open a zoomable image if picture already exists '''
        target_id = self.target_entry["id"]
        #print('OOPS?',target_id, 'this seems correct')
        if platform == 'android':
            if force:
                # take new photo
                F.XCameraPopup().open()
            else:
                # open zoomable image popup
                F.ZoomImagePopup().open()
        else:
            if force:
                # TODO allow other platforms ; ie for linux
                # https://github.com/ValentinDumas/KivyCam
                print("Error: platform support not implemented for photo")
                #print("Error: platform support not implemented for photo ; debugging only")
                from random import choice
                pic = Path(f'/home/meta/naspi/metameta/mtag/{choice([1,2,3])}.jpeg').read_bytes()
                Path(self.pictures_path / (target_id+'.jpeg')).write_bytes(pic)
                self.save_picture(None, self.pictures_path / (target_id+'.jpeg'))
            else:
                # open zoomable image popup
                F.ZoomImagePopup().open()

    def edit_entry(self, entry_id):
        self.target_entry = get_entry(self.db, entry_id)
        print("EDIT:",self.target_entry['id'])
        self.switch_screen("editor")

    def edit_text_field(self, index=None):
        data = self.target_entry["text_fields"][index] if index is not None else {}
        p = F.TextFieldEditPopup(
            index=index,
            key=data.get("key", ""),
            value=data.get("value", ""),
        )
        p.open()

    def save_entry(self):
        # this saves everything again.. kept because of key+val pairs deletion
        save_entry(self.db, self.target_entry)
        self.switch_screen("entries")

    def save_text_field(self, index=None, key="", value=""):
        data = {"key": key, "value": value}
        text_fields = self.target_entry["text_fields"][:]
        if index is not None:
            text_fields[index] = data
        else:
            text_fields.append(data)

        self.target_entry["text_fields"] = text_fields
        # this saves all key/value pairs... TODO save only the one we just edited!
        save_entry(self.db, self.target_entry)

    def remove_text_field(self, index):
        text_fields = self.target_entry["text_fields"][:]
        text_fields.pop(index)
        self.target_entry["text_fields"] = text_fields

    def preset_value(self, field):
        # TODO open a popup with a list, populated from sqlite (with auto-add)
        try:
            i = settings.presetkeys.index(field.text)
            if i == len(settings.presetkeys)-1:
                field.text = settings.presetkeys[0]
            else:
                field.text = settings.presetkeys[i+1]
        except ValueError:
            # not in list
            field.text = settings.presetkeys[0]

if __name__ == '__main__':
    mTag().run()
