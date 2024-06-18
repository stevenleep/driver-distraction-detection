import time
import cv2
import global_label

# 简单的没有模型的代码
def process_video(video_path):
    start_time = time.time()
    frame_count = 0
    cap = cv2.VideoCapture(video_path)

    # global global_label.global_current_label

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("无法捕获视频帧")
            break

        # global global_current_label
        global_label.updateValue("safe")
        global_current_label = global_label.getValue()
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 1
        text_color = (255, 0, 0)
        text_position = (50, 50)
        cv2.putText(frame, global_current_label, text_position, font, font_scale, text_color, 2)
        # Calculate FPS
        frame_count += 1
        elapsed_time = time.time() - start_time
        fps = frame_count / elapsed_time
        cv2.putText(frame, f'FPS: {round(fps, 2)}', (10, 30), font, 0.5, (0, 255, 0), 1)
        # Convert processed frame back to bytes
        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')


# 实时摄像头
def generate_frames():
    start_time = time.time()
    frame_count = 0
    cap = cv2.VideoCapture(0)
    global global_current_label
    while cap.isOpened():
        ret, frame = cap.read()

        if not ret:
            print("无法捕获视频帧")
            break

        global_label.updateValue("dangerous")
        global_current_label = global_label.getValue()

        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 1
        text_color = (255, 0, 0)
        text_position = (50, 50)
        cv2.putText(frame, global_current_label, text_position, font, font_scale, text_color, 2)
        # Calculate FPS
        frame_count += 1
        elapsed_time = time.time() - start_time
        fps = frame_count / elapsed_time
        cv2.putText(frame, f'FPS: {round(fps, 2)}', (10, 30), font, 0.5, (0, 255, 0), 1)
        # Convert processed frame back to bytes
        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')