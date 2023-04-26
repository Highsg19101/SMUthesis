import os



imgname = 'car'
for i in range(1,21):
	print(imgname+str(i)+'.jpg')
	os.system('./img_detection_2.0 detector test cfg/coco.data cfg/yolov3.cfg yolov3.weights auto/'+imgname+str(i)+'.jpg')
	os.system('cp predictions.jpg static/classified/imshowList/'+imgname+'/'+imgname+str(i)+'.jpg')
	
