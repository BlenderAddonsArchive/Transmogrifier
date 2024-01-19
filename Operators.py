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
    Operator, 
) 
import os
import subprocess
import shutil
from pathlib import Path
import json
from . import Functions



#     ███████    ███████████  ██████████ ███████████     █████████   ███████████    ███████    ███████████    █████████ 
#   ███░░░░░███ ░░███░░░░░███░░███░░░░░█░░███░░░░░███   ███░░░░░███ ░█░░░███░░░█  ███░░░░░███ ░░███░░░░░███  ███░░░░░███
#  ███     ░░███ ░███    ░███ ░███  █ ░  ░███    ░███  ░███    ░███ ░   ░███  ░  ███     ░░███ ░███    ░███ ░███    ░░░ 
# ░███      ░███ ░██████████  ░██████    ░██████████   ░███████████     ░███    ░███      ░███ ░██████████  ░░█████████ 
# ░███      ░███ ░███░░░░░░   ░███░░█    ░███░░░░░███  ░███░░░░░███     ░███    ░███      ░███ ░███░░░░░███  ░░░░░░░░███
# ░░███     ███  ░███         ░███ ░   █ ░███    ░███  ░███    ░███     ░███    ░░███     ███  ░███    ░███  ███    ░███
#  ░░░███████░   █████        ██████████ █████   █████ █████   █████    █████    ░░░███████░   █████   █████░░█████████ 
#    ░░░░░░░    ░░░░░        ░░░░░░░░░░ ░░░░░   ░░░░░ ░░░░░   ░░░░░    ░░░░░       ░░░░░░░    ░░░░░   ░░░░░  ░░░░░░░░░  

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
            self.report({'ERROR'}, (f"{Path(directory).name} directory doesn't exist"))
            return False
        return True


    def execute(self, context):
        settings = bpy.context.scene.TransmogrifierSettings

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
            converter_report_dict = Functions.read_json()
            conversion_count = converter_report_dict["conversion_count"]
            if conversion_count > 1:
                self.report({'INFO'}, f"Conversion complete. {conversion_count} files were converted.")
            elif conversion_count == 1:
                self.report({'INFO'}, f"Conversion complete. {conversion_count} file was converted.")
            else:
                self.report({'INFO'}, f"Could not convert or no items needed conversion. {conversion_count} files were converted.")

        return {'FINISHED'}


    def select_children_recursive(self, obj, context):
        for c in obj.children:
            if obj.type in context.scene.transmogrifier.texture_resolution_include:
                c.select_set(True)
            self.select_children_recursive(c, context)


    def export_selection(self, context, base_dir):
        settings = bpy.context.scene.TransmogrifierSettings

        # Create variables_dict dictionary from TransmogrifierSettings to pass to write_json function later.
        variables_dict = Functions.get_transmogrifier_settings(self, context)

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
            options = Functions.load_operator_preset(
                'wm.collada_import', settings.import_dae_preset)
            #bpy.ops.wm.collada_import(**options)
            import_file_command = "bpy.ops.wm.collada_import(**"
            
        elif settings.import_file == "ABC":
            options = Functions.load_operator_preset(
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
            options = Functions.load_operator_preset(
                'wm.usd_import', settings.import_usd_preset)
            import_file_command = "bpy.ops.wm.usd_import(**"

        elif settings.import_file == "OBJ":
            options = Functions.load_operator_preset(
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
            options = Functions.load_operator_preset(
                'import_scene.fbx', settings.import_fbx_preset)
            import_file_command = "bpy.ops.import_scene.fbx(**"

        elif settings.import_file == "glTF":
            options = {
                'filepath': '',
            }
            import_file_command = "bpy.ops.import_scene.gltf(**"

        elif settings.import_file == "X3D":
            options = Functions.load_operator_preset(
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
            options = Functions.load_operator_preset(
                'wm.collada_export', settings.dae_preset)
            options["filepath"] = "export_file_1"
            options["selected"] = True
            #bpy.ops.wm.collada_export(**options)
            export_file_1_command = "bpy.ops.wm.collada_export(**"
            
        elif settings.export_file_1 == "ABC":
            options = Functions.load_operator_preset(
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
            options = Functions.load_operator_preset(
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
            options = Functions.load_operator_preset(
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
            options = Functions.load_operator_preset(
                'export_scene.fbx', settings.fbx_preset)
            options["filepath"] = "export_file_1"
            options["use_selection"] = True
            #bpy.ops.export_scene.fbx(**options)
            export_file_1_command = "bpy.ops.export_scene.fbx(**"

        elif settings.export_file_1 == "glTF":
            options = Functions.load_operator_preset(
                'export_scene.gltf', settings.gltf_preset)
            options["filepath"] = "export_file_1"
            options["use_selection"] = True
            #bpy.ops.export_scene.gltf(**options)
            export_file_1_command = "bpy.ops.export_scene.gltf(**" 

        elif settings.export_file_1 == "X3D":
            options = Functions.load_operator_preset(
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
            options = Functions.load_operator_preset(
                'wm.collada_export', settings.dae_preset)
            options["filepath"] = "export_file_2"
            options["selected"] = True
            #bpy.ops.wm.collada_export(**options)
            export_file_2_command = "bpy.ops.wm.collada_export(**"
            
        elif settings.export_file_2 == "ABC":
            options = Functions.load_operator_preset(
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
            options = Functions.load_operator_preset(
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
            options = Functions.load_operator_preset(
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
            options = Functions.load_operator_preset(
                'export_scene.fbx', settings.fbx_preset)
            options["filepath"] = "export_file_2"
            options["use_selection"] = True
            #bpy.ops.export_scene.fbx(**options)
            export_file_2_command = "bpy.ops.export_scene.fbx(**"

        elif settings.export_file_2 == "glTF":
            options = Functions.load_operator_preset(
                'export_scene.gltf', settings.gltf_preset)
            options["filepath"] = "export_file_2"
            options["use_selection"] = True
            #bpy.ops.export_scene.gltf(**options)
            export_file_2_command = "bpy.ops.export_scene.gltf(**"

        elif settings.export_file_2 == "X3D":
            options = Functions.load_operator_preset(
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
        Functions.write_json(variables_dict, json_file)

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


# Copy import/export/transmogrifier presets shipped with Transmogrifier to relevant Blender Preferences directory.
class COPY_ASSETS(Operator):
    """Copy example presets shipped with Transmogrifier to User Preferences"""
    bl_idname = "copyassets.transmogrifier"
    bl_label = "Copy Assets to Preferences"

    def execute(self, context):
        # Define paths.
        assets_dir = Path(__file__).parent / "assets"
        presets_dir_src = assets_dir / "presets" / "operator"
        presets_dir_dest = bpy.utils.user_resource('SCRIPTS', path="presets/operator")

        # Make list of source paths and destination paths (parents).
        dir_src_list = [presets_dir_src]
        dir_dest_list = [presets_dir_dest]
        
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


class ADD_TRANSMOGRIFIER_PRESET(Operator):
    """Creates a Transmogrifier preset from current settings"""
    bl_idname = "transmogrifierpreset.add"
    bl_label = "Add Preset"

    preset_name: bpy.props.StringProperty(name="Name", default="")

    def execute(self, context):
        
        variables_dict = Functions.get_transmogrifier_settings(self, context)
        add_preset_name = self.preset_name + ".json"
        json_file = Path(bpy.utils.script_paths(subdir="presets/operator/transmogrifier")[0]) / add_preset_name
        Functions.write_json(variables_dict, json_file)

        return {'FINISHED'}
    
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=200)
    

class REMOVE_TRANSMOGRIFIER_PRESET(Operator):
    """Removes currently selected Transmogrifier preset"""
    bl_idname = "transmogrifierpreset.remove"
    bl_label = "Remove Preset"

    def execute(self, context):
        
        settings = bpy.context.scene.TransmogrifierSettings
        remove_preset_name = settings.transmogrifier_preset_enum + ".json"
        json_file = Path(bpy.utils.script_paths(subdir="presets/operator/transmogrifier")[0]) / remove_preset_name

        if remove_preset_name != "NO_PRESET":
            Path.unlink(json_file)

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
    TRANSMOGRIFY,
    COPY_ASSETS,
    ADD_TRANSMOGRIFIER_PRESET,
    REMOVE_TRANSMOGRIFIER_PRESET,
)

# Register Classes.
def register():
    for cls in classes:
        bpy.utils.register_class(cls)

# Unregister Classes.
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)