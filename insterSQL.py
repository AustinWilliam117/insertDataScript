"""多进程"""
from datetime import datetime, timedelta
from multiprocessing import cpu_count, Pool
from tqdm import tqdm
import gc
import pymysql
import random
import uuid
import os

"""链接数据库"""
db_config = {
    'host':'10.54.0.28',
    'user':'root',
    'password':'Pachira@123',
    'database':'x86_27_all_bj',
    'port':3307,
    'charset':'utf8mb4',
    'autocommit':True,
    'local_infile':1 # 数据库权限问题
}

call_label = ['SMS_测试', '未完成调研', '完成调研', '机主本人', '完成调研未打分', '差评', '电话', '肯定', '否定',
              '赞同', '举报', '反对', '支持', '同意', '宽带', '回家']

"""随机生成uuid"""
def create_uuid():
    uid = uuid.uuid4()
    return uid

"""随机生成手机号"""
def create_phone():
    # 第二位数字
    second = [3, 4, 5, 7, 8][random.randint(0, 4)]

    # 第三位数字
    third = {3: random.randint(0, 9),
             4: [5, 7, 9][random.randint(0, 2)],
             5: [i for i in range(10) if i != 4][random.randint(0, 8)],
             7: [i for i in range(10) if i not in [4, 9]][random.randint(0, 7)],
             8: random.randint(0, 9),
             }[second]

    # 最后八位数字
    suffix = random.randint(9999999, 100000000)

    # 拼接手机号
    return "1{}{}{}".format(second, third, suffix)

"""随机返回call_label"""
def label():
    labelList = random.sample(call_label, 5)
    # 将列表转换成字符串
    result = ','.join(labelList)
    return result

"""获取当前时间"""
def get_now(after: int):
    # 获取当前时间
    now = datetime.strptime("2023-09-01 16:53:04", "%Y-%m-%d %H:%M:%S")
    now = now + timedelta(days=after)
    # print(now)
    formatTime = now.strftime("%Y-%m-%d %H:%M:%S")
    return formatTime

"""随机性别"""
def get_gender():
    gender_list = ['男', '女']
    return random.choice(gender_list)

"""随机呼叫状态"""
def call_status():
    call_status_list = ['正常挂机', '强制挂机', '识别错误挂断', '对方拒接', '超时未接听', '超时挂机']
    return random.choice(call_status_list)

"""是否达成意向"""
def get_success():
    get_success_list = ['1', '0']
    return random.choice(get_success_list)

"""挂机原因"""
def disconnect_reason():
    disconnect_reason_list = ['主动挂机']
    return random.choice(disconnect_reason_list)

"""提交数据库"""
# 文件路径 和 表名
def commitDB(data_file, table_name):
    # 连接数据库
    conn = pymysql.connect(**db_config)
    #cur = db.cursor()

    # 使用 load data file 加载数据
    loadData = f"LOAD DATA LOCAL INFILE '{data_file}' INTO TABLE {table_name} FIELDS TERMINATED BY '\\t' ENCLOSED BY '\"' LINES TERMINATED BY '\\n';"
    #print("========================")
    #print(loadData)
    #print("========================")
    try:
        with conn.cursor() as cursor:
            cursor.execute("use x86_27_all_bj;")
            conn.commit()
            cursor.execute(loadData)
            conn.commit()
        # cur.execute(loadData)
        # db.commit()
            print(data_file,table_name,"数据加载成功")
    except Exception as err:
        print(f"数据加载失败: {err}")
        
    conn.close()
    # cur.close()
    # db.close()

"""常用参数"""
robot_flow = '1bd056e8e9a948a9933c649e4612b6a1'
caller = '10086'
call_type = 'out'
duration = '100'  # 通话时长
talk_times = '12'
province = '311' # 省份ID 上海210
department = '336' # 所属用户组
current_count = '0' # 并发数
flow_path = '开场白_询问是否本人-是机主本人_询问是否登门检测-已登门_请客户评价上门服务-通用_未理解-1_6分_致歉_询问不满意原因-低分原因_致歉_结束语1'
cmos_modify_time = '2023-06-14 05:57:19.155'
slots_info = '{\"sayRengongCount\": 0, \"四分\": \"\", \"六分\": \"\", \"三分\": \"3\", \"两分\": \"\", \"五分\": \"\", \"一分\": \"\", \"服务品质问题\": \"\", \"宽带类问题\": \"网速不好\", \"手机上网及套餐资费问题\": \"\", \"互联网电视问题\": \"\", \"遥控器问题\": \"\", \"看家宝问题\": \"\"}'

interaction1 = '尊敬的客户您好，我是中国移动工作人员，来电是想对您做一个简单的服务回访，大概耽误您两分钟时间，请问,尾号1143的号码是您在用吗?'
interaction2 = '<audio src=\'/zyzx/scjkdbhhf/是机主本人_询问是否登门检测.wav\'>嗯，首先想请问一下，最近有没有中国移动的工作人员为您提供上门检测的服务呢?</audio>'
interaction3 = '<audio src=\'/zyzx/scjkdbhhf/已登门_请客户评价上门服务.wav\'>好的，那请您对本次上门服务及处理结果进行评价，10分代表非常满意，1分代表非常不满意，1到10分您打几分呢？</audio>'
interaction4 = '<audio src=\"/zyzx/scjkdbhhf/通用_用户未说话1.wav\">您好，</audio>|<audio src=\'/zyzx/scjkdbhhf/已登门_请客户评价上门服务_引导.wav\'>10分代表非常满意，1分代表非常不满意，1到10分，您对本次上门服务及处理结果打几分呢？</audio>'
interaction5 = '<audio src=\'/zyzx/scjkdbhhf/1_6分_致歉_询问不满意原因.wav\'>非常抱歉给您带来了不好的体验了，您觉得您的宽带还有哪方面不太好呢？</audio>'
interaction6 = '<audio src=\'/zyzx/scjkdbhhf/低分原因_致歉_结束语.wav\'>很抱歉给您带来的不好体验，若您后续有任何使用问题，可随时拨打10086，感谢您长期以来对移动的支持，服务就在身边，初心从未改变。一点一滴，为您十分满意。祝您生活愉快，再见。</audio>'

musicURL = 'http://192.168.130.253:9110/audiolistening/5s.wav?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=Y11K6AH43N6G29LX6X93%2F20230626%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20230626T103805Z&X-Amz-Expires=604800&X-Amz-Security-Token=eyJhbGciOiJIUzUxMiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3NLZXkiOiJZMTFLNkFINDNONkcyOUxYNlg5MyIsImV4cCI6MTY4NzgxOTAzMiwicGFyZW50IjoibWluaW8ifQ.rq0TSPF5bS7up07tMP5eBVw7NplzRvFVT_LFDVelrdr89HnfSJew_i0y-Oci4t0O6-zaxqmCIGfp1a8SmZ-g8Q&X-Amz-SignedHeaders=host&versionId=null&X-Amz-Signature=7b221d2c46e66ad4b40daa773c906a089bd12a11d6d42cbc1a935fdf626a0568'

def alternate():
    if not hasattr(alternate, 'counter'):
        alternate.counter = 0

    if alternate.counter % 2 == 0:
        alternate.counter += 1
        return "caller"
    else:
        alternate.counter += 1
        return "called"

"""初始化TXT"""
def writeTxtInit(formatTime1, fileName, list):
    txtPath = baseFile + '/' + formatTime1 + '/' + fileName + '.txt'
    #print(txtPath)
    with open(txtPath, 'a+', encoding='utf-8') as f:
        f.write(list + '\n')

"""写入TXT"""
def writeTxt(formatTime1, fileName, list):
    txtPath = baseFile + '/' + formatTime1 + '/' + fileName + '.txt'
    with open(txtPath, 'a+', encoding='utf-8') as f:
        f.write(list + '\n')

"""创建文件夹"""
def createDir(path):
    folder = os.path.exists(path)

    if not folder:
        os.mkdir(path)
        print(path, " 创建完成")
    else:
        print(path, " 该文件夹已经存在")

id1 = 50003
id2 = 50003
id3 = 50003

"""自增ID"""
def increaseID1():
    global id1
    id1 += 1
    return str(id1)

"""自增ID"""
def increaseID2():
    global id2
    id2 += 1
    return str(id2)

"""自增ID"""
def increaseID3():
    global id3
    id3 += 1
    return str(id3)

if __name__ == '__main__':
    # 程序使用CPU开始时间
    start=datetime.now()
    
    baseFile = '/var/lib/mysql-files/data'
    #baseFile = r"C:\Users\William\Desktop\data"

    # 初始list字段
    dataListSQL1_initList = '"id"	"call_id"	"robot_flow"	"caller"	"called"	"call_type"	"start_time"	"end_time"	"duration"	"call_status"	"talk_times"	"call_label"	"slots_info"	"gender"	"province"	"faq_label"	"flow_path"	"department"	"disconnect_reason"	"current_count"	"variabules"	"is_success"	"cmos_modify_time"'
    dataListSQL2_initList = '"id"	"call_id"	"talker"	"content"	"talk_at"	"label_name"	"uuid"	"file_url"	"prompt_name"	"task_name"	"cmos_modify_time"'
    dataListSQL3_initList = '"call_id"	"call_label"	"id"	"cmos_modify_time"'
    
    # al_job、al_mat、al_tag list数据
    dataListSQL1 = ''
    dataListSQL2 = ''
    dataListSQL3 = ''
    start_date = datetime.strptime("2023-09-11 16:53:04", "%Y-%m-%d %H:%M:%S")
    end_date = start_date + timedelta(days=7)  # 30天后
    current_date = start_date
    while current_date <= end_date:
        # 获取当前日期的字符串形式
        formatTime = current_date.strftime("%Y-%m-%d %H:%M:%S")
        # 每天生成一个时间，写入文本中
        formatTime1 = formatTime.split()[0]

        # 创建日期目录
        dirPath = os.path.join(baseFile, formatTime1)
        os.makedirs(dirPath, exist_ok=True)  # 创建目录，如果已存在则忽略

        # 初始化文件
        #writeTxtInit(formatTime1, 'dataListSQL1', dataListSQL1_initList)
        #writeTxtInit(formatTime1, 'dataListSQL2', dataListSQL2_initList)
        #writeTxtInit(formatTime1, 'dataListSQL3', dataListSQL3_initList)

        # 每天生成50w数据
        for i in range(0, 500000):
            uid = str(create_uuid())
            # 随机拿5个call_label
            labelValues = label()
            
            # dataListSQL1 = (uid, robot_flow, caller, create_phone(), call_type, formatTime, formatTime, duration,
            #                     call_status(), talk_times, labelList, slots_info, get_gender(), province, flow_path,
            #                     department, disconnect_reason(), current_count, cmos_modify_time, get_success())
            dataListSQL1 = '"'+increaseID1() +'"\t"'+ uid +'"\t"'+ robot_flow +'"\t"'+ caller +'"\t"'+ create_phone() +'"\t"'+ call_type +'"\t"'+ formatTime +'"\t"'+ \
                            formatTime +'"\t"'+ duration +'"\t"'+ call_status() +'"\t"'+ talk_times +'"\t"'+ labelValues +'"\t"'+ \
                            slots_info +'"\t"'+ get_gender() +'"\t"'+ province +'"\t\t"'+ flow_path +'"\t"'+ department +'"\t"'+ \
                            disconnect_reason() +'"\t"'+ current_count +'"\t"'+ "0" +'"\t"'+ get_success() +'"\t"'+ cmos_modify_time +'"'
            #print(dataListSQL1)
            
            writeTxt(formatTime1, 'dataListSQL1', dataListSQL1)

            for value in range(10):
                # dataListSQL2 = (uid, alternate(), interaction1, formatTime, labelValues, uid, musicURL,
                #                 '1_6分_致歉_询问不满意原因', cmos_modify_time)
                dataListSQL2 = '"'+increaseID2() +'"\t"'+ uid +'"\t"'+ alternate() +'"\t"'+ interaction1 +'"\t"'+ formatTime +'"\t"'+ labelValues +'"\t"'+ uid +'"\t"'+ musicURL +'"\t\t"'+ \
                                '1_6分_致歉_询问不满意原因' +'"\t"'+ cmos_modify_time+'"'
                #print(dataListSQL2)
                writeTxt(formatTime1, 'dataListSQL2', dataListSQL2)

            # 将label字符串转成列表
            labelValues = labelValues.split(',')
            
            for value in labelValues:
                # dataListSQL3 = (uid, value, '2022-06-21 11:23:23.467')
                dataListSQL3 = '"'+ uid +'"\t"'+ value +'"\t"'+increaseID3()+ '"\t"'+ '2022-06-21 11:23:23.467'+'"'
                #print(dataListSQL3)
                writeTxt(formatTime1, 'dataListSQL3', dataListSQL3)
            
        # 提交数据库
        txtPath = baseFile + '/' + formatTime1 + '/' + 'dataListSQL1' + '.txt'
        #print(txtPath)
        commitDB(txtPath, 'al_job_202309')
        # 提交数据库
        txtPath = baseFile + '/' + formatTime1 + '/' + 'dataListSQL2' + '.txt'
        commitDB(txtPath, 'al_mat_202309')
        # 提交数据库
        txtPath = baseFile + '/' + formatTime1 + '/' + 'dataListSQL3' + '.txt'
        commitDB(txtPath, 'al_tag_202309')

        # 循环结束加1天
        current_date += timedelta(days=1)

    # 程序使用CPU结束时间
    end=datetime.now()
    # 打印耗时
    print('Running time: %s Seconds'%(end-start))

