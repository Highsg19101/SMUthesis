import os, sys, string
from flask import redirect, Flask, render_template, request, redirect, url_for, send_from_directory
from werkzeug import secure_filename


UPLOAD_FOLDER = 'static'
RESULT_FOLDER = './'
ALLOWED_EXTENSIONS = set(['jpg','jpeg','png','mp4','avi']) # 업로드 허용되는 파일형식

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def classified_IMG(img_path):
	os.system('./img_detection_2.0 detector test cfg/coco.data cfg/yolov3.cfg yolov3.weights '+img_path) #분류 시작
	f = open("classifieded_Object_img.log",'r') #수정한 YOLO가 실행파일이 객체를 분류할때 생성시킨 log 파일
	obj_list= []
	line = f.readline()
	print(line)
	if line == None:
		return "line","is None"
	obj_list = line.split(' ') #이미지에서 분류된 객체의 이름
	obj_list.pop()

	many_print = count_object(obj_list) #가장 많이 출현된 객체를 반환

	if many_print == "car":
		os.system('./img_detection_2.0 detector test data/obj.data yolo-obj.cfg three_detection.weights '+img_path)
		f = open("classifieded_Object_img.log",'r')
		obj_list= []
		line = f.readline()
		if line == None:
			return "line is ","None"
		obj_list = line.split(' ')
		obj_list.pop()
		many_print = count_object(obj_list) #가장 많이 출연한 객체
	f.close()
	f = open("print_object.txt","r")
	obj_print = f.readline()

	f.close()

	return obj_print, many_print

def classified_MP4(mp4_path,user_key,f_name):
	if user_key == "i40" or user_key == "ray" or f_name == "santafe": #국산 차종이 있는 동영상을 분류 할 때
		print("korean car")
		os.system('./mp4_detection_2.0 detector demo data/obj.data yolo-obj.cfg three_detection.weights '+mp4_path)

	else: #그냥 동영상에서의 객체를 분류할 때
		os.system('./mp4_detection_2.0 detector demo cfg/coco.data cfg/yolov3.cfg yolov3.weights '+mp4_path)

	return mp4_analysis(user_key,f_name) #객체가 출현한 모든 시간과 동영상 런닝타임 반환

def count_object(obj_list):
        #print(obj_list)
	f = open('print_object.txt','w') #웹페이지에 표시할 글이 있는 txt 파일
	f_m = open('m_object.txt','w')
	word = {} # dict type
	for i in obj_list: #출연한 객체를 count함
		try: word[i] += 1
		except: word[i] = 1

	list_word = list(word) #list로 변환
	print('list_word',type(list_word),list_word)
	for i in range(0,len(list_word)): #ex) car is 3, person is 10, ~~~ is ~~~.....
                l = str(word[list_word[i]])
                s = str(list_word[i])
                f.write(s)
                f_m.write(s)
                f.write(' is ')
                f_m.write(' ')
                f_m.write(l)
                f.write(l)
                f.write(',')
                f_m.write(',')
	f.close()
	f_m.close()
	f = open('m_object.txt','r') #가장 많이 출연한 객체가 있는 txt 파일  ex) person 12, car 15, stopsign 5 ...
	many = f.readline()
	f.close()
	many = many.split(',')  # ex) many = ["person 12","car 15","stopsign 5"]
	ob_li = [0] * len(many) #초기화
	count = [0] * len(many)

	for i in range(0,len(many)-1):
		obj = many[i].split(" ")#obj = ['person','12']  -> obj = ['car', 15]
		ob_li[i] = obj[0]
		count[i] = obj[1]

	print("ob_li",type(ob_li),ob_li)
	return ob_li[count.index(max(count))].pop() #ob li와 count는 1:1 매칭되므로 count 에서 가장 큰 index의 ob_li를 반환

def mp4_analysis(my_key,fileName):
	fps = 30 #fps는 30으로 가정

	origin = fileName.split(".")[0]

	os.system("cp classifieded_Object_mp4.log logfile/"+origin+".log") #고유의 파일이름으로 log 파일 남겨둠 (추후에 재 업로드가 되었을때 분류를 할 필요가 없음)
	os.system("rm classifieded_Object_mp4.log")
	#f = open("logfile/"+origin+".log","r")
	f = open("classifieded_Object.log","r")
	lines = f.readlines()
	print('lines = ',lines)
	length_lines = len(lines)
	last_frame = int(lines[-1])

	cor_count = 0

	length_mp4 = float(last_frame) / fps # 마지막프레임의 수 / fps = 동영상 런닝타임
	print('last frame' , last_frame)
	print_list = [0] * length_lines * 100

	for i in range(0,length_lines):
		lines[i] = lines[i].strip('\n')
		spl = lines[i].split()
		print(spl)
		for j in range(0,len(spl)):
			if my_key == spl[j]:
				index = lines[i-1]
				frame = index
				index = float(index) / fps
				indx = round(float(index),2)
				print_list[cor_count] = indx
				cor_count = cor_count + 1

	print_list = map(int,print_list)
	print_list = list(set(print_list))
	print_list.pop(0)
	print_list.sort()
	print('print_list',print_list)
	f.close()
	return print_list, round(length_mp4,2) #print_list 는 3,5,19,21 과 같은 object 출현 시간들이 담겨있음


def allowed_file(file_name):
	what = '.' in file_name and file_name.rsplit('.',1)[1] in ALLOWED_EXTENSIONS
	print('what ?', what)
	return what

@app.route('/keyword',methods=['GET','POST'])
def keyword(username= None):
	global key
	error = None
	if request.method == 'POST':
		username = request.form['username']
		print(username)
	else:
		error = 'error'

	return render_template('keyword2.html',caption = username,error=error)

@app.route('/img',methods=['GET','POST'])
def img():
	error = None
	if request.method == 'POST':
		up_file = request.files['file']
		print(allowed_file(up_file.filename))
		if up_file and allowed_file(up_file.filename):
			fileType = (up_file.filename).split('.')
#			print(type(fileType))
			fileType = fileType[1]
			up_filename = secure_filename(up_file.filename)
			up_file.save(os.path.join(app.config['UPLOAD_FOLDER'],up_filename))
			print('FILE TYPE IS ',up_filename)
			object, many_obj = classified_IMG('static/'+ up_filename) # 출연한 객체와 가장 많이 출연한 객체를 반환받음

			p_up_name = 'P'+up_filename
			os.system('cp predictions.jpg static/classified/'+p_up_name)
			print(p_up_name)
			result_IMG = ''
			result_IMG = 'classified/'+p_up_name
			#os.system('rm classifieded_Object.txt')
			return render_template('jpg.html',filename = result_IMG ,filename1 = result_IMG ,caption=object,many_count = many_obj)
			#업로드된 파일에서 가장 많이 출연한 object의 이름과, 출연한 객체의 이름, 출연횟수를 반환
	else:
		error = 'error'

	return render_template('jpg.html')

@app.route('/mp4/',methods=['GET','POST'])
def mp4(username = None):
	error = None
	if request.method == 'POST':
		username = request.form['username']
		up_file = request.files['file']

		if up_file and allowed_file(up_file.filename):
			up_filename = secure_filename(up_file.filename)

			print(up_filename)

			log_filename = up_filename.split(".")[0]

			if os.path.exists("logfile/"+log_filename+".log") == False: #로그파일이 없다면 처음부터 다시 분류를 해야함

				up_file.save(os.path.join(app.config['UPLOAD_FOLDER'],up_filename))
				keyword = username

				index,fi_si = classified_MP4('static/'+up_filename,keyword,up_filename)

				return render_template('mp4.html',filename = 'classsified/detect.jpg',obj_name = keyword,caption = index,file_size = fi_si)

			else :#os.path.exists(log_filename+".log") == True:
				#로그파일이 존재하므로 바로 mpr_analysis를 통해 log파일을 분석하고 반환 (yolo를 통한 동영상분석 skip)
				keyword2 = username
				index, fi_si = mp4_analysis(keyword2 ,up_filename)
				return render_template('mp4.html',filename = 'classified/detect.jpg',obj_name = keyword2, caption = index, file_size = fi_si)

	else:
		error = 'error'
	return render_template('mp4.html')

@app.route('/',methods=['GET','POST'])
def main():
	os.system('rm static/classified/predictions.jpg')
	return render_template('main30.html')

if __name__ == '__main__':
	app.run(host='0.0.0.0', debug = True)
