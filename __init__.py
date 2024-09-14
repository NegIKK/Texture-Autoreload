bl_info = {
    "name": "Texture AutoReloader",
    "author": "Daniel Matus and mr.AI",
    "version": (0, 1, 1),
    "blender": (4, 2, 0),
    "category": "Object",
    "description": "Automatically reloads all textures in the project at regular intervals.",
}



import bpy

def reload_textures():
    """Reload all file-based textures in the project"""
    for image in bpy.data.images:
        if image.source == 'FILE':
            image.reload()
    print("All textures reloaded!")

def texture_reloader_timer():
    """Timer function for periodic texture reloading"""
    preferences = bpy.context.scene.auto_texture_reloader

    # Проверяем, включена ли автоподгрузка
    if preferences.enable_autoreload:
        reload_textures()
        return preferences.reload_interval  # Продолжаем запускать таймер с указанным интервалом
    else:
        return None  # Остановить таймер

class AutoTextureReloaderProperties(bpy.types.PropertyGroup):
    enable_autoreload: bpy.props.BoolProperty(
        name="Enable Auto Reload",
        description="Automatically reload textures at the specified interval",
        default=False,
        update=lambda self, context: self.update_timer(context)
    )

    reload_interval: bpy.props.FloatProperty(
        name="Reload Interval (seconds)",
        description="Time interval in seconds between texture reloads",
        default=15.0,
        min=1.0
    )

    def update_timer(self, context):
        if self.enable_autoreload:
            bpy.app.timers.register(texture_reloader_timer, first_interval=self.reload_interval)
        else:
            try:
                bpy.app.timers.unregister(texture_reloader_timer)
            except ValueError:
                pass  # Таймер не был зарегистрирован

class WM_OT_toggle_texture_reloader(bpy.types.Operator):
    bl_idname = "wm.toggle_texture_reloader"
    bl_label = "Toggle Texture Reloader"

    def execute(self, context):
        props = context.scene.auto_texture_reloader
        props.enable_autoreload = not props.enable_autoreload
        if props.enable_autoreload:
            bpy.app.timers.register(texture_reloader_timer, first_interval=props.reload_interval)
        else:
            try:
                bpy.app.timers.unregister(texture_reloader_timer)
            except ValueError:
                pass  # Таймер не был зарегистрирован
        return {'FINISHED'}

class TOPBAR_MT_texture_reloader_menu(bpy.types.Menu):
    bl_label = "Texture Reloader"
    bl_idname = "TOPBAR_MT_texture_reloader_menu"

    def draw(self, context):
        layout = self.layout
        props = context.scene.auto_texture_reloader
        layout.prop(props, "enable_autoreload", text="Auto Reload")
        if props.enable_autoreload:
            layout.prop(props, "reload_interval", text="Interval")

def draw_func(self, context):
    self.layout.menu(TOPBAR_MT_texture_reloader_menu.bl_idname)

def add_menu(self, context):
    self.layout.separator()  # Добавляем разделитель перед нашим меню
    self.layout.menu(TOPBAR_MT_texture_reloader_menu.bl_idname)

def register():
    bpy.utils.register_class(AutoTextureReloaderProperties)
    bpy.types.Scene.auto_texture_reloader = bpy.props.PointerProperty(type=AutoTextureReloaderProperties)
    
    bpy.utils.register_class(WM_OT_toggle_texture_reloader)
    bpy.utils.register_class(TOPBAR_MT_texture_reloader_menu)
    
    # Добавляем меню в верхнюю панель
    bpy.types.TOPBAR_MT_editor_menus.append(add_menu)

def unregister():
    bpy.utils.unregister_class(WM_OT_toggle_texture_reloader)
    bpy.utils.unregister_class(TOPBAR_MT_texture_reloader_menu)
    
    # Удаляем меню из верхней панели
    bpy.types.TOPBAR_MT_editor_menus.remove(add_menu)

    del bpy.types.Scene.auto_texture_reloader
    
    # Удаляем таймер, если он зарегистрирован
    try:
        bpy.app.timers.unregister(texture_reloader_timer)
    except ValueError:
        pass

if __name__ == "__main__":
    register()