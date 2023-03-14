#!/usr/bin/python
# vim: ts=4 number nowrap

print("alpha")

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
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.core.window import Window

import gi
gi.require_version('Gst', '1.0')
from xcamera.xcamera import XCamera
from zbarcam.zbarcam import ZBarCam

from db import get_engine, save_entry, get_entry, get_entries
import settings
from enc_dec import *

from urllib.parse import urlparse

# test features
THUMBNAILS = True
POSITION = True    # also uncomment references to ReadPositionButton in mtag.kv

msg_nogps = 'GPS not available'

if POSITION:
    try:
        from plyer import gps
    except ModuleNotFoundError:
        print(msg_nogps)
    else:
        print("plyer import OK")
    #from kivy.properties import StringProperty


resource_add_path("./xcamera/")

logging.basicConfig()
logger = logging.getLogger(__name__)


class EntryRow(F.ButtonBehavior, F.BoxLayout):
    id_str = F.StringProperty()
    id = F.ObjectProperty()

class TypeRow(F.ButtonBehavior, F.BoxLayout):
    otype = F.StringProperty()
    otype_bytes = F.ObjectProperty()


class TextFieldEditPopup(F.Popup):
    index = F.NumericProperty(allownone=True)
    rune = F.StringProperty()   # TODO not shown nor editable!
    key = F.ObjectProperty()
    value = F.ObjectProperty()

class TypeSelPopup(F.Popup):
    otypes = F.DictProperty()

class oType:
    def __init__(self, name, props = None):
        self.id = name
        if props is not None:
            self.props = props # dict with runes as keys
        else:
            print("TODO fetch data from database")


    def items(self):
        return  (
            ('key0', 'value0'),
            ('key1', 'value1'),
        )

    def get(self, x,y):
        #print(f"oType.get({x},{y})")
        return y
        #match x:
        #    case 'width':
        #        return 42
        #    case 'height':
        #        return 12
        #    case 'size':
        #        return [0,48]
        #    case 'pos_hint':
        #        return 0,0
        #    case 'size_hint':
        #        return 1,None
        #    case 'size_hint_min':
        #        return 1,None
        #    case 'size_hint_max':
        #        return 1,None
        #    case 'size_hint_x':
        #        return 1
        #    case 'size_hint_y':
        #        return None
        #    case 'size_hint_min_x':
        #        return 1
        #    case 'size_hint_min_y':
        #        return None
        #    case 'size_hint_max_x':
        #        return 1
        #    case 'size_hint_max_y':
        #        return None
import cv2
from pyzbar.pyzbar import decode, ZBarSymbol
def readQR( video_dev,_set = None ):
	'''
		画像キャプチャ
		VideoCaptureインスタンス生成
	'''
	cap = cv2.VideoCapture(video_dev, cv2.CAP_DSHOW)
	cap.open(video_dev)
	
	try:
		while cap.isOpened():
			ret, frame = cap.read()
		
			if ret:
				# デコード
				value = decode(frame, symbols=[ZBarSymbol.QRCODE])
		
				if value:
					for qrcode in value:
						if _set: _set[qrcode.data] = True
						else:
							try:
								cv2.destroyWindow('pyzbar')
							except cv2.error:
								#print("OOPS")
								pass
							else:
								x, y, w, h = qrcode.rect

								cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 3)
	
								qrimage_path = '/tmp/qrimage.png'
								is_written = cv2.imwrite(qrimage_path, frame)
								if not is_written:
									print('image was not saved!')
								return qrcode.data, qrimage_path
		
						# QRコード座標
						x, y, w, h = qrcode.rect

						# QRコードデータ
						#dec_inf = qrcode.data.decode('utf-8')
						#print('QR-decode:', dec_inf)
						#frame = cv2.putText(frame, dec_inf, (x, y-6), font, .3, (255, 0, 0), 1, cv2.LINE_AA)
		
						# バウンディングボックス
						cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 3)
		
				# 画像表示
				cv2.imshow('pyzbar', frame)


			# quit
			if cv2.waitKey(1) & 0xFF == ord('q'):
				break
	except KeyboardInterrupt:
		return 
	finally:
		# キャプチャリソースリリース
		cap.release()

#
# Kivy Application
#
class mTag(App):
    target_entry = F.DictProperty()
    entries = F.ListProperty()

    if POSITION:
        gps_location = F.StringProperty()
        gps_status = F.StringProperty('Click Start to get GPS location updates')

    #def build(self):
    #    lf='\n'
    #    print(f"{10*((10*'*')+lf)}")

    def __init__(self):
        super().__init__()
        self.db = get_engine(self.db_path)
        self.load_entries()
        self.pictures_path.mkdir(parents=True, exist_ok=True)
        self.thumbnails_path.mkdir(parents=True, exist_ok=True)
        self.gps_status = 'pre-init'

        Window.bind(on_keyboard=self.onBackBtn)

        print(f"__init__() done ; {self.user_data_dir = }")

    def onBackBtn(self, window, key, *args):
        """ To be called whenever user presses Back/Esc Key """
        # If user presses Back/Esc Key
        if key == 27:
            # Do whatever you need to do, like check if there are any
            # screens that you can go back to.
            if self.root.current == 'entries':
                pass
            elif self.root.current == 'editor':
                # TODO prompt to save!
                self.switch_screen("entries")
            else:
                print(self.root.current)
                #self.switch_screen("editor")

            # return True if you don't want to close app
            # return False if you do
            return True
        return False

    def request_android_permissions(self):
        """
        Since API 23, Android requires permission to be requested at runtime.
        This function requests permission and handles the response via a
        callback.
        The request will produce a popup if permissions have not already been
        been granted, otherwise it will do nothing.
        """
        from android.permissions import request_permissions, Permission

        def callback(permissions, results):
            """
            Defines the callback to be fired when runtime permission
            has been granted or denied. This is not strictly required,
            but added for the sake of completeness.
            """
            if all([res for res in results]):
                print("callback. All permissions granted.")
            else:
                print("callback. Some permissions refused.")

        request_permissions([Permission.ACCESS_COARSE_LOCATION,
                Permission.ACCESS_FINE_LOCATION], callback)
        # # To request permissions without a callback, do:
        # request_permissions([Permission.ACCESS_COARSE_LOCATION,
        #                      Permission.ACCESS_FINE_LOCATION])

    def GPSinit(self):
        print("trying GPS...")

        if platform == "android":
            try:
                gps.configure(on_location=self.on_location,
                              on_status=self.on_status)
            except (NotImplementedError, ModuleNotFoundError):
                import traceback
                traceback.print_exc()
                self.gps_status = msg_nogps
            else:
                print("gps.py: Android detected. Requesting permissions")
                self.request_android_permissions()
                return True
        else:
            self.gps_status = msg_nogps
            print(self.gps_status)

        return False


    def GPSstart(self, minTime, minDistance, widget = None):
        if ( self.gps_status == 'pre-init' and self.GPSinit() ) or \
             self.gps_status != msg_nogps:
            try:
                gps.start(minTime, minDistance)
            except NotImplementedError:
                self.gps_location = "NotImplementedError"
                widget.text = msg_nogps
        else:
                widget.state = "normal"
                widget.text = msg_nogps

    def GPSstop(self):
        try:
            gps.stop()
        except NotImplementedError:
            self.gps_location = "NotImplementedError"

    @mainthread
    def on_location(self, **kwargs):
        self.gps_location = '\n'.join([
            '{}={}'.format(k, v) for k, v in kwargs.items()])

    @mainthread
    def on_status(self, stype, status):
        self.gps_status = 'type={}\n{}'.format(stype, status)

    def on_pause(self):
        gps.stop()
        return True

    def on_resume(self):
        gps.start(1000, 1)  
        pass


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

    #def scan_id(self, get_uuid4=False):
    def scan_id(self,otype = None, get_uuid4=False):
        #if otype == None:
        #    p = F.TypeSelPopup()
        #    p.open()
            #if self.target_entry['otype'] == 'shelf':
            #    print("last item was a shelf.. what now?")
            #    self.switch_screen("entries")
            #    return
            #elif self.target_entry['otype'] == 'set':
            #    otype = 'box'
            #elif self.target_entry['otype'] == 'box':
            #    otype = 'part'
            #elif self.target_entry['otype'] == 'part':
            #    otype = 'part'


        if not get_uuid4:
            if platform == 'android':
                F.ZBarCamPopup().open()
            elif platform == 'linux':
                Clock.schedule_once(lambda *_: self.edit_entry( readQR( settings.video_dev )[0], otype), 2)
            else:
                print(f"unkown {platform = }")
        else:
            # temporary hack to simulate scanning a code
            # TODO allow webcam input or manual entry
            Clock.schedule_once(lambda *_: self.edit_entry(enc(str(uuid4())),otype), 2)
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
        if qrcontent.startswith(b'http'):
            parsed = urlparse(qrcontent)
            return f"{parsed.netloc}_{parsed.path.replace('/', '_')}_{parsed.params}_{parsed.query}"
        else:
            return dec( qrcontent.replace(b'/', b'_') )

    def export_db(self, *args, button):
        """ TODO this should not exist ; not in this form at least """
        print("TODO: request suffix/hint for filename")
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
        if target_id == '':
            return
        # workaround because can't use binary filename here
        try:
            target_id = self.sanitize(target_id)
        except AttributeError:
            pass

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

        if THUMBNAILS:
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
        else:
            return str(path)

    @mainthread
    def save_picture(self, camera, filename):
        #print(f"{filename = }")
        rename(filename, self.picture_for(self.target_entry["id"]))
        #print(f"{self.picture_for(self.target_entry['id']) = }")

        # thumbnail generation
        if THUMBNAILS:
            from PIL import Image
            im = Image.open(filename)
            im = im.resize(settings.thumbsize)
            im.save( str(filename).replace(settings.bindir,settings.thumbdir) )
            im.close()

        self.root.get_screen("editor").ids.picture.source = self.picture_for(self.target_entry["id"])
        self.root.get_screen("editor").ids.picture.reload()

    def snap_picture(self, force = True):
        ''' snaps a picture ; TODO may be used to open a zoomable image if picture already exists

            force: if True, don't open a zoomable image
        '''
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
                pic = Path(f'{settings.dummy_image_path}{choice([1,2,3])}.jpeg').read_bytes()
                #_path = self.pictures_path / self.sanitize(target_id)+'.jpeg'
                #print(f"{self.pictures_path=} / {dec(target_id)=} +'.jpeg'")
                #print(f"")
                Path(self.pictures_path / (self.sanitize(target_id)+'.jpeg')).write_bytes(pic)
                self.save_picture(None, self.pictures_path / (self.sanitize(target_id)+'.jpeg'))
            else:
                # open zoomable image popup
                F.ZoomImagePopup().open()

    def import_file(self):
        print("TODO open file chooser dialog")

    def edit_entry(self, entry_id, otype = None):
        self.target_entry = get_entry(self.db, entry_id)
        #target_entry = get_entry(self.db, entry_id)
        #print(f"{target_entry = }")
        #self.target_entry = target_entry
        #print("EDIT:",self.target_entry['id'])
        #print('DATA:',self.target_entry['text_fields'])

        if otype is None:
            for t in self.target_entry['text_fields']:
                if t['rune'] == 'Ingwaz' and t['key'] == settings.prefix: # TODO configurable in GUI
                    otype = t['value']
                    # TODO otype.append( t['value'] )
                    break
        #print("TYPE:",otype)
        self.target_entry['otype'] = otype

        #if otype == 'shelf':
        #    self.shelf_id = entry_id
        #elif otype == 'set':
        #    self.set_id = entry_id

        self.switch_screen("editor")

    def edit_text_field(self, index=None):
        data = self.target_entry["text_fields"][index] if index is not None else {}
        print(f"{self.target_entry = }")
        p = F.TextFieldEditPopup(
            title=dec(self.target_entry['id']),
            index=index,
            #key=data.get('key', ""),
            key=enc(data.get('key', "")),
            #value=data.get('value', ""),
            value=enc(data.get('value', "")),
        )
        p.open()

    def save_entry(self):
        # this saves everything again.. kept because of key+val pairs deletion
        otype = self.target_entry['otype']
        entry_id = self.target_entry['id']
        errors = []

        # making sure we have all the required values
        required_props = []
        if otype is not None:   # TODO otype must be a list!
            for prop in settings.presetkeys[otype]:
                print(f"{otype}: requesting property {prop[2]}")
                required_props.append(prop[2])
            for entry in self.target_entry['text_fields']:
                try:
                    required_props.remove(entry['key'])
                    print(f"found property '{entry['key']}'")
                except ValueError:
                    pass
        for prop in required_props:
            errors.append(f"ERROR: '{prop}' is not set when it should be")

        if otype == 'box':
            self.box_id = entry_id
            try:
                print('AUTO-ADD BOX',entry_id, '>>', self.shelf_id)
            except AttributeError:
                errors.append("ERROR: box is not on a shelf")
        elif otype == 'part':
            try: 
                print('AUTO-ADD BOX',entry_id, '>>', self.box_id)
            except AttributeError:
                errors.append("ERROR: part is not in a box")
            try: 
                print('AUTO-ADD SET',entry_id, '>>', self.set_id)
            except AttributeError:
                errors.append("ERROR: part is not in a set")

        if len(errors):
            content = BoxLayout(orientation='vertical')
            content.add_widget(Label(text='\n'.join(errors)))
            button = Button(text='Close')
            content.add_widget(button)
            popup = Popup(title='Errors detected', content=content, auto_dismiss=False)
            button.bind(on_press=popup.dismiss)
            popup.open()
        else:
            # TODO only add these if not already present! this add multiple entries when multiple identical key are allowed!
            if otype == 'shelf':
                print("Adding type 'shelf'")
                self.save_text_field( 'Ingwaz', None, 'ch.ju.sauser-frères', 'shelf' )
            elif otype == 'set':
                self.save_text_field( 'Ingwaz', None, 'ch.ju.sauser-frères', 'set' )
            elif otype == 'box':
                self.save_text_field( 'Ingwaz', None, 'ch.ju.sauser-frères', 'box' )
                self.save_text_field( 'Isaz', None, 'shelf', self.shelf_id )
            elif otype == 'part':
                self.save_text_field( 'Ingwaz', None, 'ch.ju.sauser-frères', 'part' )
                self.save_text_field( 'Isaz', None, 'box', self.box_id )
                self.save_text_field( 'Isaz', None, 'set', self.set_id )
            save_entry(self.db, self.target_entry)  # TODO why is this needed here? it's already called by save_text_field()
            self.switch_screen("entries")

    def save_text_field(self, rune=None, index=None, key="", value=""):
        data = {'rune': rune, 'key': enc(key), 'value': enc(value)}
        text_fields = self.target_entry["text_fields"][:]
        if index is not None:
            text_fields[index] = data
        else:
            text_fields.append(data)
        #print('TEXT_FIELDS',text_fields)

        self.target_entry["text_fields"] = text_fields
        # this saves all key/value pairs... TODO save only the one we just edited!
        save_entry(self.db, self.target_entry)

    def remove_text_field(self, index):
        text_fields = self.target_entry["text_fields"][:]
        text_fields.pop(index)
        self.target_entry["text_fields"] = text_fields

    def preset_value(self, field):
        # TODO open a popup with a list, populated from sqlite (with auto-add)
        otype = self.target_entry['otype']
        try:
            #i = settings.presetkeys[otype].index(field.text)
            i = 0
            for v in settings.presetkeys[otype]:
                if v[2] == field.text:
                    raise Exception("MatchFound")
                i += 1
            raise ValueError
        except ValueError:
            # not in list
            field.text = settings.presetkeys[otype][0][2]
        except KeyError:
            pass
        except Exception as e:
            if str(e) == "MatchFound":
                if i == len(settings.presetkeys[otype])-1:
                    field.text = settings.presetkeys[otype][0][2]
                else:
                    field.text = settings.presetkeys[otype][i+1][2]
            else:
                raise e

"""
    def get_location(self, method = 'network', button = None):
        '''
            method is one of:
            - gps (pure gps location, slow, energy consuming, but very accurate)
            - network (mix of gps and wifi/cell locating, faster, but less accurate)
            - passwive (like above but completely without using gps)

            Adapted from
                https://stackoverflow.com/questions/29797435/get-precise-android-gps-location-in-python

            OSM support (TODO): https://wiki.openstreetmap.org/wiki/Android
        '''
        if not POSITION:
            button.text = 'Not available :-/'
            return

        if platform == 'android':
            # import needed modules
            import android
            import time
            #import sys, select, os #for loop exit

            #notify me
            #self.droid.makeToast("fetching GPS data")
            if button is not None:
                button.text = "fetching position..."
            else:
                print( "fetching position..." )

            #print("start gps-sensor...")
            self.droid.startLocating()

            while True:
                #exit loop hook
                #if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
                #    line = input()
                #    print("exit endless loop...")
                #    break

                #wait for location-event
                event = self.droid.eventWaitFor('location',5000).result
                try :
                    if button is None:
                        print(' ; '.join([': '.join([k, repr(event['data'][method][k])]) for k in event['data'][method].keys()]))
                    else:
                        #timestamp = repr(event['data'][method]['time'])
                        longitude = repr(event['data'][method]['longitude'])
                        latitude = repr(event['data'][method]['latitude'])
                        altitude = repr(event['data'][method]['altitude'])
                        #speed = repr(event['data'][method]['speed'])
                        #accuracy = repr(event['data'][method]['accuracy'])
                        button.text = ' ; '.join([longitude, latitude, altitude])
                    break
                except KeyError:
                    if method not in ('gps','network','passive'):
                        if button is None:
                            print(f"Method '{method}' not supported")
                        else:
                            button.text = f"Error: {method}"
                        break
                    else:
                        continue
                else:
                    self.droid.eventClearBuffer()


                #time.sleep(5) #wait for 5 seconds

            print("stop gps-sensor...")
            self.droid.stopLocating()
        else:
            print("No location support on this platform")
"""

if __name__ == '__main__':
    mTag().run()
