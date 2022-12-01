from highway_detection import Tracker,SpeedEstimate
import cv2
import numpy as np
import time
from PIL import Image, ImageDraw, ImageFont



class HighwayAnalyse:
    def __init__(self):

        self.speed_esti = SpeedEstimate()
        # 记录左右车道上次位置、速度 { id :{'last_pos':(123,234),'speed':12.34}  , 2: ........} 
        self.left_ids_info = {} 
        self.right_ids_info = {}

        # 中文label图像
        self.zh_label_img_list = self.getPngList()

        # 记录车辆数量
        self.vehicle_num = {'car':0,'truck':0}  
        # 汽车尾部
        self.track_tail_points = {'left':{},'right':{}}
        # 速度计量
        self.track_speeds = {'<90':0,'90-110':0,'>110':0}

    def getPngList(self):
        """
        获取PNG图像列表

        @return numpy array list
        """
        overlay_list = []
        # 遍历文件
        for i in range(2):
            fileName = './label_png/%s.png' % (i)
            overlay = cv2.imread(fileName)
            # overlay = cv2.cvtColor(overlay, cv2.COLOR_RGB2BGR)
            
            overlay_list.append(overlay)

        return overlay_list
    
    def plot_bboxes_1(self,image, bboxes,side='left'):
        """
        绘制，展示速度
        """
        alpha = 0.9
        this_ids_info = self.left_ids_info if side == 'left' else self.right_ids_info

        

        for (l, t, r, b, cls_name, track_id) in bboxes:
            # png_id = 0
            # if cls_name == 'truck':
            #     png_id = 1
            #     color = (255, 0, 255)
            #     self.vehicle_num['truck'] +=1
            # elif cls_name == 'car':
            #     color = (0, 255, 0)
            #     self.vehicle_num['car'] +=1


            # image[t:b,l:r,0] = image[t:b,l:r,0] * alpha + color[0] * (1-alpha)
            # image[t:b,l:r,1] = image[t:b,l:r,1] * alpha + color[1] * (1-alpha)
            # image[t:b,l:r,2] = image[t:b,l:r,2] * alpha + color[2] * (1-alpha)

            # cv2.rectangle(image, (l,t), (r,b), color, thickness=1)
           

            # # 拖着小尾巴
            # if side == 'left':
            #     # 尾部位置（左）
            #     head_pos = l+int((r-l)/2),t
            # else:
            #     head_pos = l+int((r-l)/2),b
            # if track_id in self.track_tail_points[side]:

            #     self.track_tail_points[side][track_id].append(head_pos)
            #     # 保持长度
            #     if len(self.track_tail_points[side][track_id]) > 20:
            #         del self.track_tail_points[side][track_id][0]

            # else:
            #     self.track_tail_points[side][track_id] = [head_pos]

            # # 绘制尾部
         
            # pts = np.asarray(self.track_tail_points[side][track_id],np.int32)
                        
            # pts = pts.reshape((-1, 1, 2)) 
            # cv2.polylines(image, [pts], False, color, 2) 


            scale = (r- l)/40 * 0.3

            if track_id in this_ids_info and this_ids_info[track_id]['speed'] != 0:
                speed = round(this_ids_info[track_id]['speed'],1)
                # self.track_speeds = {'<90':0,'90-110':0,'>110':0}
                # if speed < 90:
                #     self.track_speeds['<90'] +=1
                # elif speed < 110:
                #     self.track_speeds['90-110'] +=1
                # else:
                #     self.track_speeds['>110'] +=1
                cv2.putText(image, '{}km/h'.format(speed), (l,t-60), cv2.FONT_ITALIC,scale,(0, 255, 0),2)
                print("track_id:===",track_id,"speed:===",speed)
            else:
                cv2.putText(image, '{}-{}'.format(cls_name, track_id), (l,t-60), cv2.FONT_ITALIC,scale,(0, 255, 0),2)

    
   # 添加中文
    def cv2AddChineseText(self,img, text, position, textColor=(0, 255, 0), textSize=30):
        if (isinstance(img, np.ndarray)):  # 判断是否OpenCV图片类型
            img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        # 创建一个可以在给定图像上绘图的对象
        draw = ImageDraw.Draw(img)
        # 字体的格式
        fontStyle = ImageFont.truetype(
            "./fonts/MSYH.ttc", textSize, encoding="utf-8")
        # 绘制文本
        draw.text(position, text, textColor, font=fontStyle)
        # 转换回OpenCV格式
        return cv2.cvtColor(np.asarray(img), cv2.COLOR_RGB2BGR)



    def update_id_info(self,bboxes,side='left'):
        """
        获取当前画面各ID的位置、车速信息
        """
        last_frame_info = self.left_ids_info if side == 'left' else self.right_ids_info


        # 本帧位置
        this_frame_info = {}
        for (l, t, r, b, cls_name, track_id) in bboxes:
            
            if side == 'left':
                # 尾部位置（左）
                head_pos = l+int((r-l)/2),t
            else:
                head_pos = l+int((r-l)/2),b
            # 初始化
            this_frame_info[track_id] = {'last_pos':head_pos,'speed':0}
            #print("track_id==",track_id)
            #print("head_pos==",head_pos)


        if len(last_frame_info) > 0:
            # 更新
            # 上：1、2、3、4
            # 本：3、4、5、6
            # 需要：更新3、4速度，插入 5、6 记录

            # 更新后的信息
            update_frame_info = {}
            update_num = 0
            insert_num  = 0

            for key,val in this_frame_info.items():
                
                if key in last_frame_info:
                    # 更新
                    # 本帧位置
                    this_frame_pos = val['last_pos']
                    # 上帧位置
                    last_frame_pos = last_frame_info[key]['last_pos']
                    # 计算距离
                    distance = self.speed_esti.pixelDistance(this_frame_pos[0], this_frame_pos[1], last_frame_pos[0], last_frame_pos[1])
                    # 速度
                    speed = distance * 3.6 #* 2 #1m/s=3.6km/h

                    update_frame_info[key] = {'last_pos':this_frame_pos,'speed':speed}

                    update_num +=1
                else:
                    # 插入
                    # 本帧位置
                    this_frame_pos = val['last_pos']
                    update_frame_info[key] = {'last_pos':this_frame_pos,'speed':0}
                    insert_num +=1
            

            print("{}侧车道，刷新{}辆车信息，新增{}辆车位置信息".format(side,update_num,insert_num))

            last_frame_info = update_frame_info


        else:
            # 初始化
            last_frame_info = this_frame_info
            print("{}侧车道，新增：{}辆车位置信息".format(side,len(last_frame_info)))

        # 重新赋值
        if side == 'left':
            self.left_ids_info = last_frame_info
            print("===========",last_frame_info)
        else:
            self.right_ids_info = last_frame_info
