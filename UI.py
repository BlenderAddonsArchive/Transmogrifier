#  █████       █████   █████████  ██████████ ██████   █████  █████████  ██████████
# ░░███       ░░███   ███░░░░░███░░███░░░░░█░░██████ ░░███  ███░░░░░███░░███░░░░░█
#  ░███        ░███  ███     ░░░  ░███  █ ░  ░███░███ ░███ ░███    ░░░  ░███  █ ░ 
#  ░███        ░███ ░███          ░██████    ░███░░███░███ ░░█████████  ░██████   
#  ░███        ░███ ░███          ░███░░█    ░███ ░░██████  ░░░░░░░░███ ░███░░█   
#  ░███      █ ░███ ░░███     ███ ░███ ░   █ ░███  ░░█████  ███    ░███ ░███ ░   █
#  ███████████ █████ ░░█████████  ██████████ █████  ░░█████░░█████████  ██████████
# ░░░░░░░░░░░ ░░░░░   ░░░░░░░░░  ░░░░░░░░░░ ░░░░░    ░░░░░  ░░░░░░░░░  ░░░░░░░░░░ 

##### BEGIN GPL LICENSE BLOCK #####

# This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

# You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>. 

##### END GPL LICENSE BLOCK #####



#  █████       █████ ███████████  ███████████     █████████   ███████████   █████ ██████████  █████████ 
# ░░███       ░░███ ░░███░░░░░███░░███░░░░░███   ███░░░░░███ ░░███░░░░░███ ░░███ ░░███░░░░░█ ███░░░░░███
#  ░███        ░███  ░███    ░███ ░███    ░███  ░███    ░███  ░███    ░███  ░███  ░███  █ ░ ░███    ░░░ 
#  ░███        ░███  ░██████████  ░██████████   ░███████████  ░██████████   ░███  ░██████   ░░█████████ 
#  ░███        ░███  ░███░░░░░███ ░███░░░░░███  ░███░░░░░███  ░███░░░░░███  ░███  ░███░░█    ░░░░░░░░███
#  ░███      █ ░███  ░███    ░███ ░███    ░███  ░███    ░███  ░███    ░███  ░███  ░███ ░   █ ███    ░███
#  ███████████ █████ ███████████  █████   █████ █████   █████ █████   █████ █████ ██████████░░█████████ 
# ░░░░░░░░░░░ ░░░░░ ░░░░░░░░░░░  ░░░░░   ░░░░░ ░░░░░   ░░░░░ ░░░░░   ░░░░░ ░░░░░ ░░░░░░░░░░  ░░░░░░░░░  


import bpy
from bpy.types import (
    AddonPreferences, 
    Panel,
    Operator, 
) 
from bpy.props import (
    EnumProperty,
    StringProperty,
)
from . import bl_info
from . import Custom_Scripts



#  █████  █████ █████
# ░░███  ░░███ ░░███ 
#  ░███   ░███  ░███ 
#  ░███   ░███  ░███ 
#  ░███   ░███  ░███ 
#  ░███   ░███  ░███ 
#  ░░████████   █████
#   ░░░░░░░░   ░░░░░ 


# Draws the .blend file specific settings used in the
# Popover panel or Side Panel panel
def draw_settings_general(self, context):
    settings = bpy.context.scene.TransmogrifierSettings
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
    col = self.layout.column(align=True)
    col.label(text="Export:", icon='EXPORT')

    col.prop(settings, "directory_output_location")
    if settings.directory_output_location == "Custom":
        col.prop(settings, "directory_output_custom")
        if settings.directory_output_custom:
            col.prop(settings, "use_subdirectories")
        if settings.ui_toggle == "Advanced":
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
    settings = bpy.context.scene.TransmogrifierSettings
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
            if settings.ui_toggle == "Advanced":
                col.prop(settings, 'copy_textures_custom_dir')
                if settings.copy_textures_custom_dir:
                    col.prop(settings, 'replace_textures')
                col = self.layout.column(align=True)
        
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
    settings = bpy.context.scene.TransmogrifierSettings
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
    settings = bpy.context.scene.TransmogrifierSettings
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
    settings = bpy.context.scene.TransmogrifierSettings
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


# Texture Settings
def draw_settings_scripts(self, context):
    settings = bpy.context.scene.TransmogrifierSettings
    col = self.layout.column(align=True)
    col.scale_y = 1.5
    col.label(text="Custom Scripts:", icon='FILE_SCRIPT')
    col.operator('ui.add_custom_script')

    # Adapted from Bystedts Blender Baker (GPL-3.0 License, https://3dbystedt.gumroad.com/l/JAqLT), UI.py, Line 508
    for index, custom_script in enumerate(context.scene.custom_scripts):   
        layout = self.layout
        layout.separator(factor = 1.0)
        custom_script_box = layout.box()
        main_col = custom_script_box.column()
        
        grid = main_col.grid_flow(row_major = True, columns = 2, even_columns = True)

        grid.label(text = "Script") 
        grid.prop(custom_script, "directory", text="")
        grid.label(text = "Trigger")          
        grid.prop(custom_script, "Trigger", text="")


# Draws the button and popover dropdown button used in the
# 3D Viewport Header or Top Bar
def draw_popover(self, context):
    row = self.layout.row()
    row = row.row(align=True)
    row.operator('transmogrifier.transmogrify', text='', icon='FILE_CACHE')
    row.popover(panel='POPOVER_PT_transmogrify', text='')


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

class VIEW3D_PT_transmogrify_scripts(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Transmogrifier"
    bl_label = "🐍  Scripts"

    def draw(self, context):
        draw_settings_scripts(self, context)

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
        draw_settings_scripts(self, context)


# Addon settings that are NOT specific to a .blend file
class TransmogrifierPreferences(AddonPreferences):
    bl_idname = bl_info["name"]

    def addon_location_updated(self, context):
        bpy.types.TOPBAR_MT_editor_menus.remove(draw_popover)
        bpy.types.VIEW3D_MT_editor_menus.remove(draw_popover)
        if hasattr(bpy.types, "VIEW3D_PT_transmogrify_general"):
            bpy.utils.unregister_class(VIEW3D_PT_transmogrify_general)
            bpy.utils.unregister_class(VIEW3D_PT_transmogrify_textures)
            bpy.utils.unregister_class(VIEW3D_PT_transmogrify_scene)
            bpy.utils.unregister_class(VIEW3D_PT_transmogrify_optimize_files)
            bpy.utils.unregister_class(VIEW3D_PT_transmogrify_archive)
            bpy.utils.unregister_class(VIEW3D_PT_transmogrify_scripts)
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
            bpy.utils.register_class(VIEW3D_PT_transmogrify_scripts)


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


# Adapted from Bystedts Blender Baker (GPL-3.0 License, https://3dbystedt.gumroad.com/l/JAqLT), UI.py, Line 782
class UI_OT_cgm_add_custom_script(Operator):
    '''
    Add new custom script to UI
    '''

    bl_idname = "ui.add_custom_script"
    bl_label = "Add Custom Script"

    print_string : StringProperty()

    def execute(self, context):
        # Import Custom_Scripts
        Custom_Scripts.add_customscript(context)
        return {'FINISHED'}



#  ███████████   ██████████   █████████  █████  █████████  ███████████ ███████████   █████ █████
# ░░███░░░░░███ ░░███░░░░░█  ███░░░░░███░░███  ███░░░░░███░█░░░███░░░█░░███░░░░░███ ░░███ ░░███ 
#  ░███    ░███  ░███  █ ░  ███     ░░░  ░███ ░███    ░░░ ░   ░███  ░  ░███    ░███  ░░███ ███  
#  ░██████████   ░██████   ░███          ░███ ░░█████████     ░███     ░██████████    ░░█████   
#  ░███░░░░░███  ░███░░█   ░███    █████ ░███  ░░░░░░░░███    ░███     ░███░░░░░███    ░░███    
#  ░███    ░███  ░███ ░   █░░███  ░░███  ░███  ███    ░███    ░███     ░███    ░███     ░███    
#  █████   █████ ██████████ ░░█████████  █████░░█████████     █████    █████   █████    █████   
# ░░░░░   ░░░░░ ░░░░░░░░░░   ░░░░░░░░░  ░░░░░  ░░░░░░░░░     ░░░░░    ░░░░░   ░░░░░    ░░░░░    

classes = (
    TransmogrifierPreferences,
    POPOVER_PT_transmogrify,
    UI_OT_cgm_add_custom_script,
)

# Register Classes.
def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    # Show addon UI
    prefs = bpy.context.preferences.addons[bl_info["name"]].preferences
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
        bpy.utils.register_class(VIEW3D_PT_transmogrify_scripts)

# Unregister Classes.
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    # Remove UI
    bpy.types.TOPBAR_MT_editor_menus.remove(draw_popover)
    bpy.types.VIEW3D_MT_editor_menus.remove(draw_popover)
    if hasattr(bpy.types, "VIEW3D_PT_transmogrify_general"):
        bpy.utils.unregister_class(VIEW3D_PT_transmogrify_general)
        bpy.utils.unregister_class(VIEW3D_PT_transmogrify_textures)
        bpy.utils.unregister_class(VIEW3D_PT_transmogrify_scene)
        bpy.utils.unregister_class(VIEW3D_PT_transmogrify_optimize_files)
        bpy.utils.unregister_class(VIEW3D_PT_transmogrify_archive)
        bpy.utils.unregister_class(VIEW3D_PT_transmogrify_scripts)