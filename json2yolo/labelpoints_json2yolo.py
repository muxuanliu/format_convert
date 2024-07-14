import json
import os
from pathlib import Path
import requests
import yaml
from PIL import Image
from tqdm import tqdm   # 进度条

def count_inner_list(nested_list):
    count = 0
    for lst in nested_list:
        if isinstance(lst,list):
#             检查对象是否为指定类型
            count += 1
    return count

def output_label(json_path,yolo_path,image_path):
    # os.makedirs(yolo_path,exist_ok=True)
    json_path = Path(json_path).resolve()
    yolo_path = Path(yolo_path).resolve()
    json_parentpath = json_path.parent
    names_dict = {0: "person"}
    flipped_names = {v: k for k, v in names_dict.items()}
    for filename in tqdm(os.listdir(json_path),desc="Converting"):
        if filename.endswith('.json'):
            with open(os.path.join(json_path,filename), 'r',encoding='utf-8') as f:
                data = json.load(f)  # json files to dict:json_data
            last_part = os.path.basename(data.get("imagePath"))
            im_path = os.path.join(image_path,last_part)
            img = Image.open(requests.get(im_path,stream=True).raw if im_path.startswith("http") else im_path)
            width,height = img.size
#                 size属性获得图像宽度和高度的元组，通常形式为(width, height)
            label_filename = last_part+"txt"
            label_path = os.path.join(yolo_path,Path(label_filename).with_suffix(".txt"))
            # 转换后标签存放路径
            temp_str = ""
            previous_person_data = ""
            cnt = 0
            for label in data.get("shapes"):
                if label.get("label") == "person" :
                    cnt += 1
                    if cnt > 1:
                        current_person_data = f"{previous_person_data} {temp_str} \n"
                        previous_person_data = current_person_data
                    label_list = label.get("points")
                    x_1,y_1 = label_list[0]
                    x_2,y_2 = label_list[1]
                    x_centre = round(((x_1+x_2)/2)/width,2)
                    y_centre = round(((y_1+y_2)/2)/height,2)
                    person_width = round(abs(x_1-x_2)/width,2)
                    person_height = round(abs(y_1-y_2)/height,2)
                    temp_str = (f"{flipped_names['person']} {x_centre} {y_centre} {person_width} {person_height} ")

                else:
                    label_list = label.get("points")
                    x,y=label_list[0]
                    # 根据json文件的特征，points内部是双重列表，且内层只有一个列表，所以我们将第一个列表的值分别赋值给x，y
                    x = round(x/width,2)
                    y = round(y/height,2)

                    temp_str = (f"{temp_str} {x} {y} ")
            current_person_data = f"{previous_person_data} {temp_str}"

            with open(label_path,"a") as f:
                f.write(current_person_data + "\n")
     # Save dataset.yaml
    d = {
        "path": f"{json_parentpath}/cs_pose # dataset root dir".replace('\\','/'),
        "train": f"images/train  # train images (relative to path) 128 images".replace('\\','/'),
        "val": f"images/val  # val images (relative to path) 128 images".replace('\\','/'),
        "test": " # test images (optional)",
        "names": names_dict,
    }  # dictionary
    file_path = os.path.join(json_parentpath, "data1.yaml")
    with open(file_path,"w",encoding='utf-8')as f:
        yaml.dump(d,f,sort_keys=False)
    print("Conversion completed successfully!")

if __name__ == '__main__':
    output_label(r"E:\datasets\jsons",r"E:\datasets\labels",r"E:\datasets\images")
