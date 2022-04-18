import os
import time
import datetime

os.system("rm imageData/*")
timeList = ["2022-01-27 22:30:00", "2022-02-23 04:00:00"]
startTime = time.strptime(timeList[0], "%Y-%m-%d %H:%M:%S")
startTime = datetime.datetime(startTime[0], startTime[1], startTime[2], startTime[3], startTime[4], startTime[5])
endTime = time.strptime(timeList[1], "%Y-%m-%d %H:%M:%S")
endTime = datetime.datetime(endTime[0], endTime[1], endTime[2], endTime[3], endTime[4], endTime[5])
curTime = startTime
docs = []
cnt = 0
while curTime < endTime:
    cnt += 1
    curTime += datetime.timedelta(minutes=30)
    if (os.path.exists("txtData/" + str(cnt) + ".txt")):
        print(cnt)
        os.system("wordcloud_cli --text txtData/" + str(cnt) + ".txt --imagefile imageData/" + str(cnt) + ".png")






