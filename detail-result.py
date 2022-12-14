from urllib.request import Request, urlopen
from urllib.parse import urlencode, quote_plus, unquote
from bs4 import BeautifulSoup
import urllib.request
import requests 
import xmltodict
import json
import os
import random

from datetime import datetime
import boto3
from boto3.dynamodb.conditions import Key, Attr

# ** 결과 페이지의 내용 가져오기 **


#query문. 
def get_request_query(url, operation, params, serviceKey):
    import urllib.parse as urlparse
    params = urlparse.urlencode(params)
    request_query = url + '/' + operation + '?' + params + '&' + 'serviceKey' + '=' + serviceKey
    return request_query
    
def Crawling_bigstars(dogname):
    
    url = "https://dogtime.com/dog-breeds/" + dogname
    req = urllib.request.Request(url, headers = {'User-Agent': 'Mozilla/5.0(Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.3'})

    response = urllib.request.urlopen(req).read()
    text = response.decode('utf-8')
    soup = BeautifulSoup(response, "html.parser")
    soup = soup.find_all("div", class_="star")
    star_list = []
    for s in soup:
        if s.text.strip()== '':
            stars = s.get("class")
            star_list.append(stars[1][-1])

    return star_list
    
    # img = s.find("div")
    # img_src = img.get("class")


def lambda_handler(event, context):
    bucket = 'starsbucket' #S3버킷이름
    s3 = boto3.client("s3")

    file_obj = s3.get_object(Bucket=bucket, Key='sub/dognumber.txt')
    num = file_obj["Body"].read().decode("utf-8")
    print(num)

    
    file_obj = s3.get_object(Bucket=bucket, Key='sub/user_local.txt')
    addr = file_obj["Body"].read().decode("utf-8")
    print(addr)
    
    file_obj = s3.get_object(Bucket=bucket, Key='sub/user_id.txt')
    user_id = file_obj["Body"].read().decode("utf-8")
    print(user_id)
    
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(os.environ['DB_TABLE_NAME2'])
    items = table.query(
            KeyConditionExpression=Key('id').eq(user_id))
    #print(items)
            
    dogs = []
    dogs.append(items["Items"][0]["first_dogname"])
    dogs.append(items["Items"][0]["second_dogname"])
    dogs.append(items["Items"][0]["third_dogname"])
    
    # dogs_eng =[]
    # dogs_eng.append(items["Items"][0]["first_engname"])
    # dogs_eng.append(items["Items"][0]["first_engname"])
    # dogs_eng.append(items["Items"][0]["first_engname"])

    
    #test 결과값으로 대입되는 변수
    if (num=="0"):
        dogName = items["Items"][0]["first_dogname"]
        dogName_eng = items["Items"][0]["first_engname"]
        dog_pic = items["Items"][0]["first_pic"]
    elif (num=="1"):
        dogName = items["Items"][0]["second_dogname"]
        dogName_eng = items["Items"][0]["second_engname"]
        dog_pic = items["Items"][0]["second_pic"]
    elif (num=="2"):
        dogName = items["Items"][0]["third_dogname"]
        dogName_eng = items["Items"][0]["third_engname"]
        dog_pic = items["Items"][0]["third_pic"]
        
    print(dogName)
    print(dogName_eng)
    
    star_list = []
    star_list = Crawling_bigstars(dogName_eng)
    print(star_list)
    
    star_data ={
        "dog_name" : dogName_eng,
        "dog_pic" : dog_pic,
        "adap" : star_list[0],
        "frinedli" : star_list[1],
        "health" : star_list[2],
        "trainability" : star_list[3],
        "physical" : star_list[4]
    }
    

    # 요청 URL과 오퍼레이션
    URL = 'http://openapi.animal.go.kr/openapi/service/rest/abandonmentPublicSrvc'
    # 파라미터
    SERVICEKEY = '9arJX1LMN1qodyehGW%2FUvqD0CGVdEXuNYt0ziiFKYTo9wURtceTYB3BrUd%2B%2FsvytNiHfEPDii5RYeRRuOLUVAA%3D%3D'
    
    sido = addr
    
    # 견종 가져오기
    PARAMS = {'up_kind_cd': '417000'}
    OPERATION = 'kind'
    request_query = get_request_query(URL, OPERATION, PARAMS, SERVICEKEY)
    response = requests.get(url=request_query)
    
    dict_type = xmltodict.parse(response.content)
    json_type = json.dumps(dict_type)
    dict2_type = json.loads(json_type)
    
    body = dict2_type['response']['body']
    items = body['items']
    
    boolean = False
    for item in items["item"]:
        if item['KNm'] == dogName:
            boolean = True
            kind = item['kindCd']
        
    
    if boolean == False:
        kind = '000114'     #매칭되는 견종이 없을 경우 믹스견과 매칭.
    
    SIDO = {'서울특별시': '6110000', '부산광역시': '6260000', '대구광역시': '6270000', '인천광역시': '6280000', '광주광역시': '6290000', '세종특별자치시': '5690000',
            '대전광역시': '6300000', '울산광역시': '6310000', '경기도': '6410000', '강원도': '6420000'}
    uprCd = SIDO[sido]
    
    #날짜 계산 식 분명 잘되었는데... 갑자기 에러남..
    #date = format(datetime.today().year) + '0' + format(datetime.today().month -1) + format(datetime.today().day)
    #PARAMS = {'bgnde': date, 'upkind': '417000', 'kind': kind, 'state': 'notice', 'upr_cd': uprCd}
   
    OPERATION = 'abandonmentPublic'  # 오퍼레이션 이름.
    PARAMS = {'upkind': '417000', 'kind': kind, 'state': 'notice', 'upr_cd': uprCd}
    request_query = get_request_query(URL, OPERATION, PARAMS, SERVICEKEY)
    response = requests.get(url=request_query)
    
    dict_type = xmltodict.parse(response.content)
    json_type = json.dumps(dict_type)
    dict2_type = json.loads(json_type)
    
    body = dict2_type['response']['body']
    items = body['items']

    #매칭되는 견종은 있으나 보호중인 유기견이 없을 경우.
    if items is None:
        
        kind = '000114'  
        PARAMS = {'upkind': '417000', 'kind': kind, 'state': 'notice', 'upr_cd': uprCd}
        request_query = get_request_query(URL, OPERATION, PARAMS, SERVICEKEY)
        response = requests.get(url=request_query)
    
        dict_type = xmltodict.parse(response.content)
        json_type = json.dumps(dict_type)
        dict2_type = json.loads(json_type)
    
        body = dict2_type['response']['body']
        items = body['items']
        
    if kind == '000114' :
        index = random.randint(0, 4)
    else:
        index = 0
        
        # return {
        #     'body': '보호중인 유기견이 없네요..'        #다음 순위의 유기견 데이터들을 가져오도록 수정해야..
        # }   
    item = items["item"][index]
    item.update(star_data)
    return {
        'body':item
    }

    
