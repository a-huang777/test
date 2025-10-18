import os
import shutil


def copy_and_replace_pyd_files(source_folder, target_folder):

    """
    将 source_folder 中的所有 .pyd 文件复制到 target_folder 中，
    如果目标文件夹中存在同名文件，则替换掉原文件。

    :param source_folder: 源文件夹路径
    :param target_folder: 目标文件夹路径
    """
    # 确保目标文件夹存在
    if not os.path.exists(target_folder):
        os.makedirs(target_folder)
        print(f"目标文件夹不存在，已创建：{target_folder}")

    # 遍历源文件夹中的所有文件
    for filename in os.listdir(source_folder):
        # 检查文件扩展名是否为 .pyd
        if filename.endswith(".pyd"):
            source_file_path = os.path.join(source_folder, filename)
            target_file_path = os.path.join(target_folder, filename)

            # 复制文件到目标文件夹，替换同名文件
            shutil.copy2(source_file_path, target_file_path)
            print(f"已复制文件：{filename} -> {target_folder}")

    print("所有 .pyd 文件已成功复制并替换完成！")

def pyd_turn_to_pyi():
    module_name = "AirCombat_demo"
    exec("import %s" % module_name)

    from pybind11_stubgen import ModuleStubsGenerator

    module = ModuleStubsGenerator(module_name)
    module.parse()
    module.write_setup_py = False

    with open("%s.pyi" % module_name, "w") as fp:
        fp.write("#\n# Automatically generated file, do not edit!\n#\n\n")
        fp.write("\n".join(module.to_lines()))
    print("pyd 文件已成功转为 pyi 文件！")
# 指定源文件夹和目标文件夹路径
if __name__ == "__main__":
    source_folder = r"D:\chiken\Middle_old\x64\Debug"  # 源文件夹路径
    target_folder =  os.getcwd()
    copy_and_replace_pyd_files(source_folder, target_folder)
    pyd_turn_to_pyi()