
from common.i18n.dictionary import preprocess_dictionary

dictionary = {
    "zh_CN": {
        ("*", "Export to Hammer"): "导出到Hammer",
        ("*", "ExampleAddon"): "示例插件",
        ("*", "filepath"): "导出路径",
        #这不是定义翻译的标准方式，但是preprocess_dictionary仍然支持这种方式。
        ("Operator", "Change Language"): "切换语言",
        ("Operator", "Change Hammer Unit"): "转为Hammer单位(开发中)",
        ("Operator", "Add Outline"): "添加描边",
    }
}

dictionary = preprocess_dictionary(dictionary)

dictionary["zh_HANS"] = dictionary["zh_CN"]
