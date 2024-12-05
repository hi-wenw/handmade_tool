import pyautogui
import time
import os

# 定义等待时间（30分钟）
wait_time = 15 * 60  # 30分钟转化为秒

# 等待30分钟
time.sleep(wait_time)

# 锁屏（Windows）
os.system("rundll32.exe user32.dll,LockWorkStation")

# 如果是在Mac上，可以使用下面的命令
# os.system_tool("pmset displaysleepnow")