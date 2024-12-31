
import os
import re
import bpy
import keyvalues3 as kv3
from ..config import __addon_name__
from ..preference.AddonPreferences import ExampleAddonPreferences

#切换界面语言
class ChangeLanguage(bpy.types.Operator):
    '''切换界面语言'''
    bl_idname = "object.change_language"
    bl_label = "Change Language"

    # 确保在操作之前备份数据，用户撤销操作时可以恢复
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context: bpy.types.Context):
        return True

    def execute(self, context: bpy.types.Context):
        addon_prefs = bpy.context.preferences.addons[__addon_name__].preferences
        assert isinstance(addon_prefs, ExampleAddonPreferences)
        # 切换语言
        prefs = bpy.context.preferences.view
        if prefs.language == 'zh_CN':
            prefs.language = 'en_US'
        else:
            prefs.language = 'zh_CN'
        prefs.use_translate_interface = True
        bpy.ops.wm.save_userpref()
        return {'FINISHED'}
#将物体尺寸从米转为英寸
class ChangeHammerUnit(bpy.types.Operator):
    '''将单位米转为英寸大小'''
    bl_idname = "object.change_hammer_unit"
    bl_label = "Change Hammer Unit"

    # 确保在操作之前备份数据，用户撤销操作时可以恢复
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context: bpy.types.Context):
        return len(context.selected_objects) > 0
        #将物体尺寸从米转为英寸

    def execute(self, context: bpy.types.Context):
        # 执行操作
        bpy.context.active_object.scale /= 39.3700787
        return {'FINISHED'}
#一键添加描边
class AddOutline(bpy.types.Operator):
    '''一键添加描边'''
    bl_idname = "object.add_outline"
    bl_label = "Add Outline"

    # 确保在操作之前备份数据，用户撤销操作时可以恢复
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context: bpy.types.Context):
        return len(context.selected_objects) > 0

    def execute(self, context: bpy.types.Context):
        # 添加实体化修改器
        bpy.ops.object.modifier_add(type='SOLIDIFY')
        modifier = bpy.context.object.modifiers["实体化"]
        modifier.thickness = 0.05
        modifier.use_flip_normals = True
        modifier.use_quality_normals = True
        modifier.material_offset = 1
        modifier.use_rim = True
        obj = context.active_object
        # 添加一个新的材质槽
        bpy.ops.object.material_slot_add()

        # Create a new material
        black_material = bpy.data.materials.new(name="OutLine")
        black_material.use_nodes = True

        #将材质赋予材质槽
        obj.material_slots[1].material = black_material
        bpy.context.object.active_material.use_backface_culling = True
        return {'FINISHED'}
#导出模型和材质
class ExportModel(bpy.types.Operator):
    '''导出模型和材质'''
    bl_idname = "object.export_model"
    bl_label = "Export Model"

    # 确保在操作之前备份数据，用户撤销操作时可以恢复
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context: bpy.types.Context):
        return len(context.selected_objects) > 0

    def execute(self, context: bpy.types.Context):
        # 执行操作
        addon_prefs = context.preferences.addons[__addon_name__].preferences
        # 获取选中的物体
        selected_objects = bpy.context.selected_objects
        # 获取选中物体的名称
        select_name = selected_objects[0].name
        # 获取导出路径
        directory = os.path.join(addon_prefs.filepath, select_name)
        #记录材质名称
        material_name = selected_objects[0].material_slots[0].name
        #导出FBX文件
        self.export_fbx(selected_objects[0], directory)
        #导出PBR材质贴图
        self.export_pbr_textures(selected_objects[0], directory)
        # 导出VMAT文件
        self.export_vmat(select_name, directory,selected_objects[0])
        #导出VMDL文件
        self.export_vmdl(select_name, directory,selected_objects[0])
        # 提示用户导出成功
        self.report({'INFO'}, f"Exported to {directory}")
        return {'FINISHED'}

    #导出PBR材质贴图
    def export_pbr_textures(self,obj, export_dir):
        if not os.path.exists(export_dir):
            os.makedirs(export_dir)
        for mat_slot in obj.material_slots:
            mat = mat_slot.material
            if mat and mat.use_nodes:
                for node in mat.node_tree.nodes:
                # 查找图像纹理节点
                    if node.type == 'TEX_IMAGE':
                        image = node.image
                        if image:
                            # 导出漫反射贴图
                            if "Base Color" in node.label:
                                image_path = os.path.join(export_dir, "texture", f"{mat.name}_diffuse.png")
                                image.filepath_raw = image_path
                                image.file_format = 'PNG'
                                image.save()
                            # 导出法线贴图
                            if "Normal" in node.label:
                                normal_path = os.path.join(export_dir, "texture", f"{mat.name}_normal.png")
                                image.filepath_raw = normal_path
                                image.file_format = 'PNG'
                                image.save()
                            # 导出粗糙度贴图
                            if "Roughness" in node.label:
                                roughness_path = os.path.join(export_dir, "texture", f"{mat.name}_roughness.png")
                                image.filepath_raw = roughness_path
                                image.file_format = 'PNG'
                                image.save()
                            # 导出金属度贴图
                            if "Metallic" in node.label:
                                metallic_path = os.path.join(export_dir, "texture", f"{mat.name}_metallic.png")
                                image.filepath_raw = metallic_path
                                image.file_format = 'PNG'
                                image.save()
                            # 导出透明度贴图
                            if "Opacity" in node.label:
                                opacity_path = os.path.join(export_dir, "texture", f"{mat.name}_opacity.png")
                                image.filepath_raw = opacity_path
                                image.file_format = 'PNG'
                                image.save()
                            # 导出发光贴图
                            if "Emission" in node.label:
                                emission_path = os.path.join(export_dir, "texture", f"{mat.name}_emission.png")
                                image.filepath_raw = emission_path
                                image.file_format = 'PNG'
                                image.save()
    #导出FBX文件
    def export_fbx(self,obj, export_dir):
        if not os.path.exists(export_dir):
            os.makedirs(export_dir)

        filepath = os.path.join(export_dir, f"{obj.name}.fbx")
        bpy.ops.export_scene.fbx(
            filepath=filepath,
            use_selection=True,
            global_scale=1.0,
            axis_forward='X',
            axis_up='Z',
            object_types={'MESH'},
            bake_space_transform=True
        )
    #导出VMDL文件
    def export_vmdl(self,select_name, directory,obj):
        # 读取Vmdl模板文件
        template = os.path.join(os.path.dirname(__file__), "templates", "model.vmdl")
        if template is None or not os.path.exists(template):
            self.report({'ERROR'}, "File not found the model.vmdl")
            return {'CANCELLED'}
        bt_config = kv3.read(template)
        # 修改模型路径
        for child in bt_config["rootNode"]["children"]:
            if child["_class"] == "RenderMeshList":
                for render_child in child["children"]:
                    # 检查子节点是否有 filename 并进行修改
                    if "filename" in render_child:
                        path = os.path.join("models", select_name, select_name + ".fbx").replace("\\", "/")
                        render_child["filename"] = path  # 修改文件名
        #修改材质路径
        for child in bt_config["rootNode"]["children"]:
            if child["_class"] == "MaterialGroupList":
                for material_group in child["children"]:
                    if material_group["_class"] == "DefaultMaterialGroup" and "remaps" in material_group:
                        for mat_slot in obj.material_slots:
                            mat = mat_slot.material
                            remap = {
                                "from": f"{mat.name}.vmat",
                                "to": os.path.join("models", select_name, "texture", f"{mat.name}.vmat").replace(
                                    "\\", "/")
                            }
                            material_group["remaps"].append(remap)
        # 写入VMDL 文件
        savename = os.path.join(directory, select_name + ".vmdl")
        kv3.write(bt_config, savename)
    #导出VMAT文件
    def export_vmat(self,select_name, directory, obj):
        # 读取Vmat模板文件
        template = os.path.join(os.path.dirname(__file__), "templates", "material.vmat")
        with open(template, "r", encoding="utf-8") as f:
            kv3_data = f.read()
        for mat_slot in obj.material_slots:
            mat = mat_slot.material
            # 使用正则表达式修改 TextureColor 的值
            pattern = r'(\bTextureColor\b\s+"[^"]+")'
            diffusepath = os.path.join("models", select_name, "texture", mat.name + "_diffuse.png").replace("\\", "/")
            replacement = f'TextureColor "{diffusepath}"'
            kv3_data_modified = re.sub(pattern, replacement, kv3_data)

            # 修改 TextureNormal
            pattern = r'(\bTextureNormal\b\s+"[^"]+")'
            normalpath = os.path.join("models", select_name, "texture", mat.name + "_normal.png").replace("\\", "/")
            if os.path.exists(normalpath):
                replacement = f'TextureNormal "{normalpath}"'
                kv3_data_modified = re.sub(pattern, replacement, kv3_data_modified)

            # 修改 TextureRoughness
            pattern = r'(\bTextureRoughness\b\s+"[^"]+")'
            roughnesspath = os.path.join("models", select_name, "texture", mat.name + "_roughness.png").replace("\\",
                                                                                                                     "/")
            if os.path.exists(roughnesspath):
                replacement = f'TextureRoughness "{roughnesspath}"'
                kv3_data_modified = re.sub(pattern, replacement, kv3_data_modified)
            # 保存修改后的数据
            output_file = os.path.join(directory, "texture", mat.name + ".vmat")
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(kv3_data_modified)
