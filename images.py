# Images - Show all media associated with the active person
#
# Copyright (C) 2021  Hans Boldt
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

"""
Module images.py

Gramplet to show all media associated with the active person

Exports:

class ImagesGramplet

"""

#-------------------#
# Python modules    #
#-------------------#
from html import escape
from math import log
from itertools import chain
import threading
import pdb

import warnings
warnings.simplefilter('always')

#-------------------#
# Gramps modules    #
#-------------------#
from gramps.gen.plug import Gramplet
#from gramps.gen.lib import Person, EventType
#from gramps.gen.display.name import displayer as name_displayer
#from gramps.gen.datehandler import get_date
#from gramps.gen.config import config
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.utils.file import media_path_full
from gramps.gui.widgets import Photo



#------------------#
# Gtk modules      #
#------------------#
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib, Gdk

#------------------#
# Translation      #
#------------------#
# try:
#     _trans = glocale.get_addon_translator(__file__)
#     _ = _trans.gettext
# except ValueError:
#     _ = glocale.translation.sgettext
# ngettext = glocale.translation.ngettext # else "nearby" comments are ignored


#-------------------#
#                   #
# Images class      #
#                   #
#-------------------#
class ImagesGramplet(Gramplet):
    """
    Images gramplet.
    """

    def init(self):
        """
        Gramplet initialization. Overrides method in class Gramplet.
        """
        self.gui.WIDGET = self.build_gui()
        self.gui.get_container_widget().remove(self.gui.textview)
        self.gui.get_container_widget().add(self.gui.WIDGET)
        self.image_list = list()


    def db_changed(self):
        """
        Overrides method in class Gramplet.

        Note: If an person, family, or event changes, any pedigree may change.
        """
        self.connect(self.dbstate.db, 'person-add', self.update)
        self.connect(self.dbstate.db, 'person-delete', self.update)
        self.connect(self.dbstate.db, 'person-update', self.update)
        self.connect(self.dbstate.db, 'event-add', self.update)
        self.connect(self.dbstate.db, 'event-delete', self.update)
        self.connect(self.dbstate.db, 'event-update', self.update)
        self.connect(self.dbstate.db, 'citation-add', self.update)
        self.connect(self.dbstate.db, 'citation-delete', self.update)
        self.connect(self.dbstate.db, 'citation-update', self.update)
        self.connect(self.dbstate.db, 'media-add', self.update)
        self.connect(self.dbstate.db, 'media-delete', self.update)
        self.connect(self.dbstate.db, 'media-update', self.update)


    def active_changed(self, handle):
        """
        Called when the active person is changed.

        Overrides method in class Gramplet.
        """
        self.update()


    def build_gui(self):
        """
        Build user interface.
        """
        self.content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.content_box.homogenous = False
        self.content_box.set_border_width(10)
        return self.content_box


    def add_image(self, media_handle):
        """
        Add one image from the media handle
        """
        media = self.dbstate.db.get_media_from_handle(media_handle)
        image = ImageBox(self.dbstate.db, self.uistate, media)
        self.content_box.pack_start(image, False, False, 5)
        self.image_list.append(image)


    def clear_images(self):
        """
        Remove all images from the Gramplet.
        """
        for image in self.image_list:
            self.content_box.remove(image)
        self.image_list = []


    def process_media(self, obj_type, obj, media_list):
        """
        Loop through items of media list
        """
        for media_ref in media_list:
            media_handle = media_ref.get_reference_handle()
            if not media_handle in self.all_media:
                media = self.dbstate.db.get_media_from_handle(media_handle)
                self.all_media[media_handle] = media.get_description()


    def main(self): # return false finishes
        """
        Generator which will be run in the background.

        Overrides method in class Gramplet.
        """
        self.clear_images()

        active_handle = self.get_active('Person')
        if not active_handle:
            return

        active = self.dbstate.db.get_person_from_handle(active_handle)
        self.all_media = dict()

        # Get all media for person
        self.process_media('person', active, active.get_media_list())

        # Get all media for citations
        for event_ref in active.get_event_ref_list():
            event_handle = event_ref.get_reference_handle()
            event = self.dbstate.db.get_event_from_handle(event_handle)
            for cit_handle in event.get_citation_list():
                cit = self.dbstate.db.get_citation_from_handle(cit_handle)
                self.process_media('citation', cit, cit.get_media_list())

        # Display all media
        media_list = list(self.all_media.items())
        media_list.sort(key=lambda x: x[1])
        for (media_handle, med_desc) in media_list:
            self.add_image(media_handle)

        self.content_box.show_all()


class ImageBox(Gtk.Box):
    """
    Graphic for one image on the screen.
    """

    def __init__(self, db, uistate, media):
        """
        """
        super().__init__(orientation=Gtk.Orientation.VERTICAL)

        full_path = media_path_full(db, media.get_path())
        mime_type = media.get_mime_type()

        desc = media.get_description()

        photo = Photo(True)
        photo.set_image(full_path, mime_type)
        photo.set_uistate(uistate, media.get_handle())
        photo.set_halign(Gtk.Align.START)
        self.pack_start(photo, False, False, 5)

        desc_label = Gtk.Label(label=desc)
        desc_label.set_halign(Gtk.Align.START)
        desc_label.set_justify(Gtk.Justification.LEFT)
        self.pack_start(desc_label, False, False, 5)

        self.show_all()
