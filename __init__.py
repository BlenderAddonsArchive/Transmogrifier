# BEGIN GPL LICENSE BLOCK #####
#
# This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

# You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>. 
#
# END GPL LICENSE BLOCK #####


import bpy
from bpy.types import AddonPreferences, PropertyGroup, Operator, Panel
from bpy.props import BoolProperty, IntProperty, EnumProperty, StringProperty, PointerProperty, FloatVectorProperty, FloatProperty
import os
import shutil
from pathlib import Path
import re
import json
import subprocess

bl_info = {
    "name": "Transmogrifier",
    "author": "Sapwood Studio",
    "version": (1, 4, 0),
    "blender": (3, 6),
    "category": "Import-Export",
    "location": "Set in preferences below. Default: Top Bar (After File, Edit, ...Help)",
    "description": "Batch converts 3D files and associated textures into other formats.",
    "doc_url": "github.com/SapwoodStudio/Transmogrifier",
    "tracker_url": "github.com/sapwoodstudio/Transmogrifier/issues",
}

# A Dictionary of operator_name: [list of preset EnumProperty item tuples].
# Blender's doc warns that not keeping reference to enum props array can
# cause crashs and weird issues.
# Also useful for the get_preset_index function.
preset_enum_items_refs = {}

# Returns a list of tuples used for an EnumProperty's items (identifier, name, description)
# identifier, and name are the file name of the preset without the file extension (.py)
def get_operator_presets(operator):
    presets = [('NO_PRESET', "(no preset)", "", 0)]
    for d in bpy.utils.script_paths(subdir="presets/operator/" + operator):
        for f in Path(d).iterdir():
            if f.suffix != ".py":
                continue
            f = Path(f).stem
            presets.append((f, f, ""))
    # Blender's doc warns that not keeping reference to enum props array can
    # cause crashs and weird issues:
    preset_enum_items_refs[operator] = presets
    return presets

# Returns a dictionary of options from an operator's preset.
# When calling an operator's method, you can use ** before a dictionary
# in the method's arguments to set the arguments from that dictionary's
# key: value pairs. Example:
# bpy.ops.category.operator(**options)
def load_operator_preset(operator, preset):
    options = {}
    if preset == 'NO_PRESET':
        return options

    for d in bpy.utils.script_paths(subdir="presets/operator/" + operator):
        fp = "".join([d, "/", preset, ".py"])
        if Path(fp).is_file():  # Found the preset file
            print("Using preset " + fp)
            file = open(fp, 'r')
            for line in file.readlines():
                # This assumes formatting of these files remains exactly the same
                if line.startswith("op."):
                    line = line.removeprefix("op.")
                    split = line.split(" = ")
                    key = split[0]
                    value = split[1]
                    options[key] = eval(value)
            file.close()
            return options
    # If it didn't find the preset, use empty options
    # (the preset option should look blank if the file doesn't exist anyway)
    return options

# Finds the index of a preset with preset_name and returns it
# Useful for transferring the value of a saved preset (in a StringProperty)
# to the NOT saved EnumProperty for that preset used to present a nice GUI.
def get_preset_index(operator, preset_name):
    for p in range(len(preset_enum_items_refs[operator])):
        if preset_enum_items_refs[operator][p][0] == preset_name:
            return p
    return 0



# A Dictionary of operator_name: [list of preset EnumProperty item tuples].
# Blender's doc warns that not keeping reference to enum props array can
# cause crashs and weird issues.
# Also useful for the get_preset_index function.
transmogrifier_preset_enum_items_refs = {}

# Returns a list of tuples used for an EnumProperty's items (identifier, name, description)
# identifier, and name are the file name of the preset without the file extension (.json)
def get_transmogrifier_presets(operator):
    presets = [('NO_PRESET', "(no preset)", "", 0)]
    for d in bpy.utils.script_paths(subdir="presets/operator/" + operator):
        for f in Path(d).iterdir():
            if f.suffix != ".json":
                continue
            f = Path(f).stem
            presets.append((f, f, ""))
    # Blender's doc warns that not keeping reference to enum props array can
    # cause crashs and weird issues:
    transmogrifier_preset_enum_items_refs[operator] = presets
    return presets

# Returns a dictionary of options from an operator's preset.
# When calling an operator's method, you can use ** before a dictionary
# in the method's arguments to set the arguments from that dictionary's
# key: value pairs. Example:
# bpy.ops.category.operator(**options)
def load_transmogrifier_preset(operator, preset):
    json_dict = {}
    if preset == 'NO_PRESET':
        return json_dict

    for d in bpy.utils.script_paths(subdir="presets/operator/" + operator):
        fp = "".join([d, "/", preset, ".json"])
        if Path(fp).is_file():  # Found the preset file
            print("Using preset " + fp)
            
            # Open JSON file
            with open(fp, 'r') as openfile:
            
                # Read from JSON file
                json_dict = json.load(openfile)
            
            return json_dict
            
    # If it didn't find the preset, use empty options
    # (the preset option should look blank if the file doesn't exist anyway)
    return json_dict

# Finds the index of a preset with preset_name and returns it
# Useful for transferring the value of a saved preset (in a StringProperty)
# to the NOT saved EnumProperty for that preset used to present a nice GUI.
def get_transmogrifier_preset_index(operator, preset_name):
    for p in range(len(transmogrifier_preset_enum_items_refs[operator])):
        if transmogrifier_preset_enum_items_refs[operator][p][0] == preset_name:
            return p
    return 0



# A dictionary of one key with a value of a list of asset libraries.
asset_library_enum_items_refs = {"asset_libraries": []}

# Get asset libraries and return a list of them.  Add them as the value to the dictionary.
def get_asset_libraries():
    libraries_list = [('NO_LIBRARY', "(no library)", "Don't move .blend files containing assets to a library.\nInstead, save .blend files adjacent converted items.", 0)]
    asset_libraries = bpy.context.preferences.filepaths.asset_libraries
    for asset_library in asset_libraries:
        library_name = asset_library.name
        libraries_list.append((library_name, library_name, ""))

    asset_library_enum_items_refs["asset_libraries"] = libraries_list

    return libraries_list

# Get index of selected asset library in asset_library_enum property based on its position in the dictionary value list.
def get_asset_library_index(library_name):
    for l in range(len(asset_library_enum_items_refs["asset_libraries"])):
        if asset_library_enum_items_refs["asset_libraries"][l][0] == library_name:
            return l
    return 0



# A dictionary of one key with a value of a list of asset catalogs.
asset_catalog_enum_items_refs = {"asset_catalogs": []}

# Get asset catalogs and return a list of them.  Add them as the value to the dictionary.
def get_asset_catalogs():
    catalogs_list = [('NO_CATALOG', "(no catalog)", "Don't assign assets to a catalog.", 0)]
    settings = bpy.context.scene.transmogrifier
    asset_libraries = bpy.context.preferences.filepaths.asset_libraries
    library_name = settings.asset_library
    library_path = [library.path for library in asset_libraries if library.name == library_name]
    if library_path:  # If the list is not empty, then it found a library path.
        library_path = Path(library_path[0])
        catalog_file = library_path / "blender_assets.cats.txt"
        if catalog_file.is_file():  # Check if catalog file exists
            with catalog_file.open() as f:
                for line in f.readlines():
                    if line.startswith(("#", "VERSION", "\n")):
                        continue
                    # Each line contains : 'uuid:catalog_tree:catalog_name' + eol ('\n')
                    uuid = line.split(":")[0]
                    catalog_name = line.split(":")[2].split("\n")[0]
                    catalogs_list.append((uuid, catalog_name, ""))

    asset_catalog_enum_items_refs["asset_catalogs"] = catalogs_list

    return catalogs_list

# Get index of selected asset catalog in asset_catalog_enum property based on its position in the dictionary value list.
def get_asset_catalog_index(catalog_name):
    for l in range(len(asset_catalog_enum_items_refs["asset_catalogs"])):
        if asset_catalog_enum_items_refs["asset_catalogs"][l][0] == catalog_name:
            return l
    return 0




# Refresh UI when a Transmogrifier preset is selected by running REFRESHUI operator.
def refresh_ui(self, context):
    eval('bpy.ops.refreshui.transmogrifier()')

# Draws the .blend file specific settings used in the
# Popover panel or Side Panel panel
def draw_settings_general(self, context):
    settings = context.scene.transmogrifier
    self.layout.use_property_split = True
    self.layout.use_property_decorate = False

    # Display combination of title and version from bl_info.
    version = ''
    for num in bl_info["version"]:
        version = version + "." + str(num)
    version = version.lstrip(".")
    title = bl_info["name"] + " " + version
    self.layout.label(text = title)

    # Batch Convert button
    # self.layout.operator('transmogrifier.transmogrify', icon='FILE_CACHE')
    row = self.layout.row()
    row = row.row(align=True)
    row.operator('transmogrifier.transmogrify', text='Batch Convert', icon='FILE_CACHE')
    row.scale_y = 1.5

    # UI settings
    # self.layout.separator()
    col = self.layout.column(align=True)
    col.label(text="User Interface:", icon='WORKSPACE')
    self.layout.use_property_split = False
    grid = self.layout.grid_flow(columns=2, align=True)
    grid.prop(settings, 'ui_toggle', expand=True)

    # Transmogrifier Presets Menu
    # self.layout.separator()
    col = self.layout.column(align=True)
    col.label(text="Workflow:", icon='DRIVER')
    layout = self.layout
    # Align menu items to the left.
    self.layout.use_property_split = False
    row = layout.row(align=True)
    row.prop(settings, 'transmogrifier_preset_enum')
    row.operator("transmogrifierpreset.add", text="", icon="ADD")
    row.operator("transmogrifierpreset.remove", text="", icon="REMOVE")

    # Import Settings
    self.layout.use_property_split = True
    # self.layout.separator()
    col = self.layout.column(align=True)
    col.label(text="Import:", icon='IMPORT')
    # Directory input
    col.prop(settings, 'directory')
    col.prop(settings, 'import_file')
    # self.layout.separator()
    # col = self.layout.column()

    # col.label(text=settings.import_file + " Settings:")
    if settings.import_file == 'DAE':
        col.prop(settings, 'import_dae_preset_enum')
    elif settings.import_file == 'ABC':
        col.prop(settings, 'import_abc_preset_enum')
    elif settings.import_file == 'USD':
        col.prop(settings, 'import_usd_extension')
        col.prop(settings, 'import_usd_preset_enum')
    elif settings.import_file == 'OBJ':
        col.prop(settings, 'import_obj_preset_enum')
    elif settings.import_file == 'PLY':
        col.prop(settings, 'import_ply_ascii')
    elif settings.import_file == 'STL':
        col.prop(settings, 'import_stl_ascii')
    elif settings.import_file == 'FBX':
        col.prop(settings, 'import_fbx_preset_enum')
    elif settings.import_file == 'glTF':
        col.prop(settings, 'import_gltf_extension')
    elif settings.import_file == 'X3D':
        col.prop(settings, 'import_x3d_preset_enum')



    # Export Settings
    # self.layout.separator()
    # self.layout.separator()
    col = self.layout.column(align=True)
    col.label(text="Export:", icon='EXPORT')
    
    # col.label(text="Models:", icon='OUTLINER_OB_MESH')
    col.prop(settings, "directory_output_location")
    if settings.ui_toggle == "Advanced":
        if settings.directory_output_location == "Custom":
            col.prop(settings, "directory_output_custom")
            if settings.directory_output_custom:
                col.prop(settings, "use_subdirectories")
                if settings.use_subdirectories:
                    col.prop(settings, "copy_item_dir_contents")
            col = self.layout.column(align=True)
    
    # Quantity
    if settings.ui_toggle == "Advanced":
        col.prop(settings, "model_quantity")

    # Align menu items to the right.
    self.layout.use_property_split = True
    col = self.layout.column(align=True)

    # File Format 1
    col = self.layout.column(align=True)
    if settings.model_quantity != "No Formats":
        # col.label(text="Format 1:", icon='OUTLINER_OB_MESH')
        col.prop(settings, 'export_file_1')

        if settings.export_file_1 == 'DAE':
            col.prop(settings, 'dae_preset_enum')
        elif settings.export_file_1 == 'ABC':
            col.prop(settings, 'abc_preset_enum')
        elif settings.export_file_1 == 'USD':
            col.prop(settings, 'usd_extension')
            col.prop(settings, 'usd_preset_enum')
        elif settings.export_file_1 == 'OBJ':
            col.prop(settings, 'obj_preset_enum')
        elif settings.export_file_1 == 'PLY':
            col.prop(settings, 'ply_ascii')
        elif settings.export_file_1 == 'STL':
            col.prop(settings, 'stl_ascii')
        elif settings.export_file_1 == 'FBX':
            col.prop(settings, 'fbx_preset_enum')
        elif settings.export_file_1 == 'glTF':
            col.prop(settings, 'gltf_preset_enum')
        elif settings.export_file_1 == 'X3D':
            col.prop(settings, 'x3d_preset_enum')
        elif settings.export_file_1 == "BLEND":
            col.prop(settings, 'pack_resources')
            if not settings.pack_resources:
                col.prop(settings, 'make_paths_relative')
        
        # Set scale
        if settings.ui_toggle == "Advanced":
            # col = self.layout.column(align=True)
            col.prop(settings, 'export_file_1_scale')
            # self.layout.separator()

        # File Format 2
        if settings.model_quantity == "2 Formats":
            col = self.layout.column(align=True)
            col = self.layout.column(align=True)
            col.prop(settings, 'export_file_2')

            if settings.export_file_2 == 'DAE':
                col.prop(settings, 'dae_preset_enum')
            elif settings.export_file_2 == 'ABC':
                col.prop(settings, 'abc_preset_enum')
            elif settings.export_file_2 == 'USD':
                col.prop(settings, 'usd_extension')
                col.prop(settings, 'usd_preset_enum')
            elif settings.export_file_2 == 'OBJ':
                col.prop(settings, 'obj_preset_enum')
            elif settings.export_file_2 == 'PLY':
                col.prop(settings, 'ply_ascii')
            elif settings.export_file_2 == 'STL':
                col.prop(settings, 'stl_ascii')
            elif settings.export_file_2 == 'FBX':
                col.prop(settings, 'fbx_preset_enum')
            elif settings.export_file_2 == 'glTF':
                col.prop(settings, 'gltf_preset_enum')
            elif settings.export_file_2 == 'X3D':
                col.prop(settings, 'x3d_preset_enum')
            elif settings.export_file_2 == "BLEND":
                col.prop(settings, 'pack_resources')
                if not settings.pack_resources:
                    col.prop(settings, 'make_paths_relative')
            
            # Set scale
            if settings.ui_toggle == "Advanced":
                # col = self.layout.column(align=True)
                col.prop(settings, 'export_file_2_scale')


        col = self.layout.column(align=True)

    # Name Settings
    col.label(text="Names:", icon='SORTALPHA')
    col.prop(settings, 'prefix')
    col.prop(settings, 'suffix')
    if settings.ui_toggle == "Advanced":
        col = self.layout.column(align=True)
        col.prop(settings, 'set_data_names')


# Texture Settings
def draw_settings_textures(self, context):
    settings = context.scene.transmogrifier
    self.layout.use_property_split = True
    self.layout.use_property_decorate = False
    col = self.layout.column(align=True)
    # Align menu items to the left.
    self.layout.use_property_split = True
    # col = self.layout.column(align=True)
    col.label(text="Textures:", icon='TEXTURE')
    col.prop(settings, 'use_textures')

    if settings.use_textures:
        if settings.ui_toggle == "Advanced":
            col.prop(settings, 'regex_textures')
            col.prop(settings, 'keep_modified_textures')
            self.layout.use_property_split = True
            col = self.layout.column(align=True)
        col.prop(settings, 'textures_source')
        if settings.ui_toggle == "Advanced":
            if settings.import_file == "BLEND" and settings.textures_source == "External":
                col.prop(settings, 'use_linked_blend_textures')
                col = self.layout.column(align=True)
            if settings.textures_source == "Custom":
                col.prop(settings, 'textures_custom_dir')
                col.prop(settings, 'copy_textures_custom_dir')
                if settings.copy_textures_custom_dir:
                    col.prop(settings, 'replace_textures')
        
        if settings.ui_toggle == "Advanced":
            # col = self.layout.column(align=True)
            col.prop(settings, 'texture_resolution')

            if settings.texture_resolution != "Default":
                # Align menu items to the left.
                self.layout.use_property_split = False

                grid = self.layout.grid_flow(columns=3, align=True)
                grid.prop(settings, 'texture_resolution_include')
            
                # Align menu items to the right.
                self.layout.use_property_split = True
                col = self.layout.column(align=True)

            col.prop(settings, 'image_format')
            lossy_compression_support = ("JPEG", "WEBP")
            if settings.image_format != "Default":
                if settings.image_format in lossy_compression_support:
                    col.prop(settings, 'image_quality')
                # Align menu items to the left.
                self.layout.use_property_split = False

                grid = self.layout.grid_flow(columns=3, align=True)
                grid.prop(settings, 'image_format_include')
        
    if settings.ui_toggle == "Advanced":
        self.layout.use_property_split = True
        col = self.layout.column(align=True)
        col.label(text="UVs:", icon='UV')
        col.prop(settings, 'rename_uvs')
        if settings.rename_uvs:
            col.prop(settings, 'rename_uvs_name')
            col = self.layout.column(align=True)
        col.prop(settings, 'export_uv_layout')
        if settings.export_uv_layout:
            col.prop(settings, 'modified_uvs')
            col = self.layout.column(align=True)
            col.prop(settings, 'uv_export_location')
            if settings.uv_export_location == "Custom":
                col.prop(settings, 'uv_directory_custom')
            col.prop(settings, 'uv_combination')
            col.prop(settings, 'uv_resolution')
            col.prop(settings, 'uv_format')
            if settings.uv_format in lossy_compression_support:
                col.prop(settings, 'uv_image_quality')  # Only show this option for formats that support lossy compression (i.e. JPEG & WEBP).
            col.prop(settings, 'uv_fill_opacity')
            # self.layout.separator()
            

def draw_settings_transforms(self, context):
    settings = context.scene.transmogrifier
    self.layout.use_property_split = True
    self.layout.use_property_decorate = False
    col = self.layout.column(align=True)

    # Transformation options.
    self.layout.use_property_split = True
    # col = self.layout.column(align=True)
    if settings.ui_toggle == "Advanced":
        col.label(text="Transformations:", icon='CON_PIVOT')
        col.prop(settings, 'set_transforms')
        if settings.set_transforms:
            self.layout.use_property_split = False
            grid = self.layout.grid_flow(columns=3, align=True)
            grid.prop(settings, 'set_transforms_filter')
            col = self.layout.column(align=True)
            
            if 'Location' in settings.set_transforms_filter:
                col.prop(settings, 'set_location')
            if 'Rotation' in settings.set_transforms_filter:
                col.prop(settings, 'set_rotation')
            if 'Scale' in settings.set_transforms_filter:
                col.prop(settings, 'set_scale')
    
            self.layout.use_property_split = True
            col = self.layout.column(align=True)

        col.prop(settings, 'apply_transforms')
        if settings.apply_transforms:
            self.layout.use_property_split = False
            grid = self.layout.grid_flow(columns=3, align=True)
            grid.prop(settings, 'apply_transforms_filter')
            # col = self.layout.column(align=True)
        # col = self.layout.column(align=True)

        # Set animation options.
        self.layout.use_property_split = True
        col = self.layout.column(align=True)
        col.label(text="Animations:", icon='ANIM')
        col.prop(settings, 'delete_animations')

    # Set scene unit options.
    # self.layout.use_property_split = True
    # col = self.layout.column(align=True)
    col.label(text="Scene:", icon='SCENE_DATA')
    col.prop(settings, 'unit_system')
    if settings.unit_system == "METRIC":
        col.prop(settings, 'length_unit_metric')
    elif settings.unit_system == "IMPERIAL":
        col.prop(settings, 'length_unit_imperial')

    # self.layout.separator()
    
# Set max file size options.
def draw_settings_optimize_files(self, context):
    settings = context.scene.transmogrifier
    self.layout.use_property_split = True
    self.layout.use_property_decorate = False
    col = self.layout.column(align=True)

    # self.layout.use_property_split = True
    # col = self.layout.column(align=True)
    col.label(text="Auto-Optimize:", icon='TRIA_DOWN_BAR')
    col.prop(settings, 'auto_resize_files')
    self.layout.use_property_split = True
    if settings.ui_toggle == "Advanced":
        if settings.auto_resize_files != "None":
            col.prop(settings, 'file_size_maximum')
            grid = self.layout.grid_flow(columns=1, align=True)
            grid.prop(settings, 'file_size_methods')
            col = self.layout.column(align=True)
            if 'Resize Textures' in settings.file_size_methods:
                col.prop(settings, 'resize_textures_limit')
            if 'Reformat Textures' in settings.file_size_methods:
                col.prop(settings, 'reformat_normal_maps')
            if 'Decimate Meshes' in settings.file_size_methods:
                col.prop(settings, 'decimate_limit')
                

# Archive options
def draw_settings_archive(self, context):
    settings = context.scene.transmogrifier
    self.layout.use_property_split = True
    self.layout.use_property_decorate = False
    col = self.layout.column(align=True)

    # Align menu items to the Right.
    self.layout.use_property_split = True
    col.label(text="Archive:", icon='ASSET_MANAGER')
    col.prop(settings, 'save_conversion_log')
    col.prop(settings, 'archive_assets')

    if settings.ui_toggle == "Advanced":
        if settings.archive_assets:
            self.layout.use_property_split = False
            col.label(text="Mark Assets:")
            grid = self.layout.grid_flow(columns=6, align=True)
            grid.prop(settings, 'asset_types_to_mark')
            col = self.layout.column(align=True)
            
            col.prop(settings, 'assets_ignore_duplicates')
            if settings.assets_ignore_duplicates:
                grid = self.layout.grid_flow(columns=6, align=True)
                grid.prop(settings, 'assets_ignore_duplicates_filter')
                col = self.layout.column(align=True)

            col.prop(settings, 'asset_extract_previews')
            if settings.asset_extract_previews:
                grid = self.layout.grid_flow(columns=6, align=True)
                grid.prop(settings, 'asset_extract_previews_filter')
                col = self.layout.column(align=True)
                        
            self.layout.use_property_split = False
            if "Collections" in settings.asset_types_to_mark and settings.import_file == "BLEND":
                col.label(text="Collections:")
                col.prop(settings, 'mark_only_master_collection')
                col = self.layout.column(align=True)

            if "Objects" in settings.asset_types_to_mark:
                col.label(text="Object Types:")
                grid = self.layout.grid_flow(columns=3, align=True)
                grid.prop(settings, 'asset_object_types_filter')
                self.layout.use_property_split = True  # Align menu items to the right.
                col = self.layout.column(align=True)

            self.layout.use_property_split = True
        
            col = self.layout.column(align=True)
            col.prop(settings, 'asset_library_enum')
            col.prop(settings, 'asset_catalog_enum')
            if settings.asset_library != "NO_LIBRARY":
                col.prop(settings, 'asset_blend_location')
            col.prop(settings, 'pack_resources')
            col.prop(settings, 'asset_add_metadata')
            if settings.asset_add_metadata:
                col.prop(settings, 'asset_description')
                col.prop(settings, 'asset_license')
                col.prop(settings, 'asset_copyright')
                col.prop(settings, 'asset_author')
                col.prop(settings, 'asset_tags')
                col = self.layout.column(align=True)
    
    if not settings.archive_assets:
        col.prop(settings, 'asset_extract_previews')


# Draws the button and popover dropdown button used in the
# 3D Viewport Header or Top Bar
def draw_popover(self, context):
    row = self.layout.row()
    row = row.row(align=True)
    row.operator('transmogrifier.transmogrify', text='', icon='FILE_CACHE')
    row.popover(panel='POPOVER_PT_transmogrify', text='')


# Create variables_dict dictionary from TransmogrifierSettings to pass to write_json function later.
def get_transmogrifier_settings(self, context):
    settings = context.scene.transmogrifier
    keys = [key for key in TransmogrifierSettings.__annotations__ if "enum" not in key]
    values = []
    for key in keys:
        # Get value as string to be evaluated later.
        value = eval('settings.' + str(key))
        # Convert relative paths to absolute paths.
        directory_path = ("directory", "directory_output_custom", "textures_custom_dir", "uv_directory_custom")
        if key in directory_path:
            value = bpy.path.abspath(value)
        # Convert enumproperty numbers to numbers.
        if key == "texture_resolution" or key == "resize_textures_limit" or key == "uv_resolution":
            if value != "Default":
                value = int(value)
        # Convert dictionaries and vectors to tuples.
        if "{" in str(value):
            value = tuple(value)
        elif "<" in str(value):
            value = str(value)
            char_start = "("
            char_end = ")"
            value = eval(re.sub('[xyz=]', '', "(" + ''.join(value).split(char_start)[1].split(char_end)[0] + ")"))
        values.append(value)

    variables_dict = dict(zip(keys, values))

    return variables_dict


# Write user variables to a JSON file.
def write_json(variables_dict, json_file):
        
    with open(json_file, "w") as outfile:
        json.dump(variables_dict, outfile)


# Read the JSON file where the conversion count is stored.
def read_json():
    # Open JSON file
    json_file = Path(__file__).parent.resolve() / "Converter_Report.json"

    with open(json_file, 'r') as openfile:
    
        # Read from JSON file
        json_object = json.load(openfile)
    
    return json_object



# Side Panel panel (used with Side Panel option)
class VIEW3D_PT_transmogrify_general(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Transmogrifier"
    bl_label = "⚙  General"

    def draw(self, context):
        draw_settings_general(self, context)
        
class VIEW3D_PT_transmogrify_textures(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Transmogrifier"
    bl_label = "🏁  Textures"

    def draw(self, context):
        draw_settings_textures(self, context)

class VIEW3D_PT_transmogrify_scene(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Transmogrifier"
    bl_label = "📐  Scene"

    def draw(self, context):
        draw_settings_transforms(self, context)

class VIEW3D_PT_transmogrify_optimize_files(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Transmogrifier"
    bl_label = "⏬  Optimize"

    def draw(self, context):
        draw_settings_optimize_files(self, context)

class VIEW3D_PT_transmogrify_archive(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Transmogrifier"
    bl_label = "🗄  Archive"

    def draw(self, context):
        draw_settings_archive(self, context)

# Popover panel (used on 3D Viewport Header or Top Bar option)
class POPOVER_PT_transmogrify(Panel):
    bl_space_type = 'TOPBAR'
    bl_region_type = 'HEADER'
    bl_label = "Transmogrifier"

    def draw(self, context):
        draw_settings_general(self, context)
        draw_settings_textures(self, context)
        draw_settings_transforms(self, context)
        draw_settings_optimize_files(self, context)
        draw_settings_archive(self, context)

# Copy import/export/transmogrifier presets and studiolights shipped with Transmogrifier to relevant Blender Preferences directories.
class COPY_ASSETS(Operator):
    """Copy an HDRI and example presets shipped with Transmogrifier to User Preferences"""
    bl_idname = "copyassets.transmogrifier"
    bl_label = "Copy Assets to Preferences"

    def execute(self, context):
        # Define paths.
        assets_dir = Path(__file__).parent / "assets"
        hdr_dir_src = assets_dir / "datafiles" / "studiolights"
        hdr_dir_dest = bpy.utils.user_resource('DATAFILES', path="studiolights")
        presets_dir_src = assets_dir / "presets" / "operator"
        presets_dir_dest = bpy.utils.user_resource('SCRIPTS', path="presets/operator")

        # Make list of source paths and destination paths (parents).
        dir_src_list = [hdr_dir_src, presets_dir_src]
        dir_dest_list = [hdr_dir_dest, presets_dir_dest]
        
        # Loop through list of source paths and copy files to parent- (or operator) specific destinations. Overwrite original files to ensure they get updated with each release.
        for dir_src in dir_src_list:
            for subdir, dirs, files in os.walk(dir_src):
                for file in files:
                    operator = Path(subdir).name
                    file_src = Path(subdir, file)
                    dir_dest_parent = dir_dest_list[dir_src_list.index(dir_src)]
                    file_dest = Path(dir_dest_parent, operator, file)
                    dir_dest = Path(file_dest).parent
                    if not Path(dir_dest).exists():
                        Path(dir_dest).mkdir(parents=True, exist_ok=True)
                    shutil.copy(file_src, file_dest)
        
        self.report({'INFO'}, "Copied Assets to Preferences")

        return {'FINISHED'}


# Addon settings that are NOT specific to a .blend file
class TransmogrifierPreferences(AddonPreferences):
    bl_idname = __name__

    def addon_location_updated(self, context):
        bpy.types.TOPBAR_MT_editor_menus.remove(draw_popover)
        bpy.types.VIEW3D_MT_editor_menus.remove(draw_popover)
        if hasattr(bpy.types, "VIEW3D_PT_transmogrify_general"):
            bpy.utils.unregister_class(VIEW3D_PT_transmogrify_general)
            bpy.utils.unregister_class(VIEW3D_PT_transmogrify_textures)
            bpy.utils.unregister_class(VIEW3D_PT_transmogrify_scene)
            bpy.utils.unregister_class(VIEW3D_PT_transmogrify_optimize_files)
            bpy.utils.unregister_class(VIEW3D_PT_transmogrify_archive)
        if self.addon_location == 'TOPBAR':
            bpy.types.TOPBAR_MT_editor_menus.append(draw_popover)
        elif self.addon_location == '3DHEADER':
            bpy.types.VIEW3D_MT_editor_menus.append(draw_popover)
        elif self.addon_location == '3DSIDE':
            bpy.utils.register_class(VIEW3D_PT_transmogrify_general)
            bpy.utils.register_class(VIEW3D_PT_transmogrify_textures)
            bpy.utils.register_class(VIEW3D_PT_transmogrify_scene)
            bpy.utils.register_class(VIEW3D_PT_transmogrify_optimize_files)
            bpy.utils.register_class(VIEW3D_PT_transmogrify_archive)


    addon_location: EnumProperty(
        name="Addon Location",
        description="Where to put the Transmogrifier Addon UI",
        items=[
            ('TOPBAR', "Top Bar",
             "Place on Blender's Top Bar (Next to File, Edit, Render, Window, Help)"),
            ('3DHEADER', "3D Viewport Header",
             "Place in the 3D Viewport Header (Next to View, Select, Add, etc.)"),
            ('3DSIDE', "3D Viewport Side Panel (Transmogrifier Tab)",
             "Place in the 3D Viewport's right side panel, in the Transmogrifier Tab"),
        ],
        default='3DSIDE',
        update=addon_location_updated,
    )

    def draw(self, context):
        layout = self.layout
        col = layout.column()

        # Display addon location options
        layout.prop(self, "addon_location")
        
        # Display copy assets button
        box = layout.box()
        col = box.column(align=True)
        col.operator("copyassets.transmogrifier", text="Copy Assets to Preferences", icon="DUPLICATE")


# Operator called when Transmogrifier preset is selected.
class REFRESHUI(Operator):
    """Refreshes Transmogrifier UI to reflect preset settings"""
    bl_idname = "refreshui.transmogrifier"
    bl_label = "Refresh UI"

    def execute(self, context):
        settings = context.scene.transmogrifier

        if settings.transmogrifier_preset != "NO_PRESET":
            # Load selected Transmogrifier preset as a dictionary.
            transmogrifier_preset_dict = load_transmogrifier_preset('transmogrifier', settings.transmogrifier_preset)

            # Read dictionary and change UI settings to reflect selected preset.
            for key, value in transmogrifier_preset_dict.items():
                # Make sure double-backslashes are preserved in directory path.
                directories_set = ("directory", "directory_output_custom", "textures_custom_dir", "uv_directory_custom")
                if key in directories_set and value != "":
                    value = "'" + repr(value) + "'"
                # Don't affect currently selected Transmogrifier preset
                elif key == "transmogrifier_preset":
                    continue
                # Wrap strings in quotations to ensure they're interpreted as strings in exec() function below.
                if type(value) == str:
                    if value == '':
                        value = "''"
                    else:
                        value = "'" + value + "'"
                # If a value is a list that contains strings, then change the list to a set.
                elif type(value) == list and type(value[0]) == str:
                    value = set(value)
                # If an integer object is an option of an EnumProperty drop down, make it a string.
                if key in ("texture_resolution", "resize_textures_limit", "uv_resolution") and type(value) == int:
                    value = "'" + str(value) + "'"   
                # Concatenate the current variable/setting to be updated.
                update_setting = 'settings.' + str(key) + ' = ' + str(value)
                # Make the setting (key) equal to the preset (value)
                exec(update_setting)

        return {'FINISHED'} 


class ADD_TRANSMOGRIFIER_PRESET(Operator):
    """Creates a Transmogrifier preset from current settings"""
    bl_idname = "transmogrifierpreset.add"
    bl_label = "Add Preset"

    preset_name: bpy.props.StringProperty(name="Name", default="")


    def execute(self, context):
        
        variables_dict = get_transmogrifier_settings(self, context)
        add_preset_name = self.preset_name + ".json"
        json_file = Path(bpy.utils.script_paths(subdir="presets/operator/transmogrifier")[0]) / add_preset_name
        write_json(variables_dict, json_file)

        return {'FINISHED'}
    
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=200)
    
class REMOVE_TRANSMOGRIFIER_PRESET(Operator):
    """Removes currently selected Transmogrifier preset"""
    bl_idname = "transmogrifierpreset.remove"
    bl_label = "Remove Preset"


    def execute(self, context):
        
        settings = context.scene.transmogrifier
        remove_preset_name = settings.transmogrifier_preset_enum + ".json"
        json_file = Path(bpy.utils.script_paths(subdir="presets/operator/transmogrifier")[0]) / remove_preset_name

        if remove_preset_name != "NO_PRESET":
            Path.unlink(json_file)

        return {'FINISHED'}

# Operator called when pressing the Batch Convert button.
class TRANSMOGRIFY(Operator):
    """Batch converts 3D files and associated textures into other formats"""
    bl_idname = "transmogrifier.transmogrify"
    bl_label = "Batch Convert"
    file_count = 0

    # Stop converter if directory has not been selected or .blend file has not been saved.
    def check_directory_path(self, context, directory):
        if directory != bpy.path.abspath(directory): # Then the blend file hasn't been saved
            self.report({'ERROR'}, "Save .blend file somewhere before using a relative directory path\n(or use an absolute directory path instead)")
            return False
        directory = bpy.path.abspath(directory)  # Convert to absolute path
        if not Path(directory).is_dir() or directory == "":
            self.report({'ERROR'}, (Path(directory).name + " directory doesn't exist"))
            return False
        return True


    def execute(self, context):
        settings = context.scene.transmogrifier

        base_dir = settings.directory
        directory_checks_out = self.check_directory_path(context, settings.directory)
        if not directory_checks_out:
            return {'FINISHED'}

        # Create path to Converter.py
        converter_py = Path(__file__).parent.resolve() / "Converter.py"

        self.file_count = 0

        self.export_selection(context, base_dir)

        if self.file_count == 0:
            self.report({'ERROR'}, "Could not convert.")
        else:
            converter_report_dict = read_json()
            conversion_count = converter_report_dict["conversion_count"]
            if conversion_count > 1:
                self.report({'INFO'}, "Conversion complete. " + str(conversion_count) + " files were converted.")
            elif conversion_count == 1:
                self.report({'INFO'}, "Conversion complete. " + str(conversion_count) + " file was converted.")
            else:
                self.report({'INFO'}, "Could not convert or no items needed conversion. " + str(conversion_count) + " files were converted.")

        return {'FINISHED'}


    def select_children_recursive(self, obj, context):
        for c in obj.children:
            if obj.type in context.scene.transmogrifier.texture_resolution_include:
                c.select_set(True)
            self.select_children_recursive(c, context)


    def export_selection(self, context, base_dir):
        settings = context.scene.transmogrifier

        # Create variables_dict dictionary from TransmogrifierSettings to pass to write_json function later.
        variables_dict = get_transmogrifier_settings(self, context)

        # Create path to StartConverter.cmd
        start_converter_file = Path(__file__).parent.resolve() / "StartConverter.cmd"

        # Create path to blender.exe
        blender_dir = bpy.app.binary_path

        # Create path to Converter.blend
        converter_blend = Path(__file__).parent.resolve() / "Converter.blend"

        # Create path to Converter.py
        converter_py = Path(__file__).parent.resolve() / "Converter.py"
        
        # Create path to Transmogrifier directory
        transmogrifier_dir = Path(__file__).parent.resolve()

        # Check directories and stop converter if they're not right.
        custom_menu_options_to_check = [settings.directory_output_location, settings.textures_source, settings.uv_export_location]
        directories_to_check = [settings.directory_output_custom, settings.textures_custom_dir, settings.uv_directory_custom]
        index = 0
        for menu in custom_menu_options_to_check:
            if menu != "Custom":
                index += 1
                continue
            directory_checks_out = self.check_directory_path(context, directories_to_check[index])
            if not directory_checks_out:
                return {'FINISHED'}
            index += 1
            

        # Determine options and import command for Import File Format

        if settings.import_file == "DAE":
            options = load_operator_preset(
                'wm.collada_import', settings.import_dae_preset)
            #bpy.ops.wm.collada_import(**options)
            import_file_command = "bpy.ops.wm.collada_import(**"
            
        elif settings.import_file == "ABC":
            options = load_operator_preset(
                'wm.alembic_import', settings.import_abc_preset)
            # By default, alembic_export operator runs in the background, this messes up batch
            # export though. alembic_export has an "as_background_job" arg that can be set to
            # false to disable it, but its marked deprecated, saying that if you EXECUTE the
            # operator rather than INVOKE it it runs in the foreground. Here I change the
            # execution context to EXEC_REGION_WIN.
            # docs.blender.org/api/current/bpy.ops.html?highlight=exec_default#execution-context
            #bpy.ops.wm.alembic_import('EXEC_REGION_WIN', **options)
            import_file_command = "bpy.ops.wm.alembic_import('EXEC_REGION_WIN', **"

        elif settings.import_file == "USD":
            options = load_operator_preset(
                'wm.usd_import', settings.import_usd_preset)
            import_file_command = "bpy.ops.wm.usd_import(**"

        elif settings.import_file == "OBJ":
            options = load_operator_preset(
                'wm.obj_import', settings.import_obj_preset)
            import_file_command = "bpy.ops.wm.obj_import(**"
            
        elif settings.import_file == "PLY":
            options = {
                'filepath': '',
            }
            import_file_command = "bpy.ops.import_mesh.ply(**"
            
        elif settings.import_file == "STL":
            options = {
                'filepath': '',
            }
            import_file_command = "bpy.ops.import_mesh.stl(**"

        elif settings.import_file == "FBX":
            options = load_operator_preset(
                'import_scene.fbx', settings.import_fbx_preset)
            import_file_command = "bpy.ops.import_scene.fbx(**"

        elif settings.import_file == "glTF":
            options = {
                'filepath': '',
            }
            import_file_command = "bpy.ops.import_scene.gltf(**"

        elif settings.import_file == "X3D":
            options = load_operator_preset(
                'import_scene.x3d', settings.import_x3d_preset)
            import_file_command = "bpy.ops.import_scene.x3d(**"

        elif settings.import_file == "BLEND":
            options = {
                "filepath": "",
                "directory": "\\Object\\",
                "autoselect": True,
                "active_collection": True,
                "instance_collections": False,
                "instance_object_data": True,
                "set_fake": False,
                "use_recursive": True
            }
            import_file_command = "bpy.ops.wm.append(**"
        
        # Set import variables to write to JSON
        
        # Set import file extension
        if settings.import_file == "glTF":
            import_file_ext = settings.import_gltf_extension
        elif settings.import_file == "USD":
            import_file_ext = settings.import_usd_extension
        else:
            import_file_ext = "." + settings.import_file.lower()
        
        # Set import file options
        import_file_options = options



        # Determine options and export command for Export File Format 1

        if settings.export_file_1 == "DAE":
            options = load_operator_preset(
                'wm.collada_export', settings.dae_preset)
            options["filepath"] = "export_file_1"
            options["selected"] = True
            #bpy.ops.wm.collada_export(**options)
            export_file_1_command = "bpy.ops.wm.collada_export(**"
            
        elif settings.export_file_1 == "ABC":
            options = load_operator_preset(
                'wm.alembic_export', settings.abc_preset)
            options["filepath"] = "export_file_1"
            options["selected"] = True
            # By default, alembic_export operator runs in the background, this messes up batch
            # export though. alembic_export has an "as_background_job" arg that can be set to
            # false to disable it, but its marked deprecated, saying that if you EXECUTE the
            # operator rather than INVOKE it it runs in the foreground. Here I change the
            # execution context to EXEC_REGION_WIN.
            # docs.blender.org/api/current/bpy.ops.html?highlight=exec_default#execution-context
            #bpy.ops.wm.alembic_export('EXEC_REGION_WIN', **options)
            export_file_1_command = "bpy.ops.wm.alembic_export('EXEC_REGION_WIN', **"

        elif settings.export_file_1 == "USD":
            options = load_operator_preset(
                'wm.usd_export', settings.usd_preset)
            options["filepath"] = "export_file_1"
            options["selected_objects_only"] = True
            #bpy.ops.wm.usd_export(**options)
            export_file_1_command = "bpy.ops.wm.usd_export(**"

        elif settings.export_file_1 == "SVG":
            options = {
                'filepath': '',
            }
            # bpy.ops.wm.gpencil_export_svg(
            #     filepath="export_file_1", selected_object_type='SELECTED')
            export_file_1_command = "bpy.ops.wm.gpencil_export_svg(**"

        elif settings.export_file_1 == "PDF":
            options = {
                'filepath': '',
            }
            # bpy.ops.wm.gpencil_export_pdf(
            #     filepath="export_file_1", selected_object_type='SELECTED')
            export_file_1_command = "bpy.ops.wm.gpencil_export_pdf(**"

        elif settings.export_file_1 == "OBJ":
            options = load_operator_preset(
                'wm.obj_export', settings.obj_preset)
            options["filepath"] = "export_file_1"
            options["export_selected_objects"] = True
            #bpy.ops.wm.obj_export(**options)
            export_file_1_command = "bpy.ops.wm.obj_export(**"

        elif settings.export_file_1 == "PLY":
            options = {
                'filepath': '',
            }
            # bpy.ops.export_mesh.ply(
            #     filepath="export_file_1", use_ascii=settings.ply_ascii, use_selection=True)
            export_file_1_command = "bpy.ops.export_mesh.ply(**"

        elif settings.export_file_1 == "STL":
            options = {
                'filepath': '',
            }
            # bpy.ops.export_mesh.stl(
            #     filepath="export_file_1", ascii=settings.stl_ascii, use_selection=True)
            export_file_1_command = "bpy.ops.export_mesh.stl(**"

        elif settings.export_file_1 == "FBX":
            options = load_operator_preset(
                'export_scene.fbx', settings.fbx_preset)
            options["filepath"] = "export_file_1"
            options["use_selection"] = True
            #bpy.ops.export_scene.fbx(**options)
            export_file_1_command = "bpy.ops.export_scene.fbx(**"

        elif settings.export_file_1 == "glTF":
            options = load_operator_preset(
                'export_scene.gltf', settings.gltf_preset)
            options["filepath"] = "export_file_1"
            options["use_selection"] = True
            #bpy.ops.export_scene.gltf(**options)
            export_file_1_command = "bpy.ops.export_scene.gltf(**" 

        elif settings.export_file_1 == "X3D":
            options = load_operator_preset(
                'export_scene.x3d', settings.x3d_preset)
            options["filepath"] = "export_file_1"
            options["use_selection"] = True
            #bpy.ops.export_scene.x3d(**options)
            export_file_1_command = "bpy.ops.export_scene.x3d(**"

        elif settings.export_file_1 == "BLEND":
            options = {
                "filepath": "",
                "compress": False,
                "relative_remap": True,
                "copy": False
            }
            export_file_1_command = "bpy.ops.wm.save_as_mainfile(**"

        # Set export variables to write to JSON
        
        # Set export file 1 extension
        if settings.export_file_1 == "glTF":
            try:
                if options["export_format"] == 'GLB':
                    export_file_1_ext = ".glb"
                else:
                    export_file_1_ext = ".gltf"
            except:
                export_file_1_ext = ".glb"
        elif settings.export_file_1 == "USD":
            export_file_1_ext = settings.usd_extension
        else:
            export_file_1_ext = "." + settings.export_file_1.lower()
        
        # Set export file options
        export_file_1_options = options



        # Determine options and import command for Export File Format 2

        if settings.export_file_2 == "DAE":
            options = load_operator_preset(
                'wm.collada_export', settings.dae_preset)
            options["filepath"] = "export_file_2"
            options["selected"] = True
            #bpy.ops.wm.collada_export(**options)
            export_file_2_command = "bpy.ops.wm.collada_export(**"
            
        elif settings.export_file_2 == "ABC":
            options = load_operator_preset(
                'wm.alembic_export', settings.abc_preset)
            options["filepath"] = "export_file_2"
            options["selected"] = True
            # By default, alembic_export operator runs in the background, this messes up batch
            # export though. alembic_export has an "as_background_job" arg that can be set to
            # false to disable it, but its marked deprecated, saying that if you EXECUTE the
            # operator rather than INVOKE it it runs in the foreground. Here I change the
            # execution context to EXEC_REGION_WIN.
            # docs.blender.org/api/current/bpy.ops.html?highlight=exec_default#execution-context
            #bpy.ops.wm.alembic_export('EXEC_REGION_WIN', **options)
            export_file_2_command = "bpy.ops.wm.alembic_export('EXEC_REGION_WIN', **"

        elif settings.export_file_2 == "USD":
            options = load_operator_preset(
                'wm.usd_export', settings.usd_preset)
            options["filepath"] = "export_file_2"
            options["selected_objects_only"] = True
            #bpy.ops.wm.usd_export(**options)
            export_file_2_command = "bpy.ops.wm.usd_export(**"

        elif settings.export_file_2 == "SVG":
            options = {
                'filepath': '',
            }
            # bpy.ops.wm.gpencil_export_svg(
            #     filepath="export_file_2", selected_object_type='SELECTED')
            export_file_2_command = "bpy.ops.wm.gpencil_export_svg(**"

        elif settings.export_file_2 == "PDF":
            options = {
                'filepath': '',
            }
            # bpy.ops.wm.gpencil_export_pdf(
            #     filepath="export_file_2", selected_object_type='SELECTED')
            export_file_2_command = "bpy.ops.wm.gpencil_export_pdf(**"

        elif settings.export_file_2 == "OBJ":
            options = load_operator_preset(
                'wm.obj_export', settings.obj_preset)
            options["filepath"] = "export_file_2"
            options["export_selected_objects"] = True
            #bpy.ops.wm.obj_export(**options)
            export_file_2_command = "bpy.ops.wm.obj_export(**"

        elif settings.export_file_2 == "PLY":
            options = {
                'filepath': '',
            }
            # bpy.ops.export_mesh.ply(
            #     filepath="export_file_2", use_ascii=settings.ply_ascii, use_selection=True)
            export_file_2_command = "bpy.ops.export_mesh.ply(**"      

        elif settings.export_file_2 == "STL":
            options = {
                'filepath': '',
            }
            # bpy.ops.export_mesh.stl(
            #     filepath="export_file_2", ascii=settings.stl_ascii, use_selection=True)
            export_file_2_command = "bpy.ops.export_mesh.stl(**"

        elif settings.export_file_2 == "FBX":
            options = load_operator_preset(
                'export_scene.fbx', settings.fbx_preset)
            options["filepath"] = "export_file_2"
            options["use_selection"] = True
            #bpy.ops.export_scene.fbx(**options)
            export_file_2_command = "bpy.ops.export_scene.fbx(**"

        elif settings.export_file_2 == "glTF":
            options = load_operator_preset(
                'export_scene.gltf', settings.gltf_preset)
            options["filepath"] = "export_file_2"
            options["use_selection"] = True
            #bpy.ops.export_scene.gltf(**options)
            export_file_2_command = "bpy.ops.export_scene.gltf(**"

        elif settings.export_file_2 == "X3D":
            options = load_operator_preset(
                'export_scene.x3d', settings.x3d_preset)
            options["filepath"] = "export_file_2"
            options["use_selection"] = True
            #bpy.ops.export_scene.x3d(**options)
            export_file_2_command = "bpy.ops.export_scene.x3d(**"
       
        elif settings.export_file_2 == "BLEND":
            options = {
                "filepath": "",
                "compress": False,
                "relative_remap": True,
                "copy": False
            }
            export_file_2_command = "bpy.ops.wm.save_as_mainfile(**"

        # Set export file 2 extension
        if settings.export_file_2 == "glTF":
            try:
                if options["export_format"] == 'GLB':
                    export_file_2_ext = ".glb"
                else:
                    export_file_2_ext = ".gltf"
            except:
                export_file_2_ext = ".glb"
        elif settings.export_file_2 == "USD":
            export_file_2_ext = settings.usd_extension
        else:
            export_file_2_ext = "." + settings.export_file_2.lower()
        
        # Set export file options
        export_file_2_options = options

        # Set length unit according to unit system.
        unit_system = settings.unit_system
        if unit_system == "METRIC":
            length_unit = settings.length_unit_metric
        elif unit_system == "IMPERIAL":
            length_unit = settings.length_unit_imperial
        elif unit_system == "NONE":
            length_unit = "NONE"

        # Update variables_dict with additional import/export options
        additional_settings_dict = {
            "import_file_ext": import_file_ext,
            "import_file_command": import_file_command, 
            "import_file_options": import_file_options, 
            "export_file_1_ext": export_file_1_ext, 
            "export_file_1_command": export_file_1_command, 
            "export_file_1_options": export_file_1_options, 
            "export_file_2_ext": export_file_2_ext, 
            "export_file_2_command": export_file_2_command, 
            "export_file_2_options": export_file_2_options, 
            "length_unit": length_unit
        }
        variables_dict.update(additional_settings_dict)

        # Write variables to JSON file before running converter
        json_file = Path(__file__).parent.resolve() / "Converter_Variables.json"
        write_json(variables_dict, json_file)

        # Run Converter.py
        subprocess.call(
            [
                blender_dir,
                converter_blend,
                "--python",
                converter_py,
            ],
            cwd=transmogrifier_dir
        ) 
        

        print("Conversion Complete")
        self.file_count += 1


# Groups together all the addon settings that are saved in each .blend file
class TransmogrifierSettings(PropertyGroup):
    # Preset Settings:
    # Option to select Transmogrifier presets
    transmogrifier_preset: StringProperty(default='FBX_to_GLB')
    transmogrifier_preset_enum: EnumProperty(
        name="", options={'SKIP_SAVE'},
        description="Use batch conversion settings from a preset.\n(Create by clicking '+' after adjusting settings in the Transmogrifier menu)",
        items=lambda self, context: get_transmogrifier_presets('transmogrifier'),
        get=lambda self: get_transmogrifier_preset_index('transmogrifier', self.transmogrifier_preset),
        set=lambda self, value: setattr(self, 'transmogrifier_preset', transmogrifier_preset_enum_items_refs['transmogrifier'][value][0]),
        update=refresh_ui
    )
    # UI Setting
    ui_toggle: EnumProperty(
        name="UI",
        items=[
            ('Simple', "Simple", "Show only basic conversion options", 1),
            ('Advanced', "Advanced", "Show all conversion options", 2),
        ],
        description="Toggle simple or advanced user interface options",
        default='Simple', 
    )
    # Import Settings
    directory: StringProperty(
        name="Directory",
        description="Parent directory to search through and import files\nDefault of // will import from the same directory as the blend file (only works if the blend file is saved)",
        default="//",
        subtype='DIR_PATH',
    )
    import_file: EnumProperty(
        name="Format",
        description="Which file format to import",
        items=[
            ("DAE", "Collada (.dae)", "", 1),
            ("ABC", "Alembic (.abc)", "", 2),
            ("USD", "Universal Scene Description (.usd/.usdc/.usda/.usdz)", "", 3),
            ("OBJ", "Wavefront (.obj)", "", 4),
            ("PLY", "Stanford (.ply)", "", 5),
            ("STL", "STL (.stl)", "", 6),
            ("FBX", "FBX (.fbx)", "", 7),
            ("glTF", "glTF (.glb/.gltf)", "", 8),
            ("X3D", "X3D Extensible 3D (.x3d)", "", 9),
            ("BLEND", "Blender (.blend)", "", 10)
        ],
        default="FBX",
    )
    # Import Format specific options:
    import_usd_extension: EnumProperty(
        name="Extension",
        description="Which type of USD to import",
        items=[
            (".usd", "Plain (.usd)",
             "Can be either binary or ASCII\nIn Blender this imports to binary", 1),
            (".usdc", "Binary Crate (default) (.usdc)",
             "Binary, fast, hard to edit", 2),
            (".usda", "ASCII (.usda)", "ASCII Text, slow, easy to edit", 3),
            (".usdz", "Zipped (.usdz)", "Packs textures and references into one file", 4),
        ],
        default=".usdz",
    )
    import_gltf_extension: EnumProperty(
        name="Extension",
        description="Which type of glTF to import",
        items=[
            (".glb", "glTF Binary (.glb)", "", 1),
            (".gltf", "glTF Embedded or Separate (.gltf)", "", 2),
        ],
        default=".glb"
    )
    ply_ascii: BoolProperty(name="ASCII Format", default=False)
    stl_ascii: BoolProperty(name="ASCII Format", default=False)

    # Presets: A string property for saving your option (without new presets changing your choice), and enum property for choosing
    import_abc_preset: StringProperty(default='NO_PRESET')
    import_abc_preset_enum: EnumProperty(
        name="Preset", options={'SKIP_SAVE'},
        description="Use import settings from a preset.\n(Create in the import settings from the File > import > Alembic (.abc))",
        items=lambda self, context: get_operator_presets('wm.alembic_import'),
        get=lambda self: get_preset_index(
            'wm.alembic_import', self.import_abc_preset),
        set=lambda self, value: setattr(
            self, 'import_abc_preset', preset_enum_items_refs['wm.alembic_import'][value][0]),
    )
    import_dae_preset: StringProperty(default='NO_PRESET')
    import_dae_preset_enum: EnumProperty(
        name="Preset", options={'SKIP_SAVE'},
        description="Use import settings from a preset.\n(Create in the import settings from the File > import > Collada (.dae))",
        items=lambda self, context: get_operator_presets('wm.collada_import'),
        get=lambda self: get_preset_index(
            'wm.collada_import', self.import_dae_preset),
        set=lambda self, value: setattr(
            self, 'import_dae_preset', preset_enum_items_refs['wm.collada_import'][value][0]),
    )
    import_usd_preset: StringProperty(default='NO_PRESET')
    import_usd_preset_enum: EnumProperty(
        name="Preset", options={'SKIP_SAVE'},
        description="Use import settings from a preset.\n(Create in the import settings from the File > import > Universal Scene Description (.usd, .usdc, .usda, .usdz))",
        items=lambda self, context: get_operator_presets('wm.usd_import'),
        get=lambda self: get_preset_index('wm.usd_import', self.import_usd_preset),
        set=lambda self, value: setattr(
            self, 'import_usd_preset', preset_enum_items_refs['wm.usd_import'][value][0]),
    )
    import_obj_preset: StringProperty(default='NO_PRESET')
    import_obj_preset_enum: EnumProperty(
        name="Preset", options={'SKIP_SAVE'},
        description="Use import settings from a preset.\n(Create in the import settings from the File > import > Wavefront (.obj))",
        items=lambda self, context: get_operator_presets('wm.obj_import'),
        get=lambda self: get_preset_index('wm.obj_import', self.import_obj_preset),
        set=lambda self, value: setattr(
            self, 'import_obj_preset', preset_enum_items_refs['wm.obj_import'][value][0]),
    )
    import_fbx_preset: StringProperty(default='NO_PRESET')
    import_fbx_preset_enum: EnumProperty(
        name="Preset", options={'SKIP_SAVE'},
        description="Use import settings from a preset.\n(Create in the import settings from the File > import > FBX (.fbx))",
        items=lambda self, context: get_operator_presets('import_scene.fbx'),
        get=lambda self: get_preset_index('import_scene.fbx', self.import_fbx_preset),
        set=lambda self, value: setattr(
            self, 'import_fbx_preset', preset_enum_items_refs['import_scene.fbx'][value][0]),
    )
    import_gltf_preset: StringProperty(default='NO_PRESET')
    import_gltf_preset_enum: EnumProperty(
        name="Preset", options={'SKIP_SAVE'},
        description="Use import settings from a preset.\n(Create in the import settings from the File > import > glTF (.glb/.gltf))",
        items=lambda self, context: get_operator_presets('import_scene.gltf'),
        get=lambda self: get_preset_index(
            'import_scene.gltf', self.import_gltf_preset),
        set=lambda self, value: setattr(
            self, 'import_gltf_preset', preset_enum_items_refs['import_scene.gltf'][value][0]),
    )
    import_x3d_preset: StringProperty(default='NO_PRESET')
    import_x3d_preset_enum: EnumProperty(
        name="Preset", options={'SKIP_SAVE'},
        description="Use import settings from a preset.\n(Create in the import settings from the File > import > X3D Extensible 3D (.x3d))",
        items=lambda self, context: get_operator_presets('import_scene.x3d'),
        get=lambda self: get_preset_index('import_scene.x3d', self.import_x3d_preset),
        set=lambda self, value: setattr(
            self, 'import_x3d_preset', preset_enum_items_refs['import_scene.x3d'][value][0]),
    )


    # Export Settings:
    export_file_1: EnumProperty(
        name="Format 1",
        description="Which file format to export to",
        items=[
            ("DAE", "Collada (.dae)", "", 1),
            ("ABC", "Alembic (.abc)", "", 2),
            ("USD", "Universal Scene Description (.usd/.usdc/.usda/.usdz)", "", 3),
            ("OBJ", "Wavefront (.obj)", "", 4),
            ("PLY", "Stanford (.ply)", "", 5),
            ("STL", "STL (.stl)", "", 6),
            ("FBX", "FBX (.fbx)", "", 7),
            ("glTF", "glTF (.glb/.gltf)", "", 8),
            ("X3D", "X3D Extensible 3D (.x3d)", "", 9),
            ("BLEND", "Blender (.blend)", "", 10),
        ],
        default="glTF",
    )
    # File 1 scale.
    export_file_1_scale: FloatProperty(
        name="Scale", 
        description="Set the scale of the model before exporting",
        default=1.0,
        soft_min=0.0,
        soft_max=10000.0,
        step=500,
    )
    # Export Settings 2:
    export_file_2: EnumProperty(
        name="Format 2",
        description="Which file format to export to",
        items=[
            ("DAE", "Collada (.dae)", "", 1),
            ("ABC", "Alembic (.abc)", "", 2),
            ("USD", "Universal Scene Description (.usd/.usdc/.usda/.usdz)", "", 3),
            ("OBJ", "Wavefront (.obj)", "", 4),
            ("PLY", "Stanford (.ply)", "", 5),
            ("STL", "STL (.stl)", "", 6),
            ("FBX", "FBX (.fbx)", "", 7),
            ("glTF", "glTF (.glb/.gltf)", "", 8),
            ("X3D", "X3D Extensible 3D (.x3d)", "", 9),
            ("BLEND", "Blender (.blend)", "", 10),
        ],
        default="USD",
    )
    # File 2 scale.
    export_file_2_scale: FloatProperty(
        name="Scale", 
        description="Set the scale of the model before exporting",
        default=1.0,
        soft_min=0.0,
        soft_max=10000.0,
        step=500,
    )
    # Export format specific options:
    usd_extension: EnumProperty(
        name="Extension",
        items=[
            (".usd", "Plain (.usd)",
             "Can be either binary or ASCII\nIn Blender this exports to binary", 1),
            (".usdc", "Binary Crate (default) (.usdc)",
             "Binary, fast, hard to edit", 2),
            (".usda", "ASCII (.usda)", "ASCII Text, slow, easy to edit", 3),
            (".usdz", "Zipped (.usdz)", "Packs textures and references into one file", 4),
        ],
        default=".usdz",
    )
    ply_ascii: BoolProperty(name="ASCII Format", default=False)
    stl_ascii: BoolProperty(name="ASCII Format", default=False)

    # Presets: A string property for saving your option (without new presets changing your choice), and enum property for choosing
    abc_preset: StringProperty(default='NO_PRESET')
    abc_preset_enum: EnumProperty(
        name="Preset", options={'SKIP_SAVE'},
        description="Use export settings from a preset.\n(Create in the export settings from the File > Export > Alembic (.abc))",
        items=lambda self, context: get_operator_presets('wm.alembic_export'),
        get=lambda self: get_preset_index(
            'wm.alembic_export', self.abc_preset),
        set=lambda self, value: setattr(
            self, 'abc_preset', preset_enum_items_refs['wm.alembic_export'][value][0]),
    )
    dae_preset: StringProperty(default='NO_PRESET')
    dae_preset_enum: EnumProperty(
        name="Preset", options={'SKIP_SAVE'},
        description="Use export settings from a preset.\n(Create in the export settings from the File > Export > Collada (.dae))",
        items=lambda self, context: get_operator_presets('wm.collada_export'),
        get=lambda self: get_preset_index(
            'wm.collada_export', self.dae_preset),
        set=lambda self, value: setattr(
            self, 'dae_preset', preset_enum_items_refs['wm.collada_export'][value][0]),
    )
    usd_preset: StringProperty(default='USDZ_Preset_Example')
    usd_preset_enum: EnumProperty(
        name="Preset", options={'SKIP_SAVE'},
        description="Use export settings from a preset.\n(Create in the export settings from the File > Export > Universal Scene Description (.usd, .usdc, .usda, .usdz))",
        items=lambda self, context: get_operator_presets('wm.usd_export'),
        get=lambda self: get_preset_index('wm.usd_export', self.usd_preset),
        set=lambda self, value: setattr(
            self, 'usd_preset', preset_enum_items_refs['wm.usd_export'][value][0]),
    )
    obj_preset: StringProperty(default='NO_PRESET')
    obj_preset_enum: EnumProperty(
        name="Preset", options={'SKIP_SAVE'},
        description="Use export settings from a preset.\n(Create in the export settings from the File > Export > Wavefront (.obj))",
        items=lambda self, context: get_operator_presets('wm.obj_export'),
        get=lambda self: get_preset_index('wm.obj_export', self.obj_preset),
        set=lambda self, value: setattr(
            self, 'obj_preset', preset_enum_items_refs['wm.obj_export'][value][0]),
    )
    fbx_preset: StringProperty(default='NO_PRESET')
    fbx_preset_enum: EnumProperty(
        name="Preset", options={'SKIP_SAVE'},
        description="Use export settings from a preset.\n(Create in the export settings from the File > Export > FBX (.fbx))",
        items=lambda self, context: get_operator_presets('export_scene.fbx'),
        get=lambda self: get_preset_index('export_scene.fbx', self.fbx_preset),
        set=lambda self, value: setattr(
            self, 'fbx_preset', preset_enum_items_refs['export_scene.fbx'][value][0]),
    )
    gltf_preset: StringProperty(default='GLB_Preset_Example')
    gltf_preset_enum: EnumProperty(
        name="Preset", options={'SKIP_SAVE'},
        description="Use export settings from a preset.\n(Create in the export settings from the File > Export > glTF (.glb/.gltf))",
        items=lambda self, context: get_operator_presets('export_scene.gltf'),
        get=lambda self: get_preset_index(
            'export_scene.gltf', self.gltf_preset),
        set=lambda self, value: setattr(
            self, 'gltf_preset', preset_enum_items_refs['export_scene.gltf'][value][0]),
    )
    x3d_preset: StringProperty(default='NO_PRESET')
    x3d_preset_enum: EnumProperty(
        name="Preset", options={'SKIP_SAVE'},
        description="Use export settings from a preset.\n(Create in the export settings from the File > Export > X3D Extensible 3D (.x3d))",
        items=lambda self, context: get_operator_presets('export_scene.x3d'),
        get=lambda self: get_preset_index('export_scene.x3d', self.x3d_preset),
        set=lambda self, value: setattr(
            self, 'x3d_preset', preset_enum_items_refs['export_scene.x3d'][value][0]),
    )


    # Pack resources into .blend.
    pack_resources: BoolProperty(
        name="Pack Resources",
        description="Pack all used external files into this .blend",
        default=True,
        )
    # Pack resources into .blend.
    make_paths_relative: BoolProperty(
        name="Relative Paths",
        description="Use relative paths for textures",
        default=True,
        )
    # Option for to where models should be exported.
    directory_output_location: EnumProperty(
        name="Location(s)",
        description="Select where models should be exported.",
        items=[
            ("Adjacents", "Adjacents", "Export each converted model to the same directory from which it was imported", 'FILE_FOLDER', 1),
            ("Custom", "Custom", "Export each converted model to a custom directory", 'NEWFOLDER', 2),
        ],
        default="Adjacents",
    )
    # Custom export directory
    directory_output_custom: StringProperty(
        name="Directory",
        description="Set a custom directory to which each converted model will be exported\nDefault of // will export to same directory as the blend file (only works if the blend file is saved)",
        default="//",
        subtype='DIR_PATH',
    )
    # Option to export models to subdirectories in custom directory
    use_subdirectories: BoolProperty(
        name="Subdirectories",
        description="Export models to their own subdirectories within the given directory",
        default=False,
    )
    # Option to include only models or also copy original folder contents to custom directory
    copy_item_dir_contents: BoolProperty(
        name="Copy Original Contents",
        description="Include original contents of each item's directory to its custom subdirectory",
        default=False,
    )
    # Option for how many models to export at a time.
    model_quantity: EnumProperty(
        name="Quantity",
        description="Choose whether to export one, two, or no model formats at a time",
        items=[
            ("1 Format", "1 Format", "Export one 3D model format for every model imported", 1),
            ("2 Formats", "2 Formats", "Export two 3D model formats for every model imported", 2),
            ("No Formats", "No Formats", "Don't export any 3D models (Useful if only batch texture conversion is desired)", 3),
        ],
        default="1 Format",
    )
    prefix: StringProperty(
        name="Prefix",
        description="Text to put at the beginning of all the exported file names",
    )
    suffix: StringProperty(
        name="Suffix",
        description="Text to put at the end of all the exported file names",
    )
    # Set data names from object names.
    set_data_names: BoolProperty(
        name="Data Names from Objects",
        description="Rename object data names according to their corresponding object names",
        default=True,
    )
    use_textures: BoolProperty(
        name="Use Textures", 
        description="Texture models with images from a selected source",
        default=True,
    )
    regex_textures: BoolProperty(
        name="Regex Textures", 
        description="Use regex to correct misspellings and inconsistencies in texture PBR names. This helps to guarantee their detection and import by Transmogrifier",
        default=True,
    )
    keep_modified_textures: BoolProperty(
        name="Keep Modified Textures", 
        description="Don't delete the textures directory used to modify image textures by regex and resolution and/or format",
        default=False,
    )
    textures_source: EnumProperty(
        name="Source", 
        description="Set the source of textures to be used",
        items=[
            ("External", "External", "Use textures nearby the imported model\n(Texture sets can exist in either 1) the same directory as the imported model, 2) a 'textures' subdirectory, or 3) texture set subdirectories within a 'textures' subdirectory)", 'FILE_FOLDER', 1),
            ("Packed", "Packed", "Use textures packed into each imported model", 'PACKAGE', 2),
            ("Custom", "Custom", "Use textures from a specific location for all models", 'NEWFOLDER', 3),
        ],
        default="External",
    )
    textures_custom_dir: StringProperty(
        name="Directory",
        description="Custom folder from which textures will be imported and applied to all converted objects",
        default="//",
        subtype='DIR_PATH',
    )
    copy_textures_custom_dir: BoolProperty(
        name="Copy to Model Folders", 
        description="Copy textures from custom directory to every folder from which a model is imported",
        default=False,
    )
    replace_textures: BoolProperty(
        name="Replace Textures", 
        description="Replace any existing textures folders with textures from custom directory",
        default=False,
    )
    use_linked_blend_textures: BoolProperty(
        name="Linked to .blend", 
        description="Use textures already linked to .blend file",
        default=False,
    )
    texture_resolution: EnumProperty(
        name="Resolution",
        description="Set a custom image texture resolution for exported models without affecting resolution of original/source texture files",
        items=[
            ("Default", "Default", "Don't resize, use imported resolution", 1),
            ("8192", "8192", "Square aspect ratio", 2),
            ("4096", "4096", "Square aspect ratio", 3),
            ("2048", "2048", "Square aspect ratio", 4),
            ("1024", "1024", "Square aspect ratio", 5),
            ("512", "512", "Square aspect ratio", 6),
            ("256", "256", "Square aspect ratio", 7),
            ("128", "128", "Square aspect ratio", 8),
        ],
        default="Default",
    )
    # Which textures to include in resizing.
    texture_resolution_include: EnumProperty(
        name="Included Textures",
        options={'ENUM_FLAG'},
        items=[
            ('BaseColor', "BaseColor", "", 1),
            ('Subsurface', "Subsurface", "", 2),
            ('Metallic', "Metallic", "", 4),
            ('Specular', "Specular", "", 16),
            ('Roughness', "Roughness", "", 32),
            ('Normal', "Normal", "", 64),
            ('Bump', "Bump", "", 128),
            ('Displacement', "Displacement", "", 256),
            ('Emission', "Emission", "", 512),
            ('Opacity', "Opacity", "", 1024),
            ('Occlusion', "Occlusion", "", 2048),
        ],
        description="Filter texture maps to resize",
        default={
            'BaseColor', 
            'Subsurface', 
            'Metallic', 
            'Specular', 
            'Roughness', 
            'Normal', 
            'Bump', 
            'Displacement', 
            'Emission', 
            'Opacity', 
            'Occlusion'
        },
    )
    image_format: EnumProperty(
        name="Format",
        description="Set a custom texture image type for exported models without affecting resolution of original/source texture files",
        items=[
            ("Default", "Default", "Don't convert image textures", 1),
            ("PNG", "PNG", "Save image textures in PNG format", 2),
            ("JPEG", "JPEG", "Save image textures in JPEG format", 3),
            ("TARGA", "TARGA", "Save image textures in TARGA format", 4),
            ("TIFF", "TIFF", "Save image textures in TIFF format", 5),
            ("WEBP", "WEBP", "Save image textures in WEBP format", 6),
            ("BMP", "BMP", "Save image textures in BMP format", 7),
            ("OPEN_EXR", "OPEN_EXR", "Save image textures in OpenEXR format", 8),
            # ("JPEG2000", "JPEG2000", "Save image textures in JPEG2000 format", 9),
            # ("CINEON", "CINEON", "Save image textures in CINEON format", 10),
            # ("DPX", "DPX", "Save image textures in DPX format", 11),
            # ("HDR", "HDR", "Save image textures in HDR format", 12),
        ],
        default="Default",
    )
    image_quality: IntProperty(
        name="Quality", 
        description="(%) Quality for image formats that support lossy compression",
        default=90,
        soft_min=0,
        soft_max=100,
        step=5,
    )
    # Which textures to include in converting.
    image_format_include: EnumProperty(
        name="Included Textures",
        options={'ENUM_FLAG'},
        items=[
            ('BaseColor', "BaseColor", "", 1),
            ('Subsurface', "Subsurface", "", 2),
            ('Metallic', "Metallic", "", 4),
            ('Specular', "Specular", "", 16),
            ('Roughness', "Roughness", "", 32),
            ('Normal', "Normal", "", 64),
            ('Bump', "Bump", "", 128),
            ('Displacement', "Displacement", "", 256),
            ('Emission', "Emission", "", 512),
            ('Opacity', "Opacity", "", 1024),
            ('Occlusion', "Occlusion", "", 2048),
        ],
        description="Filter texture maps to convert",
        default={
            'BaseColor', 
            'Subsurface', 
            'Metallic', 
            'Specular', 
            'Roughness', 
            'Normal', 
            'Bump', 
            'Displacement', 
            'Emission', 
            'Opacity', 
            'Occlusion'
        },
    )
    # Set all UV map names to "UVMap". This prevents a material issue with USDZ's - when object A and object B share the same material, but their UV
    # map names differ, the material has to pick one UVMap in the UV Map node inputs connected to each texture channel. So if object A's UV map is called
    # "UVMap" but object B's UV map is called "UV_Channel", then the shared material may pick "UV_Channel" as the UV inputs, thus causing object A to appear
    # untextured despite the fact that it shares the same material as object B.
    rename_uvs: BoolProperty(
        name="Rename UV Maps",
        description="Normalize UV map names.  Multiple UV maps within the same object will increment, for example, as 'UVMap', 'UVMap_1', 'UVMap_2', and so on. This prevents an issue in USD formats when two or more objects share the same material but have different UV map names, which causes some objects to appear untextured",
        default=True,
    )
    rename_uvs_name: StringProperty(
        name="Name",
        description="Text to rename all UV maps (e.g. 'UVMap', 'UVChannel', 'map')",
        default="UVMap"
    )
    export_uv_layout: BoolProperty(
        name="Export UV Maps",
        description="Export UV layout to file",
        default=False,
    )
    modified_uvs: BoolProperty(
        name="Modified",
        description="Export UVs from the modified mesh",
        default=False,
    )
    uv_export_location: EnumProperty(
        name="Location(s)",
        description="Select where UV layouts should be exported",
        items=[
            ("Textures", "Textures", "Export UVs to a Textures subfolder for each item. If none exists, create one", 'TEXTURE', 1),
            ("UV", "UV", "Export UVs to a 'UV' subfolder for each item. If none exists, create one", 'UV', 2),
            ("Adjacents", "Adjacents", "Export UVs to the same directories as converted models for each item", 'FILE_FOLDER', 3),
            ("Custom", "Custom", "Export all UVs to a custom directory of choice", 'NEWFOLDER', 4),
        ],
        default="UV",
    )
    uv_directory_custom: StringProperty(
        name="Directory",
        description="Set a custom directory to which UV maps will be exported\nDefault of // will export to same directory as the blend file (only works if the blend file is saved)",
        default="//",
        subtype='DIR_PATH',
    )
    uv_combination: EnumProperty(
        name="Combination",
        description="Select how UV layouts should be combined upon export",
        items=[
            ("All", "All", "Export all UVs together (1 UV layout per converted model)", 'STICKY_UVS_LOC', 1),
            ("Object", "Object", "Export UVs by object (1 UV layout per object)", 'OBJECT_DATA', 2),
            ("Material", "Material", "Export UVs by material (1 UV layout per material)", 'MATERIAL', 3),
        ],
        default="Material",
    )
    uv_resolution: EnumProperty(
        name="Resolution",
        description="Set a custom image texture resolution for exported models without affecting resolution of original/source texture files",
        items=[
            ("8192", "8192", "Square aspect ratio", 1),
            ("4096", "4096", "Square aspect ratio", 2),
            ("2048", "2048", "Square aspect ratio", 3),
            ("1024", "1024", "Square aspect ratio", 4),
            ("512", "512", "Square aspect ratio", 5),
            ("256", "256", "Square aspect ratio", 6),
            ("128", "128", "Square aspect ratio", 7),
        ],
        default="1024",
    )
    uv_format: EnumProperty(
        name="Format",
        description="File format to export the UV layout to \n(Transparency only works for PNG, EPS, and SVG)",
        items=[
            ("PNG", "PNG", "Export the UV layout to bitmap PNG image", 1),
            ("EPS", "EPS", "Export the UV layout to a vector EPS file", 2),
            ("SVG", "SVG", "Export the UV layout to a vector SVG file", 3),
            ("JPEG", "JPEG", "Export the UV layout to bitmap JPEG format", 4),
            ("TARGA", "TARGA", "Export the UV layout to bitmap TARGA format", 5),
            ("TIFF", "TIFF", "Export the UV layout to bitmap TIFF format", 6),
            ("WEBP", "WEBP", "Export the UV layout to bitmap WEBP format", 7),
            ("BMP", "BMP", "Export the UV layout to bitmap BMP format", 8),
            ("OPEN_EXR", "OPEN_EXR", "Export the UV layout to bitmap OpenEXR format", 9),
        ],
        default="PNG",
    )
    uv_image_quality: IntProperty(
        name="Quality", 
        description="(%) Quality for image formats that support lossy compression",
        default=90,
        soft_min=0,
        soft_max=100,
        step=5,
    )
    uv_fill_opacity: FloatProperty(
        name="Fill Opacity", 
        description="Set amount of opacity for export UV layout \n(between 0.0 and 1.0)",
        default=0.0,
        soft_min=0.0,
        soft_max=1.0,
        step=1.0,
    )
    # Option to set custom transformations
    set_transforms: BoolProperty(
        name="Set", 
        description="Set custom transformations of the imported object(s) before exporting", 
        default=False
    )
    # Option to set custom transformations.
    set_transforms_filter: EnumProperty(
        name="Filter",
        options={'ENUM_FLAG'},
        items=[
            ('Location', "Location", "", 1),
            ('Rotation', "Rotation", "", 2),
            ('Scale', "Scale", "", 4),
        ],
        description="Filter transforms to set",
        default={
            'Location', 
            'Rotation', 
            'Scale', 
        },
    )
    # Set location amount.
    set_location: FloatVectorProperty(
        name="Location", 
        default=(0.0, 0.0, 0.0), 
        subtype="TRANSLATION"
    )
    # Set rotation amount.
    set_rotation: FloatVectorProperty(
        name="Rotation (XYZ Euler)", 
        default=(0.0, 0.0, 0.0), 
        subtype="EULER"
    )
    # Set scale amount.
    set_scale: FloatVectorProperty(
        name="Scale", 
        default=(1.0, 1.0, 1.0), 
        subtype="XYZ"
    )
    # Apply transformations.
    apply_transforms: BoolProperty(
        name="Apply", 
        description="Apply all transformations on all objects",
        default=True,
    )
    # Filter what transforms to apply.
    apply_transforms_filter: EnumProperty(
        name="Filter",
        options={'ENUM_FLAG'},
        items=[
            ('Location', "Location", "", 1),
            ('Rotation', "Rotation", "", 2),
            ('Scale', "Scale", "", 4),
        ],
        description="Filter transforms to apply during conversion",
        default={
            'Location', 
            'Rotation', 
            'Scale', 
        },
    )
    # Clear animation data.
    delete_animations: BoolProperty(
        name="Delete", 
        description="Remove all animation data from all objects",
        default=True,
    )
    # Set unit system:
    unit_system: EnumProperty(
        name="Unit System",
        description="Set the unit system to use for export",
        items=[
            ("METRIC", "Metric", "", 1),
            ("IMPERIAL", "Imperial", "", 2),
            ("NONE", "None", "", 3),
        ],
        default="METRIC",
    )
    # Set length unit if metric system was selected.
    length_unit_metric: EnumProperty(
        name="Length",
        description="Set the length unit to use for export",
        items=[
            ("ADAPTIVE", "Adaptive", "", 1),
            ("KILOMETERS", "Kilometers", "", 2),
            ("METERS", "Meters", "", 3),
            ("CENTIMETERS", "Centimeters", "", 4),
            ("MILLIMETERS", "Millimeters", "", 5),
            ("MICROMETERS", "Micrometers", "", 6),
        ],
        default="CENTIMETERS",
    )
    # Set length unit if imperial system was selected.
    length_unit_imperial: EnumProperty(
        name="Length",
        description="Set the length unit to use for export",
        items=[
            ("ADAPTIVE", "Adaptive", "", 1),
            ("MILES", "Miles", "", 2),
            ("FEET", "Feet", "", 3),
            ("INCHES", "Inches", "", 4),
            ("THOU", "Thousandths", "", 5),
        ],
        default="INCHES",
    )
    # Option to set file size maximum.
    auto_resize_files: EnumProperty(
        name="Files Included",
        description="Set a maximum file size and Transmogrifier will automatically try to reduce the file size according to the requested size. If exporting 2 formats at once, it only takes the first file format into account",
        items=[
            ("All", "All", "Auto-optimize all exported files even if some previously exported files are already below the target maximum", 1),
            ("Only Above Max", "Only Above Max", "Only auto-optimize exported files are still above the threshold. Ignore previously exported files that are already below the target maximum", 2),
            ("None", "None", "Don't auto-optimize any exported files", 3),
        ],
        default="All",
    )
    # File size maximum target.
    file_size_maximum: FloatProperty(
        name="Limit (MB)", 
        description="Set the threshold below which Transmogrifier should attempt to reduce the file size (Megabytes)",
        default=15.0,
        soft_min=0.0,
        soft_max=1000.0,
        step=10,
    )
    # Filter file size reduction methods.
    file_size_methods: EnumProperty(
        name="Methods",
        options={'ENUM_FLAG'},
        items=[
            ('Draco-Compress', "Draco-Compress", "(Only for GLB export). Try Draco-compression to lower the exported file size.", 'FULLSCREEN_EXIT', 1),
            ('Resize Textures', "Resize Textures", "Try resizing textures to lower the exported file size.", 'NODE_TEXTURE', 2),
            ('Reformat Textures', "Reformat Textures", "Try reformatting all textures except the normal map to JPEG's to lower the exported file size.", 'IMAGE_DATA', 4),
            ('Decimate Meshes', "Decimate Meshes", "Try decimating objects to lower the exported file size.", 'MOD_DECIM', 16),
        ],
        description="Filter file size reduction methods to use for automatic export file size reduction",
        default={
            'Resize Textures', 
            'Reformat Textures', 
            'Draco-Compress', 
        },
    )
    # Limit resolution that auto resize files should not go below.
    resize_textures_limit: EnumProperty(
        name="Resize Limit",
        description="Set minimum image texture resolution for auto file size not to go below. Images will not be upscaled",
        items=[
            ("8192", "8192", "Square aspect ratio", 1),
            ("4096", "4096", "Square aspect ratio", 2),
            ("2048", "2048", "Square aspect ratio", 3),
            ("1024", "1024", "Square aspect ratio", 4),
            ("512", "512", "Square aspect ratio", 5),
            ("256", "256", "Square aspect ratio", 6),
            ("128", "128", "Square aspect ratio", 7),
        ],
        default="512",
    )
    # Include normal map in auto-reformatting.
    reformat_normal_maps: BoolProperty(
        name="Reformat Normal Maps",
        description="Determine whether normal maps should be included in 'Reformat Textures' (to JPG's)",
        default=False,
        )
    # Limit how many time a mesh can be decimated during auto resize files.
    decimate_limit: IntProperty(
        name="Decimate Limit", 
        description="Limit the number of times an item can be decimated. Items will be decimated by 50% each time",
        default=3,
        soft_min=0,
        soft_max=10,
        step=1,
    )
    # Save conversion log.
    save_conversion_log: BoolProperty(
        name="Save Log",
        description="Save a log of the batch conversion in the given directory. This can help troubleshoot conversion errors",
        default=False,
    )
    # Mark data blocks as assets.
    archive_assets: BoolProperty(
        name="Archive Assets",
        description="Archive specified assets to Asset Library",
        default=True,
        )
    # Mark asset data filter.
    asset_types_to_mark: EnumProperty(
        name="Mark Assets",
        options={'ENUM_FLAG'},
        items=[
            ('Actions', "", "Mark individual actions (animations) as assets.", "ACTION", 1),
            ('Collections', "", "Mark individual collections as assets.", "OUTLINER_COLLECTION", 2),
            ('Materials', "", "Mark individual materials as assets.", "MATERIAL", 4),
            ('Node_Groups', "", "Mark individual node trees as assets.", "NODETREE", 8),
            ('Objects', "", "Mark individual objects as assets.", "OBJECT_DATA", 16),
            ('Worlds', "", "Mark individual worlds as assets.", "WORLD", 32),
        ],
        description="Select asset types to archive",
        default={
            'Collections',
            "Materials",
        },
    )
    assets_ignore_duplicates: BoolProperty(
        name="Ignore Duplicates",
        description="Ignore duplicate assets that already exist in the selected asset library.\n(i.e. Don't mark duplicates as assets)",
        default=True,
    )
    assets_ignore_duplicates_filter: EnumProperty(
        name="Ignore Duplicates Filter",
        options={'ENUM_FLAG'},
        items=[
            ('Actions', "", "Ignore duplicate actions. Actions with the same as one already\nin the selected asset library will not be marked as assets.", "ACTION", 1),
            ('Collections', "", "Ignore duplicate collections. Collections with the same as one already\nin the selected asset library will not be marked as assets.", "OUTLINER_COLLECTION", 2),
            ('Materials', "", "Ignore duplicate materials. Materials with the same as one already\nin the selected asset library will not be marked as assets.", "MATERIAL", 4),
            ('Node_Groups', "", "Ignore duplicate node trees. Node Trees with the same as one already\nin the selected asset library will not be marked as assets.", "NODETREE", 8),
            ('Objects', "", "Ignore duplicate objects. Objects with the same as one already\nin the selected asset library will not be marked as assets.", "OBJECT_DATA", 16),
            ('Worlds', "", "Ignore duplicate worlds. Worlds with the same as one already\nin the selected asset library will not be marked as assets.", "WORLD", 32),
        ],
        description="Filter which asset types to ignore when an asset\nof that type already exists in the selected asset library",
        default={
            'Actions',
            'Collections',
            "Materials",
            'Node_Groups',
            'Objects',
            'Worlds',
        },
    )
    mark_only_master_collection: BoolProperty(
        name="Mark Only Master",
        description="Mark only the master collection as an asset and ignore other collections.\n(For each item converted, all objects are moved to a master collection matching the item name.\nThis option is only relevant when importing .blend files that may already contain collections.)",
        default=True,
    )
    asset_object_types_filter: EnumProperty(
        name="Object Types",
        options={'ENUM_FLAG'},
        items=[
            ('MESH', "Mesh", "", 1),
            ('CURVE', "Curve", "", 2),
            ('SURFACE', "Surface", "", 4),
            ('META', "Metaball", "", 8),
            ('FONT', "Text", "", 16),
            ('GPENCIL', "Grease Pencil", "", 32),
            ('ARMATURE', "Armature", "", 64),
            ('EMPTY', "Empty", "", 128),
            ('LIGHT', "Lamp", "", 256),
            ('CAMERA', "Camera", "", 512),
        ],
        description="Filter which object types to mark as assets.\nNot all will be able to have preview images generated",
        default={
            'MESH', 
            'CURVE', 
            'SURFACE', 
            'META', 
            'FONT', 
            'GPENCIL', 
            'ARMATURE', 
            'LIGHT', 
            'CAMERA', 
        },
    )
    asset_library: StringProperty(default='(no library)')
    asset_library_enum: EnumProperty(
        name="Asset Library", options={'SKIP_SAVE'},
        description="Archive converted assets to selected library",
        items=lambda self, context: get_asset_libraries(),
        get=lambda self: get_asset_library_index(self.asset_library),
        set=lambda self, value: setattr(self, 'asset_library', asset_library_enum_items_refs["asset_libraries"][value][0]),
    )
    asset_catalog: StringProperty(default='(no catalog)')
    asset_catalog_enum: EnumProperty(
        name="Catalog", options={'SKIP_SAVE'},
        description="Assign converted assets to selected catalog",
        items=lambda self, context: get_asset_catalogs(),
        get=lambda self: get_asset_catalog_index(self.asset_catalog),
        set=lambda self, value: setattr(self, 'asset_catalog', asset_catalog_enum_items_refs["asset_catalogs"][value][0]),
    )
    asset_blend_location: EnumProperty(
        name="Blend Location",
        description="Set where the blend files containing assets will be stored",
        items=[
            ("Move", "Move to Library", "Move blend files and associated textures to selected asset library.", 1),
            ("Copy", "Copy to Library", "Copy blend files and associated textures to selected asset library.", 2),
            ("None", "Don't Move/Copy", "Don't move or copy blend files and associated textures to selected asset library.\n(Select this option when Transmogrifying inside an asset library directory.)", 3),
        ],
        default="Move",
    )
    asset_add_metadata: BoolProperty(
        name="Add Metadata",
        description="Add metadata to converted items",
        default=True,
    )
    asset_description: StringProperty(
        name="Description",
        description="A description of the asset to be displayed for the user",
    )
    asset_license: StringProperty(
        name="License",
        description="The type of license this asset is distributed under. An empty license name does not necessarily indicate that this is free of licensing terms. Contact the author if any clarification is needed",
    )
    asset_copyright: StringProperty(
        name="Copyright",
        description="Copyright notice for this asset. An empty copyright notice does not necessarily indicate that this is copyright-free. Contact the author if any clarification is needed",
    )
    asset_author: StringProperty(
        name="Author",
        description="Name of the creator of the asset",
    )
    asset_tags: StringProperty(
        name="Tags",
        description="Add new keyword tags to assets. Separate tags with a space",
    )
    asset_extract_previews: BoolProperty(
        name="Save Previews to Disk",
        description="Extract preview image thumbnail for every asset marked and save to disk as PNG.\n(Only works for assets that can have previews generated.)",
        default=True,
    )
    asset_extract_previews_filter: EnumProperty(
        name="Extract Previews Filter",
        options={'ENUM_FLAG'},
        items=[
            ('Actions', "", "Extract previews of Actions assets.", "ACTION", 1),
            ('Collections', "", "Extract previews of Collections assets.", "OUTLINER_COLLECTION", 2),
            ('Materials', "", "Extract previews of Materials assets.", "MATERIAL", 4),
            ('Node_Groups', "", "Extract previews of Node_Groups assets.", "NODETREE", 8),
            ('Objects', "", "Extract previews of Objects assets.", "OBJECT_DATA", 16),
            ('Worlds', "", "Extract previews of Worlds assets.", "WORLD", 32),
        ],
        description="Filter asset types from which to extract image previews to disk.",
        default={
            'Collections',
            'Objects',
        },
    )
    


def register():
    # Register classes
    bpy.utils.register_class(TransmogrifierPreferences)
    bpy.utils.register_class(TransmogrifierSettings)
    bpy.utils.register_class(POPOVER_PT_transmogrify)
    bpy.utils.register_class(COPY_ASSETS)
    bpy.utils.register_class(REFRESHUI)
    bpy.utils.register_class(ADD_TRANSMOGRIFIER_PRESET)
    bpy.utils.register_class(REMOVE_TRANSMOGRIFIER_PRESET)
    bpy.utils.register_class(TRANSMOGRIFY)

    # Add Batch Convert settings to Scene type
    bpy.types.Scene.transmogrifier = PointerProperty(type=TransmogrifierSettings)

    # Show addon UI
    prefs = bpy.context.preferences.addons[__name__].preferences
    if prefs.addon_location == 'TOPBAR':
        bpy.types.TOPBAR_MT_editor_menus.append(draw_popover)
    if prefs.addon_location == '3DHEADER':
        bpy.types.VIEW3D_MT_editor_menus.append(draw_popover)
    elif prefs.addon_location == '3DSIDE':
        bpy.utils.register_class(VIEW3D_PT_transmogrify_general)
        bpy.utils.register_class(VIEW3D_PT_transmogrify_textures)
        bpy.utils.register_class(VIEW3D_PT_transmogrify_scene)
        bpy.utils.register_class(VIEW3D_PT_transmogrify_optimize_files)
        bpy.utils.register_class(VIEW3D_PT_transmogrify_archive)


def unregister():
    # Delete the settings from Scene type (Doesn't actually remove existing ones from scenes)
    del bpy.types.Scene.transmogrifier

    # Unregister Classes
    bpy.utils.unregister_class(TransmogrifierPreferences)
    bpy.utils.unregister_class(TransmogrifierSettings)
    bpy.utils.unregister_class(POPOVER_PT_transmogrify)
    bpy.utils.unregister_class(COPY_ASSETS)
    bpy.utils.unregister_class(REFRESHUI)
    bpy.utils.unregister_class(ADD_TRANSMOGRIFIER_PRESET)
    bpy.utils.unregister_class(REMOVE_TRANSMOGRIFIER_PRESET)
    bpy.utils.unregister_class(TRANSMOGRIFY)

    # Remove UI
    bpy.types.TOPBAR_MT_editor_menus.remove(draw_popover)
    bpy.types.VIEW3D_MT_editor_menus.remove(draw_popover)
    if hasattr(bpy.types, "VIEW3D_PT_transmogrify_general"):
        bpy.utils.unregister_class(VIEW3D_PT_transmogrify_general)
        bpy.utils.unregister_class(VIEW3D_PT_transmogrify_textures)
        bpy.utils.unregister_class(VIEW3D_PT_transmogrify_scene)
        bpy.utils.unregister_class(VIEW3D_PT_transmogrify_optimize_files)
        bpy.utils.unregister_class(VIEW3D_PT_transmogrify_archive)


if __name__ == '__main__':
    register()
