import json
import os
from pathlib import Path
import shutil

import requests
import yaml
from PIL import Image
from tqdm import tqdm   # 进度条


from utils import make_dirs


def convert(file, zip=True):
    """Converts Labelbox JSON labels to YOLO format and saves them, with optional zipping."""
    names = []  # class names 定义一个空列表
    file = Path(file)
    save_dir = make_dirs(file.stem) # 获取文件名部分，不包含拓展名
    with open(file,encoding='utf-8') as f:
        data = json.load(f)  # load JSON

    for img in tqdm(data, desc=f"Converting {file}"):   # desc设置进度条的描述信息的参数，该示例为在进度条上显示类似Converting file.jpg
        # img读到的是一个键，因为字典迭代默认为键
        # im_path = img["Labeled Data"]       #获取json文件中labeled data键的值
        # im_path = img["imagePath"]       #获取json文件中labeled data键的值
        im_path = data.get("imagePath")       #获取json文件中labeled data键的值
        im = Image.open(requests.get(im_path, stream=True).raw if im_path.startswith("http") else im_path)
        # open 条件表达式语法  value_if_true if condition else value_if_false，
        # requests.get(im_path, stream=True).raw stream=True逐步获取响应内容而不是一次性将其全部下载到内存中；.raw可以以流的方式逐步读取响应内容
        width, height = im.size  # image size
        # label_path = save_dir / "labels" / Path(img["External ID"]).with_suffix(".txt").name
        # label_path = save_dir / "labels" / Path(img["imagePath"]).with_suffix(".txt").name    这是错误的，因为它里面不是字典
        label_path = save_dir / "labels" / Path(data.get("imagePath")).with_suffix(".txt").name
        #“/”创建一个多级目录；Path('文件').with_suffix更改文件拓展名；.name获取文件路径的最后一级组成部分，如/home/user/example.txt获得example.txt
        image_path = save_dir / "images" / data.get("imagePath")
        im.save(image_path, quality=95, subsampling=0)
        #quality质量级别，1-95；subsampling子采样，0；1；2，0表示关闭，1开启，2高质量子采样，默认保存为jpeg格式

        # for label in img["Label"]["objects"]:
        # 获取Label属性，然后从该属性中获得名为objects的子属性的值
        # for label in img["shapes"]:
        for label in data.get("shapes"):
            # box
            # top, left, h, w = label["bbox"].values()  # top, left, height, width
            # X,Y  = label["points"].values()  # X Y
            XY = label["points"][0]
            X = XY[0]/width
            Y = XY[1]/height
            # xywh = [(left + w / 2) / width, (top + h / 2) / height, w / width, h / height]  # xywh normalized
            # XY = [X/width,Y/height]
            # class
            # cls = label["value"]  # class name
            cls = label["label"]  # class name
            if cls not in names:
                names.append(cls)
                #.append向列表末尾添加一个元素

            # line = names.index(cls), *xywh  # YOLO format (class_index, xywh)
            line = names.index(cls), *XY  # YOLO format (class_index, XY)
            with open(label_path, "a") as f:
                # “a”追加模式
                f.write(("%g " * len(line)).rstrip() % line + "\n")
                #%g是python中格式化字符串的一种格式化符号，会根据值的大小自动选择%f和%e
                #"%g " * len(line)：这部分代码是使用格式化字符串，将 %g 这个格式符重复 len(line) 次，每个 %g 之间用空格分隔。
                #rstrip()：这个方法用于移除字符串末尾的空格（包括空格、制表符等）
                #整段的作用是将元组line中的元素按照%g的格式写入文件，并在行末尾添加换行符，以便下一行继续写入数据。

    # Save dataset.yaml
    d = {
        "path": f"../datasets/{file.stem}  # dataset root dir",
        "train": "images/train  # train images (relative to path) 128 images",
        "val": "images/val  # val images (relative to path) 128 images",
        "test": " # test images (optional)",
        "nc": len(names),
        "names": names,
    }  # dictionary

    with open(save_dir / file.with_suffix(".yaml"),"w",encoding='utf-8') as f:
        yaml.dump(d, f, sort_keys=False)
        #dump将字典写入文件对象中，禁止对键排序 sort_keys=False

    # Zip
    # if zip:
    #     print(f"Zipping as {save_dir}.zip...")
    #     os.system(f"zip -qr {save_dir}.zip {save_dir}")

    # Zip
    if zip:
        save_dir_abs = os.path.abspath(save_dir)
        zip_file = f"{save_dir_abs}.zip"
        print(f"Zipping as {zip_file}...")
        shutil.make_archive(save_dir_abs, 'zip', save_dir_abs)
        # def make_archive(base_name, format, root_dir=None, base_dir=None, verbose=0,
        #                  dry_run=0, owner=None, group=None, logger=None):

    print("Conversion completed successfully!")


if __name__ == "__main__":
    convert(r"D:\Desktop\test_convert\20220430171746.json")


