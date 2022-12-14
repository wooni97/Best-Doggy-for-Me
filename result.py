import json
import boto3
import os
import uuid
import datetime

#사용자 문항 선택값 DB 저장
bucket = 'starsbucket' #S3버킷이름

def lambda_handler(event, context):
    
    # TODO implement
    user_id = str(uuid.uuid4())
    q1 = event["answer1"]
    q2 = event["answer2"]
    q3 = event["answer3"]
    q4 = event["answer4"]
    q5 = event["answer5"]
    q6 = event["answer6"]
    q7 = event["answer7"]
    q8 = event["answer8"]
    q9 = event["answer9"]
    q10 = event["answer10"]
    q11 = event["answer11"]
    q12 = event["answer12"]
    q13 = event["answer13"]
    q14 = event["answer14"]
    q15 = event["answer15"]
    q16 = event["answer16"]
    q17 = event["answer17"]
    q18 = event["answer18"]
    q19 = event["answer19"]
    q20 = event["answer20"]
    q21 = event["answer21"]
    q22 = event["answer22"]
    q23 = event["answer23"]
    q24 = event["answer24"]
    q25 = event["answer25"]
    q26 = event["answer26"]
    
    s3 = boto3.client("s3")
    
    
    lambda_path = "/tmp/1.txt"
    with open(lambda_path, 'w+') as file:
        file.write(user_id)
        file.close()
    s3.upload_file(lambda_path, bucket, "sub/user_id.txt")
    
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(os.environ['DB_TABLE_NAME'])
    table.put_item(
        Item = {
            "id" : user_id,
            "Q1" : q1,
            "Q2" : q2,
            "Q3" : q3,
            "Q4" : q4,
            "Q5" : q5,
            "Q6" : q6,
            "Q7" : q7,
            "Q8" : q8,
            "Q9" : q9,
            "Q10" : q10,
            "Q11" : q11,
            "Q12" : q12,
            "Q13" : q13,
            "Q14" : q14,
            "Q15" : q15,
            "Q16" : q16,
            "Q17" : q17,
            "Q18" : q18,
            "Q19" : q19,
            "Q20" : q20,
            "Q21" : q21,
            "Q22" : q22,
            "Q23" : q23,
            "Q24" : q24,
            "Q25" : q25,
            "Q26" : q26
            
        })
        
    sns = boto3.client('sns')
    sns.publish(
        TopicArn = os.environ['SNS_TOPIC'],
        Message = user_id
        )

        
    return {
        'statusCode': 200,
        'body': user_id
    }
