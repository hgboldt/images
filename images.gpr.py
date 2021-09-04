# File: images.gpr.py
register(GRAMPLET,
         id="Images",
         name=_("Images"),
         description = _("Gramplet showing all media for active person"),
         version="0.0.0",
         gramps_target_version="5.1",
         status = STABLE,
         fname="images.py",
         height = 50,
         detached_width = 400,
         detached_height = 500,
         gramplet = 'ImagesGramplet',
         gramplet_title=_("Images"),
         help_url="5.1_Addons#Addon_List",
         navtypes=['Person']
         )
