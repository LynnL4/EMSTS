#!/usr/bin/env python
# tary, 14:49 2018/10/18
import os
import sys
import oss2
import time

class log_uploader(object):
    def __init__(self):
        self.access_key_id = u"LTAItrcoENSSuy59"
        self.access_key_secret = u"sB1BygVCus6unjwLmPlkJ2lErvjqNp"
        self.bucket_name = u"meslogfiles"
        self.endpoint = u"oss-cn-hangzhou.aliyuncs.com"

    def uploadfile(self, fileName, localFile):
        auth = oss2.Auth(self.access_key_id, self.access_key_secret)
        bucket = oss2.Bucket(auth, self.endpoint, self.bucket_name)
        try:
            oss2.resumable_upload(bucket, fileName, localFile)
            time.sleep(0.1)

            file_exist_check = bucket.object_exists(fileName)
            if file_exist_check != True:
                return False
        except Exception as e:
            print(e)
            return False

        return True

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: {} filename filepath")
        quit(1)

    uploader = log_uploader()
    # uploader.uploadfile("113990554_1843000010_T201810191901_FAIL.log", "/var/schneider/113990554_1843000010_T201810191901_FAIL.log")
    uploader.uploadfile(sys.argv[1], sys.argv[2])
    quit(0)
