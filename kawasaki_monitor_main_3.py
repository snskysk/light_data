# coding: UTF-8
import os
import json
from urllib.parse import unquote_plus
import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

from googleapiclient.discovery import build 
from googleapiclient.http import MediaFileUpload 
from oauth2client.service_account import ServiceAccountCredentials
import time
import datetime
import cv2


def takepic_up_del_File2GoogleDrive(fileName, localFilePath):
    interval = cf["interval"]
    error_interval = cf["error_interval"]
    device_num = cf["device_num"]
    count = 0
    error_count = 0
    delay=1
    window_name='frame'


    while True:
        # caption windowの立ち上げ
        cap = cv2.VideoCapture(device_num)
        if not cap.isOpened():
            print("cap not open")
        ret, frame = cap.read()
        # cv2.imshow(window_name, frame)

        if judge_active_time_or_not():
            print("\r"+"---processing now---",end="")
            try:
                # captin windowの静止画を保存
                cv2.imwrite(fileName, frame)
                time.sleep(2)

                # ファイルアップロード
                ext = os.path.splitext(localFilePath.lower())[1][1:]
                if ext == "jpg":
                    ext = "jpeg"
                mimeType = "image/" + ext

                service = getGoogleService()
                file_metadata = {"name": fileName, "mimeType": mimeType, "parents": ["12InHgdlWLXQPetS3jWfyW1Au9zdLXxV3"] } 
                media = MediaFileUpload(localFilePath, mimetype=mimeType, resumable=True) 
                file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
                file_id =file["id"]
                time.sleep(interval - 2)

                # ファイル削除
                file = service.files().delete(fileId=file_id).execute()
                count += 1

            except Exception as e:
                logger.exception(e)
                error_count += 1
                if error_count > 10:
                    break
                time.sleep(error_interval)
        else:
            print("\r"+"---sleeping now---",end="")
            time.sleep(3600)
        cv2.destroyWindow(window_name)




# アクティブ時間か否かを確認し、ブールを返す
def judge_active_time_or_not():
    dt_now = datetime.datetime.now()
    if cf["active_hour"] <= dt_now.hour and dt_now.hour < cf["deactive_hour"]:
        active_flag = True
    else:
        active_flag = False
    return active_flag

# 認証の関数
# 参考：https://qiita.com/w2or3w/items/b66a4a8e45e6001a9c46
def getGoogleService():
    scope = ['https://www.googleapis.com/auth/drive.file'] 
    keyFile = 'kawasaki_monitor_key.json'
    credentials = ServiceAccountCredentials.from_json_keyfile_name(keyFile, scopes=scope)

    return build("drive", "v3", credentials=credentials, cache_discovery=False) 


cf = {
    "active_hour":10,
    "deactive_hour":16,
    "interval":30,
    "error_interval":20,
    "device_num":0
}

file_name = "monitoring.jpg"
localFilePath = "home/dlinano/workspace/kawasaki_monitor/" + file_name

# uploadFileToGoogleDrive(file_name, localFilePath)
takepic_up_del_File2GoogleDrive(file_name, localFilePath)

# file_id = "1yplyj4VIqYNzHe4r4mDqhPnX9H8YYj-u"
# deleteFileToGoogleDrive(file_name, localFilePath, file_id)


