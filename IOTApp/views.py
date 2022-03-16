import json
import apis.aep_device_command
import apis.aep_rule_engine
import apis.aep_device_status
from django.shortcuts import render
from django.http.response import JsonResponse
import pymysql
import time as t

# Create your views here.
#################### device info
appKey = 'Qs72DtRJvWf'
appSecret = 'uaqJk969pK'
MasterKey = '02e68a26acbf4c9da217cf85fb8deb44'
tenantId = '2000057055'
productId = '15101722'
deviceId = '39c054ca43e248519d0e73ed9130c3a8'
ruleIdAlarm = '99ed150c-944f-c14d-5467-980f3b3cf396'
ruleIdNorm = '4b1f2217-f067-dec0-2b12-05906e409cd5'

operator = "Server"

##### database
db_user = "root"
db_password = "123"
database = "iot"
host = "localhost"

###name_list
device_data_name_list = ['time','humidity_data','temperature_data']

def index(request):
    '''主页'''
    return render(request, "index.html")

def execute(sql):
    '''执行sql语句'''
    db = pymysql.connect(user=db_user, password=db_password, database=database, host=host)
    cursor = db.cursor()
    try:
        cursor.execute(sql)
        db.commit()
        mark = True
    except:
        db.rollback()
        mark = False
    db.close()
    return mark

def select(sql):
    '''显示信息'''
    db = pymysql.connect(user=db_user, password=db_password, database=database, host=host)
    cursor = db.cursor()
    cursor.execute(sql)
    results = cursor.fetchall()
    db.close()
    return results

def insert(sql):
    '''插入信息'''
    return execute(sql)

def delete(sql):
    '''删除信息'''
    return execute(sql)

def generateDictData(result,name_list):
    '''根据sql结果和列名生成字典'''
    dict = {}
    assert len(result) == len(name_list)
    for i in range(len(result)):
        dict[name_list[i]] = result[i]
    return dict

def motor_control(request=None,control_int=None):
    '''远程控制电机转动'''
    if request:
        control_int = request.GET.get("control_int")
    body = {
        "content": {
            "params":{
                "control_int":control_int
            },
            "serviceIdentifier":"motor_control"
        },
        "deviceId": deviceId,
        "operator": operator,
        "productId": productId,
        "ttl": 7200,
        "deviceGroupId":None,
        "level": 1
    }
    body = json.dumps(body)
    result = apis.aep_device_command.CreateCommand(appKey=appKey, appSecret=appSecret, MasterKey=MasterKey, body=body)
    result = json.loads(result)
    if int(control_int) == 1:
        print("##################################")
        print("#############已启动电机#############")
        print("##################################")
    else:
        print("##################################")
        print("#############已关闭电机#############")
        print("##################################")
    if request:
        return JsonResponse(result,safe=False)
    return result

def led_control(request=None,control_int=None):
    '''远程控制led闪烁'''
    if request:
        control_int = request.GET.get("control_int")
    body = {
        "content": {
            "params":{
                "control_int":control_int
            },
            "serviceIdentifier":"led_control"
        },
        "deviceId": deviceId,
        "operator": operator,
        "productId": productId,
        "ttl": 7200,
        "deviceGroupId":None,
        "level": 1
    }
    body = json.dumps(body)
    result = apis.aep_device_command.CreateCommand(appKey=appKey, appSecret=appSecret, MasterKey=MasterKey, body=body)
    result = json.loads(result)
    if int(control_int) == 1:
        print("##################################")
        print("#############已启动LED#############")
        print("##################################")
    else:
        print("##################################")
        print("#############已关闭LED#############")
        print("##################################")
    if request:
        return JsonResponse(result, safe=False)
    return result

def alarm_control(request):
    '''远程控制报警'''
    assert request
    control_int = request.GET.get("control_int")
    if int(control_int) == 1:
        stopRule(ruleIdAlarm)
        stopRule(ruleIdNorm)
        print("##################################")
        print("#############已关闭规则#############")
        print("##################################")
    else:
        startRule(ruleIdAlarm)
        startRule(ruleIdNorm)
        print("##################################")
        print("#############已开启规则#############")
        print("##################################")
    result_motor = motor_control(request=None,control_int=control_int)
    result_led = led_control(request=None,control_int=control_int)
    if int(control_int) == 1:
        print("##################################")
        print("#############已启动报警#############")
        print("##################################")
    else:
        print("##################################")
        print("#############已关闭报警#############")
        print("##################################")
    return JsonResponse([result_motor,result_led],safe=False)

def report_control(request):
    '''远程控制数据上报启动'''
    control_int = request.GET.get("control_int")
    body = {
        "content": {
            "params": {
                "control_int": control_int
            },
            "serviceIdentifier": "report_control"
        },
        "deviceId": deviceId,
        "operator": operator,
        "productId": productId,
        "ttl": 7200,
        "deviceGroupId": None,
        "level": 1
    }
    body = json.dumps(body)
    result = apis.aep_device_command.CreateCommand(appKey=appKey, appSecret=appSecret, MasterKey=MasterKey, body=body)
    result = json.loads(result)
    if int(control_int) == 1:
        print("##################################")
        print("#############已启动上报#############")
        print("##################################")
    else:
        print("##################################")
        print("#############已关闭上报#############")
        print("##################################")
    return JsonResponse(result, safe=False)

def show_data(request):
    '''从MySQL中获取所有的温湿度数据'''
    data = []
    sql = "select * from device_data"
    results = select(sql)
    assert results
    for result in results:
        data.append(generateDictData(result,device_data_name_list))
    return JsonResponse(data=data,safe=False)

def show_new_data(request):
    '''主动获取最新的温湿度数据'''
    body = {
        "productId": productId,
        "deviceId": deviceId,
        "datasetId": "humidity_data",
    }
    body = json.dumps(body)
    result = json.loads(apis.aep_device_status.QueryDeviceStatus(appKey=appKey, appSecret=appSecret, body=body))
    humidity_data = result.get("deviceStatus").get("value")
    body = {
        "productId": productId,
        "deviceId": deviceId,
        "datasetId": "temperature_data",
    }
    body = json.dumps(body)
    result = json.loads(apis.aep_device_status.QueryDeviceStatus(appKey=appKey, appSecret=appSecret, body=body))
    temperature_data = result.get("deviceStatus").get("value")
    time_stamp = result.get("deviceStatus").get("timestamp")
    time = change_time_stamp(time_stamp)
    data = generateDictData([time,humidity_data,temperature_data],device_data_name_list)
    return JsonResponse(data,safe=False)

def change_time_stamp(time_stamp):
    time_stamp = int(time_stamp) / 1000
    time_stamp = t.localtime(time_stamp)
    time = t.strftime("%Y-%m-%d %H:%M:%S", time_stamp)
    return time

def get_data(request):
    '''接收CTwing平台推送的温湿度数据'''
    data = request.body
    assert data
    result = json.loads(data)
    time_stamp = result.get('timestamp')
    time = change_time_stamp(time_stamp)
    humidity_data = result.get('payload').get('humidity_data')
    temperature_data = result.get('payload').get('temperature_data')
    sql = "insert into device_data (time,humidity_data,temperature_data) values ('%s','%s','%s')" \
          % (time,humidity_data,temperature_data)
    #Todo 定期清理MySQL
    mark = insert(sql)
    if mark:
        print("##################################")
        print("#############成功写入MySQL#############")
        print("##################################")
    return JsonResponse(mark,safe=False)

def threshold_set(request):
    '''设置规则阈值'''
    humidity_data = int(request.GET.get("humidity_data"))
    temperature_data = int(request.GET.get("temperature_data"))
    stopRule(ruleIdAlarm)
    stopRule(ruleIdNorm)
    print("##################################")
    print("#############已关闭规则#############")
    print("##################################")
    updateAlarmRule(humidity_data,temperature_data)
    updateNormRule(humidity_data,temperature_data)
    print("##################################")
    print("#############已修改规则#############")
    print("##################################")
    startRule(ruleIdAlarm)
    startRule(ruleIdNorm)
    print("##################################")
    print("#############已开启规则#############")
    print("##################################")
    return JsonResponse(data=True,safe=False)

def updateAlarmRule(humidity_data,temperature_data):
    assert type(humidity_data) == int
    ruleStr = "SELECT humidity_data, temperature_data FROM ruleengine_2000057055_15101722 " \
              "WHERE deviceId() = '39c054ca43e248519d0e73ed9130c3a8' AND humidity_data > %d OR temperature_data > %d"\
              % (humidity_data,temperature_data)
    body = {
        "ruleId": ruleIdAlarm,
        "dataLevel": 1,
        "description": "报警",
        "ruleStreams": [
            {
                "productId": productId,
                "deviceId": deviceId,
                "deviceGroupId": None,
                "ruleStr": ruleStr,
                "dataLevel": 1
            }
        ],
        "ruleType": 1000
    }
    body = json.dumps(body)
    result = apis.aep_rule_engine.UpdateRule(appKey, appSecret, body)
    result = json.loads(result)
    return result

def updateNormRule(humidity_data,temperature_data):
    ruleStr = "SELECT humidity_data, temperature_data FROM ruleengine_2000057055_15101722 " \
              "WHERE deviceId() = '39c054ca43e248519d0e73ed9130c3a8' " \
              "AND humidity_data <= %d AND temperature_data <= %d" %(humidity_data,temperature_data)
    body = {
        "ruleId": ruleIdNorm,
        "dataLevel": 1,
        "description": "关闭报警",
        "ruleStreams": [
            {
                "productId": productId,
                "deviceId": deviceId,
                "deviceGroupId": None,
                "ruleStr": ruleStr,
                "dataLevel": 1,
            }
        ],
        "ruleType": 1000,
    }
    body = json.dumps(body)
    result = apis.aep_rule_engine.UpdateRule(appKey, appSecret, body)
    result = json.loads(result)
    return result

def createRule():
    body = {
        "dataLevel": 1,
        "description": "报警",
         "ruleStreams": [
             {
                 "productId": productId,
                 "deviceId": deviceId,
                 "ruleStr": "SELECT humidity_data, temperature_data FROM ruleengine_2000057055_15101722 "
                            "WHERE deviceId() = '39c054ca43e248519d0e73ed9130c3a8' AND humidity_data > 80 AND temperature_data > 45",
                 "dataLevel": 1
             }
         ],
        "ruleType": 1000,
        "creator": operator
    }
    body = json.dumps(body)
    result = apis.aep_rule_engine.CreateRule(appKey=appKey,appSecret=appSecret,body=body)
    result = json.loads(result)
    print(result)

def stopRule(ruleId):
    body = {
        "ruleId": ruleId,
        "runningStatus": "1100"
    }
    body = json.dumps(body)
    result = apis.aep_rule_engine.UpdateRuleRunStatus(appKey, appSecret, body)
    result = json.loads(result)
    print(result)

def startRule(ruleId):
    body = {
        "ruleId": ruleId,
        "runningStatus": "1000"
    }
    body = json.dumps(body)
    result = apis.aep_rule_engine.UpdateRuleRunStatus(appKey, appSecret, body)
    result = json.loads(result)
    print(result)

def deleteRule(ruleId):
    body = {
        "ruleId":ruleId
    }
    body = json.dumps(body)
    result = apis.aep_rule_engine.DeleteRule(appKey,appSecret,body)
    result = json.loads(result)
    print(result)


def TEST(request):
    startRule(ruleIdAlarm)
    startRule(ruleIdNorm)
    return JsonResponse(True,safe=False)
