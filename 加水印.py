import cv2



cap = cv2.VideoCapture('runs/detect/exp20/highway.mp4')
fps = cap.get(cv2.CAP_PROP_FPS)
# 设置视频的编码格式
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
#获取视频的宽和高
video_width = int(cap.get(3))
video_height = int(cap.get(4))
# 定义视频保存的输出属性
out = cv2.VideoWriter('runs/detect/exp20/v2xway.mp4', fourcc, fps,(video_width,video_height))
while True:
    ret,frame  = cap.read()
    if frame is None:
        break
    cv2.putText(frame, 'QQ1223371220', (300,1800), cv2.FONT_ITALIC,2,(100,100,100),3)
        # videoWriter.write(frame)
    out.write(frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# videoWriter.release()
cap.release()
cv2.destroyAllWindows()


