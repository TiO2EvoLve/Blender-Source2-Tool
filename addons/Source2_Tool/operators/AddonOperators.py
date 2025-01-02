import json
import os
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
        for obj in selected_objects:
            # 清除所有选择
            bpy.ops.object.select_all(action='DESELECT')
            # 选择当前物体
            obj.select_set(True)
            bpy.context.view_layer.objects.active = obj  # 设置活动对象
            # 获取选中物体的名称
            select_name = obj.name
            # 获取导出路径
            directory = os.path.join(addon_prefs.filepath, select_name)
            #导出FBX文件
            export_fbx(obj, directory)
            #导出PBR材质贴图生成vmat文件
            export_pbr_textures(obj, directory)
            #导出VMDL文件
            export_vmdl(select_name, directory,obj)
            # 提示用户导出成功
            self.report({'INFO'}, f"已导出 {directory}")
        return {'FINISHED'}

#导出PBR材质和创建vmat
def export_pbr_textures(obj, export_dir):
    if not os.path.exists(export_dir):
        os.makedirs(export_dir)
    for mat_slot in obj.material_slots:
        mat = mat_slot.material
        json_path = os.path.join(os.path.dirname(__file__), "templates", "material.vmat")
        with open(json_path, "r", encoding="utf-8-sig") as file:
            data = json.load(file)
        if mat and mat.use_nodes:
            for node in mat.node_tree.nodes:
            # 查找图像纹理节点
                if node.type == 'TEX_IMAGE':
                    image = node.image
                    if image:
                        # 导出漫反射贴图
                        if "Base Color" in node.label:
                            image_path = os.path.join(export_dir, "texture", f"{mat.name}_diffuse.png")
                            savepng(image, image_path)
                            path = os.path.join("models", obj.name, "texture", f"{mat.name}_diffuse.png").replace("\\", "/")
                            data["Layer0"]["TextureColor"] = path
                        # 导出法线贴图
                        if "Normal" in node.label:
                            normal_path = os.path.join(export_dir, "texture", f"{mat.name}_normal.png")
                            savepng(image, normal_path)
                            path = os.path.join("models", obj.name, "texture", f"{mat.name}_normal.png").replace("\\", "/")
                            data["Layer0"]["TextureNormal"] = path
                        # 导出粗糙度贴图
                        if "Roughness" in node.label:
                            roughness_path = os.path.join(export_dir, "texture", f"{mat.name}_roughness.png")
                            savepng(image, roughness_path)
                            path = os.path.join("models", obj.name, "texture", f"{mat.name}_roughness.png").replace("\\", "/")
                            data["Layer0"]["TextureRoughness"] = path
                        # 导出金属度贴图
                        if "Metallic" in node.label:
                            metallic_path = os.path.join(export_dir, "texture", f"{mat.name}_metallic.png")
                            savepng(image, metallic_path)
                            path = os.path.join("models", obj.name, "texture", f"{mat.name}_metallic.png").replace("\\", "/")
                            data["Layer0"]["F_SPECULAR"] = "1"
                            data["Layer0"]["F_METALNESS_TEXTURE"] = "1"
                            data["Layer0"]["TextureMetalness"] = path
                        # 导出透明度贴图
                        if "Alpha" in node.label:
                            opacity_path = os.path.join(export_dir, "texture", f"{mat.name}_opacity.png")
                            savepng(image, opacity_path)
                            path = os.path.join("models", obj.name, "texture", f"{mat.name}_opacity.png").replace("\\", "/")
                            data["Layer0"]["F_TRANSLUCENT"] = "1"
                            data["Layer0"]["TextureTranslucency"] = path
                        # 导出发光贴图
                        if "Emission" in node.label:
                            emission_path = os.path.join(export_dir, "texture", f"{mat.name}_emission.png")
                            savepng(image, emission_path)
                            path = os.path.join("models", obj.name, "texture", f"{mat.name}_emission.png").replace("\\", "/")
                            data["Layer0"]["F_SPECULAR"] = "1"
                            data["Layer0"]["TextureSelfIllumMask"] = path
        modified_content = dict_to_string(data)
        # 保存修改后的数据
        output_file = os.path.join(export_dir, "texture", mat.name + ".vmat")
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(modified_content)

# 保存图片
def savepng(image, path):
    image.filepath_raw = path
    image.file_format = 'PNG'
    image.save()

# 导出FBX文件
def export_fbx(obj, export_dir):
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

# 导出VMDL文件
def export_vmdl(select_name, directory, obj):
    # 读取Vmdl模板文件
    template = os.path.join(os.path.dirname(__file__), "templates", "model.vmdl")
    bt_config = kv3.read(template)
    # 修改模型路径
    for child in bt_config["rootNode"]["children"]:
        if child["_class"] == "RenderMeshList":
            for render_child in child["children"]:
                # 检查子节点是否有 filename 并进行修改
                if "filename" in render_child:
                    path = os.path.join("models", select_name, select_name + ".fbx").replace("\\", "/")
                    render_child["filename"] = path  # 修改文件名
    # 修改材质路径
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
#将字典转换为vmat格式
def dict_to_string( data, indent=0):
    result = ""
    for key, value in data.items():
        if isinstance(value, dict):
            result += " " * indent + key + " {\n"
            result += dict_to_string(value, indent + 4)
            result += " " * indent + "}\n"
        else:
            result += " " * indent + f'{key} "{value}"\n'
    return result


