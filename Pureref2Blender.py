bl_info = {
    "name": "Paste PureRef Images",
    "blender": (2, 80, 0),
    "category": "Image",
    "author": "Martin Fir, Tine Maher, The Wall",
    "description": "Paste images from clipboard or local files into Blender. Supports jpg, png, avif, heic, webp, gif formats.",
    "version": (1, 0, 0),
}

import bpy
import os
import tempfile
import subprocess
import sys

class InstallPillowOperator(bpy.types.Operator):
    """Install Pillow"""
    bl_idname = "preferences.install_pillow"
    bl_label = "Install Pillow"

    def execute(self, context):
        try:
            import ensurepip
            ensurepip.bootstrap()
            subprocess.check_call([sys.executable, "-m", "pip", "install", "Pillow"])
            self.report({'INFO'}, "Pillow installed successfully. Please restart Blender.")
        except Exception as e:
            self.report({'ERROR'}, f"Failed to install Pillow: {e}")
        return {'FINISHED'}

def ensure_pillow():
    try:
        import PIL
        return True
    except ImportError:
        return False

class PastePureRefImageOperator(bpy.types.Operator):
    """Paste Image from Clipboard"""
    bl_idname = "image.paste_pureref_image"
    bl_label = "Paste PureRef Image"
    bl_icon = 'IMAGE_DATA'

    @classmethod
    def poll(cls, context):
        return context.area.type == 'VIEW_3D'

    def execute(self, context):
        try:
            from PIL import ImageGrab, Image
            image = ImageGrab.grabclipboard()
            if isinstance(image, Image.Image):
                temp_dir = tempfile.gettempdir()
                temp_path = os.path.join(temp_dir, "clipboard_image.png")
                image.save(temp_path)
                
                img = bpy.data.images.load(temp_path)
                
                # Calculate position for new image
                x_offset = 0
                y_offset = 0
                count = 0
                padding = 1.0  # 1 meter padding
                
                for obj in context.collection.objects:
                    if obj.type == 'EMPTY' and obj.empty_display_type == 'IMAGE':
                        x_offset += obj.dimensions.x + padding  # Add padding
                        
                        # Start a new row after 7 images
                        if count % 7 == 6:
                            y_offset -= obj.dimensions.y + padding  # Vertical spacing between rows
                            x_offset = 0
                        
                        count += 1

                ref = bpy.data.objects.new(name=img.name, object_data=None)
                ref.empty_display_type = 'IMAGE'
                ref.data = img
                ref.location = (x_offset, y_offset, 0)  # Adjust Y and Z as needed
                context.collection.objects.link(ref)

                self.report({'INFO'}, "Image pasted from clipboard")
            else:
                self.report({'WARNING'}, "No image in clipboard")
        except ImportError:
            self.report({'ERROR'}, "Pillow is not installed. Please install Pillow from the add-on preferences and restart Blender.")
        except Exception as e:
            self.report({'ERROR'}, str(e))
        
        return {'FINISHED'}

class PasterefPreferences(bpy.types.AddonPreferences):
    bl_idname = __name__

    def draw(self, context):
        layout = self.layout
        if not ensure_pillow():
            layout.operator(InstallPillowOperator.bl_idname, text="Install Pillow")
            layout.label(text="Please restart Blender after installation.", icon='INFO')

def menu_func(self, context):
    self.layout.operator(PastePureRefImageOperator.bl_idname, icon='IMAGE_DATA')

def register():
    bpy.utils.register_class(InstallPillowOperator)
    bpy.utils.register_class(PastePureRefImageOperator)
    bpy.utils.register_class(PasterefPreferences)
    bpy.types.VIEW3D_MT_add.append(menu_func)

def unregister():
    bpy.utils.unregister_class(InstallPillowOperator)
    bpy.utils.unregister_class(PastePureRefImageOperator)
    bpy.utils.unregister_class(PasterefPreferences)
    bpy.types.VIEW3D_MT_add.remove(menu_func)

if __name__ == "__main__":
    register()
