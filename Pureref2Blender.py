bl_info = {
    "name": "Paste PureRef Images",
    "blender": (2, 80, 0),
    "category": "Image",
}

import bpy
import os
import tempfile
import subprocess
import sys

def ensure_pillow():
    try:
        import PIL
    except ImportError:
        # Attempt to install Pillow
        try:
            import ensurepip
            ensurepip.bootstrap()
            subprocess.check_call([sys.executable, "-m", "pip", "install", "Pillow"])
        except Exception as e:
            print(f"Failed to install Pillow: {e}")

ensure_pillow()
from PIL import ImageGrab, Image

class PastePureRefImageOperator(bpy.types.Operator):
    """Paste Image from Clipboard"""
    bl_idname = "image.paste_pureref_image"
    bl_label = "Paste PureRef Image"

    @classmethod
    def poll(cls, context):
        return context.area.type == 'VIEW_3D'

    def execute(self, context):
        try:
            # Grab the image from the clipboard
            image = ImageGrab.grabclipboard()
            
            # Check if the clipboard content is an image
            if isinstance(image, Image.Image):
                # Save the image to a temporary file
                temp_dir = tempfile.gettempdir()
                temp_path = os.path.join(temp_dir, "clipboard_image.png")
                image.save(temp_path)
                
                # Load the image in Blender
                img = bpy.data.images.load(temp_path)
                
                # Create a new empty object and set it as an image empty
                ref = bpy.data.objects.new(name=img.name, object_data=None)
                ref.empty_display_type = 'IMAGE'
                ref.data = img
                ref.location = context.scene.cursor.location
                
                # Link the new empty to the current collection
                context.collection.objects.link(ref)

                self.report({'INFO'}, "Image pasted from clipboard")
            else:
                self.report({'WARNING'}, "No image in clipboard")
        except Exception as e:
            self.report({'ERROR'}, str(e))
        
        return {'FINISHED'}

def menu_func(self, context):
    self.layout.operator(PastePureRefImageOperator.bl_idname)

def register():
    bpy.utils.register_class(PastePureRefImageOperator)
    bpy.types.VIEW3D_MT_add.append(menu_func)

def unregister():
    bpy.utils.unregister_class(PastePureRefImageOperator)
    bpy.types.VIEW3D_MT_add.remove(menu_func)

if __name__ == "__main__":
    register()
