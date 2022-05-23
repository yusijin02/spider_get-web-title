# 合并csv
import time

print("[{}]".format(time.strftime("%H:%M:%S", time.localtime())) + "[INFO]Script uinon.py gets started.")
with open("RESULT.csv", "a", encoding="utf8") as resultFile:
    for i in range(50):
        print("[{}]".format(time.strftime("%H:%M:%S", time.localtime())) + "[INFO]Adding result{}.csv".format(i))
        with open("result{}.csv".format(i), "r", encoding="utf8") as sourceFile:
            for line in sourceFile:
                resultFile.write(line)
