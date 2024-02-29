## Usage 🏭

1. **Select a directory** containing 3D files of the chosen **import format**, or a parent directory of arbitrary organization and/or depth as long as there exists at least one 3D file of the specified import format somewhere inside.  Try out the [Demo](#demo-) 🧪 below to get started.

<img src="https://github.com/SapwoodStudio/Transmogrifier/assets/87623407/9e977a7f-57d7-4659-a5eb-df903e837e79" width="250">

<img src="https://github.com/SapwoodStudio/Transmogrifier/assets/87623407/e3dc4110-ff04-4297-8698-18a1ce5a358f" width="600">


2. **Select an output directory** to which 3D files of the chosen **export format(s)** should be exported. "Adjacents" means that converted models will be saved to the same directories from which they were imported. "Custom" means that converted models will be saved to a chosen custom directory.

<img src="https://github.com/SapwoodStudio/Transmogrifier/assets/87623407/116d5ace-0772-48ac-9f2e-c68195019591" width="250">

<img src="https://github.com/SapwoodStudio/Transmogrifier/assets/87623407/cb6dbc9e-1eee-4b79-a3f5-bd3866f4b2ad" width="250">

<img src="https://github.com/SapwoodStudio/Transmogrifier/assets/87623407/f5c54398-b248-4cae-9ddd-e57511750e00" width="250">


3. **Set additional export settings** as described in the [Features](#features-) section below. (_Optional: to save current settings for later use, save the current .blend file_)

<img src="https://github.com/SapwoodStudio/Transmogrifier/assets/87623407/248c5c34-1100-4822-a285-6e11571ebdd2" width="250">


4. **Click "Batch Convert"**. This will spawn another instance of Blender. The new Blender window will remain grey while the conversion process gets output to the console window. The original Blender window will remain frozen/unresponsive until the batch conversion is complete. This is normal operation. After the conversion finishes, the greyed-out Blender window will disappear and the original Blender instance will report how many files were converted.  If you wish to see the conversion process get logged in real-time, you must start Blender from your terminal/Command Line first before Transmogrifying.

<img src="https://github.com/SapwoodStudio/Transmogrifier/assets/87623407/02bf64ab-3675-4175-bcba-0af212ec97f3" width="250">

(Ubuntu Example)

<img src="https://github.com/SapwoodStudio/Transmogrifier/assets/87623407/1ebf7242-368f-4199-aaef-8ce7fe1ca05a" width="600">

(Windows Example)

<img src="https://github.com/SapwoodStudio/Transmogrifier/assets/87623407/053903c1-5167-488e-86e4-a5c65a7aa6ad" width="600">

<img src="https://github.com/SapwoodStudio/Transmogrifier/assets/87623407/90cc4699-137c-4c69-bf8d-dd887d2cae61" width="350">



## Features ✨
Transmogrifier includes a robust set of tools for non-destructively converting 3D files and associated textures into other formats.

### User Interface
Toggle between a simple and advanced Transmogrifier user interface.

<img src="https://github.com/SapwoodStudio/Transmogrifier/assets/87623407/f2189142-ecd1-4f21-9ab8-c248366701cf" width="350">


### Workflow
Create custom Transmogrifier presets (aka "Workflows) for quickly switching between different conversion scenarios. Click the plus button "+" to create a Workflow from all of the current Transmogrifier settings, giving it a custom name. Workflows are stored as "operator presets" in Blender preferences directory. To remove a workflow, select it from the menu, then click the minus button "-". 

<img src="https://github.com/SapwoodStudio/Transmogrifier/assets/87623407/4bc129b8-f3e3-42c2-9a0a-e9075614645d" width="350">

<img src="https://github.com/SapwoodStudio/Transmogrifier/assets/87623407/c4feafda-0e2d-4a39-a828-fc8ad9ed16cf" width="350">


### 3D Formats
- FBX
- OBJ
- glTF/GLB
- STL
- PLY
- X3D
- DAE
- ABC
- USD/USDA/USDC/USDZ
- BLEND

<img src="https://github.com/SapwoodStudio/Transmogrifier/assets/87623407/f62105a2-753b-4941-8b85-0e8dfdae1995" width="350">


### Import/Export Presets
Set user-defined import and export presets.

<img src="https://github.com/SapwoodStudio/Transmogrifier/assets/87623407/4b47db1d-2a2c-4ff3-8d6c-dbfcef1ff03a" width="350">


### Import Location
Select a directory containing 3D files of the chosen import format, or a parent directory of arbitrary organization and/or depth as long as there exists at least one 3D file of the specified import format somewhere inside.

<img src="https://github.com/SapwoodStudio/Transmogrifier/assets/87623407/59cc7cd1-a190-44d3-93c5-14b4be71d011" width="350">


### Export Location
Set the export location to either "Adjacent" or "Custom". "Adjacents" means that converted models will be saved to the same directories from which they were imported. "Custom" means that converted models will be saved to a chosen custom directory. Choose whether to place converted models in subdirectories of their same names. If so, choose whether to copy original files from import directories to respective subdirectories.

<img src="https://github.com/SapwoodStudio/Transmogrifier/assets/87623407/af484984-c556-4238-875a-6cff2e9fb455" width="350">

<img src="https://github.com/SapwoodStudio/Transmogrifier/assets/87623407/9d0c3d9d-ab4e-4e84-bdbf-6066c3d24b35" width="350">


### Name
Set a custom prefix and/or suffix for every exported file. Synchronize object names and object data names according to the former.

<img src="https://github.com/SapwoodStudio/Transmogrifier/assets/87623407/bc0f4688-ee44-4811-81af-6ac891aebd58" width="350">


### Textures

Transmogrifier can detect the presence of multiple image texture sets and non-destructively modify them during the conversion process. Select whether to use textures, regex the PBR tags in the textures' names, and keep the otherwise temporary textures folders with their modifications.

#### Source:
- **External**: image textures nearby the imported model. 
    - in a "textures" subfolder
    - in "[texture set]" subfolders inside a "textures" subfolder
    - in the same directory as the imported 3D file
- **Packed**: image textures packed into the imported file (e.g. GLB or USDZ)
- **Custom**: image textures from a custom directory, which will be applied to all models converted.

<img src="https://github.com/SapwoodStudio/Transmogrifier/assets/87623407/aba24831-c3fb-459d-990d-846e3870e46b" width="350">
<img src="https://github.com/SapwoodStudio/Transmogrifier/assets/87623407/ff6a4355-1888-413b-940e-67d1a06c9aaf" width="350">

<img src="https://github.com/SapwoodStudio/Transmogrifier/assets/87623407/c261ea84-65ba-4c2c-89b2-02e7ca65629b" width="700">

_Models from [Polyhaven](https://polyhaven.com/models) ([CC0](https://creativecommons.org/share-your-work/public-domain/cc0/)). The scenarios shown depend on whether the selected import or export formats support textures. Each gray box with rounded corners indicates a directory/folder._

#### 3 Texturing Rules

There are three naming conventions that must be followed in order for textures to be properly imported, materials created, and materials assigned to the right objects.
1. **Transparent pieces have "transparent" in name and are separate objects.** Objects that should appear transparent must have the word "transparent" present somewhere in their names. This indicates to Transmogrifier that it should duplicate the material as "[material]_transparent" and turn on "Alpha Blend" blending mode, then assign "[material]" to the opaque objects and "[material]_transparent" to the transparent objects. This convention works for multiple texture sets as well.

<img src="https://github.com/SapwoodStudio/Transmogrifier/assets/87623407/78ae1583-a459-432b-9779-33ddbf73069e" width="700">

2. **Per item, if only 1 texture set is present, object names don't matter except for Rule 1.** For "External" and "Custom" texture sources and for models with only one texture set present, the first rule doesn't matter because it is assumed that that texture set should be applied to all the objects in the scene. 

<img src="https://github.com/SapwoodStudio/Transmogrifier/assets/87623407/4393055d-da1f-4787-a704-56ac2827df1e" width="700">

3. **Per item, if >1 texture set is present and textures source is either "External" or "Custom", object and textures set names do matter: an object's name must include its corresponding texture set name somewhere in the object's name.** For models with more than one texture set present, a **texture set** naming convention must also be followed for Transmogrifier to correctly import and assign multiple texture sets to the proper objects. Simply ensure that the the **first word** before an underscore or another separator in the textures' names is 1) **distinct** between texture sets and 2) **consistent** between i.) each PBR image in each texture set and ii.) between the texture sets and the objects to which those textures should be applied (See image below). As such, having multiple materials assigned to different meshes within an object is not possible. For "Packed" textures source, Transmogrifier automatically keeps associated materials, textures, and objects synchronized. 

<img src="https://github.com/SapwoodStudio/Transmogrifier/assets/87623407/7ec4a257-442b-4e0c-8aaf-60e152d4e9fe" width="700">


#### Resolution:
Resize textures and filter what to include by PBR type. Images will not be upscaled.

- 8192
- 4096
- 2048
- 1024
- 512
- 256
- 128

<img src="https://github.com/SapwoodStudio/Transmogrifier/assets/87623407/b6f7aa82-c207-42c6-bda0-0588fcf81e1d" width="350">

<img src="https://github.com/SapwoodStudio/Transmogrifier/assets/87623407/8e566708-0a43-453f-9a2c-8945c1d52a7e" width="350">


#### Format: 
Reformat textures and filter what to include by PBR type.

- PNG
- JPEG (.jpg)
- TARGA
- TIFF
- WEBP
- BMP
- OPEN_EXR

<img src="https://github.com/SapwoodStudio/Transmogrifier/assets/87623407/5d2522cb-2b95-43ea-bd86-d713d70a42b1" width="350">

<img src="https://github.com/SapwoodStudio/Transmogrifier/assets/87623407/53de71c5-ceaf-4430-8bdd-fc1cb2a5cb70" width="350">


### UVs
#### Rename UV Maps
Rename all UV maps for all objects converted with a custom name.  This is important for USD, where objects sharing the same material evidently need to share the same UV map name as well.  If an object has more than one UV map, a numerical incrementer suffix will be applied to each UV map (e.g. "UVMap_1", "UVMap_2", etc.).

<img src="https://github.com/SapwoodStudio/Transmogrifier/assets/87623407/02ef204d-02b7-4242-ab41-6f68732bf13e" width="350">


#### Export UV Maps
Export UVs with the same options available via the UV Editor and more.

<img src="https://github.com/SapwoodStudio/Transmogrifier/assets/87623407/186eed7c-1d03-4d65-988f-3d6aba34357e" width="350">


Set a location for UV's to be exported into:

<img src="https://github.com/SapwoodStudio/Transmogrifier/assets/87623407/c2df1cfe-4463-4ab1-8371-3933aa37a531" width="350">


Set how UVs should be combined for export:

<img src="https://github.com/SapwoodStudio/Transmogrifier/assets/87623407/0541a1c9-f0e4-4551-a04c-88f875237321" width="350">



### Transformations
Perform custom transformations and/or apply transformations to every model before export. Filter what transformations to set/apply.

<img src="https://github.com/SapwoodStudio/Transmogrifier/assets/87623407/f44b1325-5415-45a8-a302-3f668608ef4b" width="350">


### Animations
Delete animations of every imported object before export. 

<img src="https://github.com/SapwoodStudio/Transmogrifier/assets/87623407/09d58e75-8c56-49c5-b6ee-6e8890e2cf8e" width="350">


### Scene
Set a custom unit system and length unit for export.

<img src="https://github.com/SapwoodStudio/Transmogrifier/assets/87623407/273edb83-792e-4cef-9a88-b6dec3b6fda1" width="350">


### Optimize
Perform automatic file-optmization methods to every model in order reduce the exported file size below a custom target maximum. Filter which methods are used. If all methods are exhausted and the file size is still above the target maximum, Transmogrifier will report this in the log and move on.

File Included:
- All (Always export despite any pre-existing file that is already below the target file size.)
- Only Above Max (Only export and resize files that are above the target file sizes. Pre-existing files already below the target are ignored.)
- None (Don't auto-resize at all.)

<img src="https://github.com/SapwoodStudio/Transmogrifier/assets/87623407/1261bf79-2aeb-40a6-b789-9e4e5309c0ba" width="350">


Methods:
- Draco compression (Only works for GLB/glTF.)
- Resize textures (Set a minimum resolution limit.)
- Reformat textures (Convert all textures to JPG except normal maps.)
- Decimate mesh objects (Uses edge collapse at 50% ratio each time. Set a maximum decimate iteration.)

<img src="https://github.com/SapwoodStudio/Transmogrifier/assets/87623407/052d2b6c-ffa3-4f42-b798-eb6d59e84f82" width="350">


### Archive
Mark assets, add metadata, store asset Blend files in a library and catalog, and extract asset previews as PNGs. Save a log of the conversion process to troubleshoot errors or simply to get a list of the output files and their file sizes.

<img src="https://github.com/SapwoodStudio/Transmogrifier/assets/87623407/23f21a0f-4f87-4000-9cba-13ad0ca3dbee" width="350">

#### Archive Assets
- **Mark Assets**
    - Actions
    - Collections
    - Materials
    - Node Trees
    - Objects
    - Worlds
- **Ignore Duplicate Assets**. Transmogrifier will avoid marking assets that already exist in the selected asset library per asset-type.
- **Save Previews to Disk**. Extract generated asset previews as PNGs beside the Blend containing assets.  Cannot save previews for asset types that have not been marked.
- **Asset Library**. Select an asset library to 1) get catalogs and 2) move/copy the Blend containing assets to that library.
    - Asset Libraries must first be created/set up via Blender Preferences and Blender must be restarted before Transmogrifying.

<img src="https://github.com/SapwoodStudio/Transmogrifier/assets/87623407/ee83d391-a9eb-46dc-a18d-9558a24d7abc" width="350">

- **Catalog**. Select from the available catalogs in a given asset library.
    - Asset Catalogs must first be created/set up in the usual manner (e.g. From a current Blender session - marking assets, creating categories in the current file, saving the Blend with inside the asset library directory. If the Blend is deleted, asset categories will still be preserved).
- **Blend Location**
    - Move to Library
    - Copy to Library
    - Don't Move/Copy. Useful when Transmogrifying inside of an asset library.
- **Pack Resources**. Pack textures and other linked data into asset Blend. If unchecked, the asset Blend will reference textures from an adjacent textures folder.
- **Add Metadata**. The input metadata will be applied to all items converted.
    - Description
    - License
    - Copyright
    - Author
    - Tags.  Separate multiple tags with a space. (e.g. "grunge worn ancient")