nohup python3 robot.py >>bg.log 2>&1 &
ps -ef | grep robot | grep -v 'grep' | awk '{print $2}'
