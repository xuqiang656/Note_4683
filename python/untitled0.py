import ffmpeg
import numpy as np
import cv2
import datetime

def main(source):
    args = {
        "rtsp_transport": "tcp",
        "fflags": "nobuffer",
        "flags": "low_delay"
    }    # 添加参数
    probe = ffmpeg.probe(source)
    cap_info = next(x for x in probe['streams'] if x['codec_type'] == 'video')
    print("fps: {}".format(cap_info['r_frame_rate']))
    width = cap_info['width']           # 获取视频流的宽度
    height = cap_info['height']         # 获取视频流的高度
    up, down = str(cap_info['r_frame_rate']).split('/')
    fps = eval(up) / eval(down)
    print("fps: {}".format(fps))    # 读取可能会出错错误
    process1 = (
        ffmpeg
        .input(source, **args)
        .output('pipe:', format='rawvideo', pix_fmt='rgb24')
        .overwrite_output()
        .run_async(pipe_stdout=True)
    )
    while True:
        in_bytes = process1.stdout.read(width * height * 3)     # 读取图片
        if not in_bytes:
            break
        # 转成ndarray
        in_frame = (
            np
            .frombuffer(in_bytes, np.uint8)
            .reshape([height, width, 3])
        )
        frame = cv2.cvtColor(in_frame, cv2.COLOR_RGB2BGR)  # 转成BGR
        # cv2.imshow(time_str(), frame)
        cv2.imwrite(time_str()+".jpg", frame)
        # if cv2.waitKey(1) == ord('q'):
        #     break
    process1.kill()             # 关闭

def time_str(fmt=None):
    if fmt is None:
        fmt = '%Y_%m_%d_%H_%M_%S'
    return datetime.datetime.today().strftime(fmt)

if __name__ == "__main__":
    # rtsp流需要换成自己的
    user_name, user_pwd = "admin", "1234"
    ca_ip = "192.168.1.168"
    channel = 2
    alhua_rtsp="rtsp://192.168.144.25:8554/main.264"

    main(alhua_rtsp)
