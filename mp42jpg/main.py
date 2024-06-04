import tkinter as tk
from tkinter import filedialog
import cv2
from pathlib import Path
import threading
from tqdm import tqdm   # 20240326添加进度条

global is_processing,current_task,pool,pause_event
pause_event = threading.Event()
pause_event.set()
is_processing = True
pool = None

def select_video():
    video_path =filedialog.askdirectory()
    entry_video.delete(0, tk.END)
    entry_video.insert(0, video_path)

def select_output_dir():
    output_dir = filedialog.askdirectory()
    entry_output.delete(0, tk.END)
    entry_output.insert(0, output_dir)


def start_process():
    global  is_processing
    is_processing = True
    app_status()



def stop_process():
    global is_processing,pool
    is_processing = False


def break_process():
    global is_processing,pause_event
    # is_processing = False
    pause_event.clear()

def continue_process():
    global is_processing,thread,pause_event
    # is_processing = True
    pause_event.set()



def app_status():
    global is_processing,thread
    video_path = entry_video.get()
    output_dir = entry_output.get()
    interval = int(frame_interval_entry.get())
    thread = threading.Thread(target=run,args=(video_path,output_dir,interval))
    thread.start()


def output_img(video_path, img_dir,frame_interval):
    global is_processing,pause_event
    # 由视频逐帧输出图片
    # video_path: 视频文件路径
    # img_dir: 图片保存目录路径，路径不支持中文
    cv = cv2.VideoCapture(video_path)
    frame_count = 0
    n = 0
    total_frames = int(cv.get(cv2.CAP_PROP_FRAME_COUNT)) // frame_interval
    pbar = tqdm(total=int(cv.get(cv2.CAP_PROP_FRAME_COUNT))/frame_interval)
    while pbar.n < total_frames:
        ret, frame = cv.read()
        if not ret:
            break
        frame_count += 1
        if frame_count % frame_interval == 0:
            pbar.update(1)
            if not pause_event.is_set():  # 检查是否需要暂停线程
                pause_event.wait()
            n += 1
            img_name = f"0000000{n}.jpg"
            img_file_path = Path(img_dir) / img_name
            if not img_file_path.exists():
                print("创建文件:", img_file_path)
                cv2.imwrite(str(img_file_path), frame, [cv2.IMWRITE_JPEG_QUALITY, 100])
            else:
                print("跳过:", img_file_path)
    pbar.close()
def run(video_dir, img_dir,frame_interval):
    global is_processing
    i=0
    for file in Path(video_dir).iterdir():
        print(i,end='\n')
        i= i+1
        if not is_processing:
            break
        if file.suffix == ".mp4":
            video_file_path = str(file)
            img_dir_name = Path(img_dir) / file.stem  # 使用视频文件名作为子目录名
            img_dir_name.mkdir(parents=True, exist_ok=True)
            output_img(video_file_path, str(img_dir_name),frame_interval)
    print("Thread execution stopped")


# 创建主窗口
root = tk.Tk()
root.title("视频处理程序")
root.geometry("800x600")

# 添加选择视频按钮
btn_select_video = tk.Button(root, text="选择视频文件", command=select_video)
btn_select_video.pack(side='top',pady=10)

# 添加选择输出路径按钮
btn_select_output = tk.Button(root, text="选择输出路径", command=select_output_dir)
btn_select_output.pack(side='top',pady=10)

# 显示视频路径输入框
entry_video = tk.Entry(root)
entry_video.pack()

# 显示输出路径输入框
entry_output = tk.Entry(root)
entry_output.pack()

# 添加帧间隔输入框
frame_interval_label = tk.Label(root, text="帧间隔：")
frame_interval_label.pack(side='top', pady=10)
frame_interval_entry = tk.Entry(root)
frame_interval_entry.pack()

# 添加开始处理按钮
btn_start = tk.Button(root, text="开始处理", command=start_process)
btn_start.pack(side='top',pady=10)

# 添加停止处理按钮
btn_start = tk.Button(root, text="停止处理", command=stop_process)
btn_start.pack(side='top',pady=10)

# 添加暂停处理按钮
btn_start = tk.Button(root, text="暂停处理", command=break_process)
btn_start.pack(side='top',pady=10)

# 添加继续处理按钮
btn_start = tk.Button(root, text="继续处理", command=continue_process)
btn_start.pack(side='top',pady=10)


# 启动主循环
root.mainloop()
