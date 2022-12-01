import cv2
import math

knownWidth = 1.8  #障碍物宽度
knownHeight = 5   #障碍物高度H(摄像头和障碍物高度之差) 5
focalLength = 2.5 #聚焦长度f
CCD_W = 4.8       #相机长度方向视野
CCD_H = 3.6       #相机宽度方向视野
IMAGE_W = 4096    #图像/视频分辨率W
IMAGE_H = 2160    #图像/视频分辨率H
veh_speed = 3.0   # 本车车速 km/h
dis_last = 0.0



# 测距处理函数
def mdm_info_proc(boxs,im0):
    #print("=======mdm_info========")
    #t_s = float(cur_s - last_s)
    #dis_last = 0
    ttc = 0
    dis_x = 0
    dis_y = 0
    z = 0
    bar_rel_spd = 0
    #print("t_s:", t_s)
    #print("id:", index, "box:", int(boxs[0]), int(boxs[1]), int(boxs[2]), int(boxs[3]))
    # z = (knownWidth * focalLength) / box[2] #距离相机垂直距离
    # center_x = box[0] + float(box[2] / 2) #图像坐标系矩形框底边中心x
    # center_y = box[1] + box[3] #图像坐标系矩形框底边中心y
    # z = (knownWidth * focalLength) / (boxs[2] - boxs[0])  # 距离相机垂直距离

    # 1、像素坐标系转换为图像坐标系
    pixel_w = boxs[2] - boxs[0]
    pixel_h = boxs[3] - boxs[1]
    #一个摄像头采集数据，然后拍照，拍出来的照片是640*480的，那么这张照片的一个像素的宽度是多少啊
    #如果是说测量的尺寸，长方向的视野/640= 一个像素点测量的宽度。
    dx = float(CCD_W / IMAGE_W) #单个像素代表的宽度 mm
    dy = float(CCD_H / IMAGE_H) #单个像素代表的高度 mm

    pixel_u = boxs[0] + float((boxs[2] - boxs[0]) / 2)  # 矩形框底边中心x
    pixel_v = boxs[3]  # 矩形框底边中心y

    img_x = float((pixel_u - IMAGE_W/2) * dx)
    img_y = float((pixel_v - IMAGE_H/2) * dy)

    # 2、图像坐标系转相机坐标系
    z = float((knownHeight * focalLength) / (pixel_h * dy))  # 距离相机垂直距离
    cam_x = float(z / focalLength * img_x)  # 左负右正

    # 3、相机坐标系下车辆距离
    dis_y = z  # 纵向距离
    dis_x = cam_x  # 横向距离
    
    #在图像/视频上画距离
    # scale = float(pixel_w/40 * 0.2)
    # scale = round(scale,3)
    z_0 = "{:.2f}".format(z)
    z_0=z_0+'m'
    cv2.putText(im0,str(z_0), (int(boxs[0]), int(boxs[1] - 30)), 0, 1,(255, 0, 0), 2,cv2.LINE_AA)

    #计算速度
    # if t_s != 0 and dis_last[index-1] != 0:
    #     if abs(dis_x) < (0.9 + 0.5):  # 判断cipv，车身往外0.5米范围内
    #         bar_speed = float((dis_y - dis_last[index-1]) / t_s)  # 前车速度 m/s
    #         bar_rel_spd = bar_speed - veh_speed * 10 / 36  # 相对速度=前-自
    #         if bar_rel_spd != 0:
    #             ttc = float(dis_y / bar_rel_spd)
    #         if ttc < 2.6 and dis_y< 3.5:
    #             fcw[0] = 1
    #             #print("FCW-前车碰撞预警")

    # dis_last[index-1] = dis_y  #y应该取上一帧记录的值

    #print("dis_y:", dis_y, "dis_x:", dis_x, "m", "ttc:", ttc, "rel_spd:", bar_rel_spd, "m/s")
    return z



def measure_v(boxs, im0, dis_diff, frame_inter):#测速处理
    #在图像/视频上画距离
    
    speed = dis_diff / frame_inter

    print("dis_diff====",dis_diff)
    print("speed=======",speed)
    speed_0 = "{:.2f}".format(speed)
    speed_0=speed_0+'m/s'
    cv2.putText(im0,str(speed_0), (int(boxs[0]+100), int(boxs[1] - 50)), 0, 2,(0, 255, 0), 2,cv2.LINE_AA)






