
import bpy

from ..operators.AddonOperators import ChangeLanguage, ChangeHammerUnit,AddOutline, ExportModel
from ....common.types.framework import reg_order
from ..config import __addon_name__

class BasePanel(object):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Source 2"

    @classmethod
    def poll(cls, context: bpy.types.Context):
        return True


@reg_order(0)
class ExampleAddonPanel(BasePanel, bpy.types.Panel):
    bl_label = "Source 2 工具"
    bl_idname = "SCENE_PT_sample"

    def draw(self, context: bpy.types.Context):
        layout = self.layout
        layout.operator(ChangeHammerUnit.bl_idname)
        layout.operator(AddOutline.bl_idname)

    @classmethod
    def poll(cls, context: bpy.types.Context):
        return True

@reg_order(2)
class ExportPanel(BasePanel, bpy.types.Panel):
    bl_label = "导出工具"
    bl_idname = "SCENE_PT_sample1"

    def draw(self, context: bpy.types.Context):
        savepath = context.preferences.addons[__addon_name__].preferences
        layout = self.layout
        layout.label(text="导出到 Hammer")
        layout.prop(savepath, "filepath",text="保存路径")
        layout.separator()
        layout.operator(ExportModel.bl_idname)

    @classmethod
    def poll(cls, context: bpy.types.Context):
        return True


@reg_order(2)
class ExampleAddonPanel2(BasePanel, bpy.types.Panel):
    bl_label = "其他工具"
    bl_idname = "SCENE_PT_sample2"

    def draw(self, context: bpy.types.Context):

        layout = self.layout
        layout.operator(ChangeLanguage.bl_idname)

    @classmethod
    def poll(cls, context: bpy.types.Context):
        return True
