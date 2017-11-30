DIR="$( cd "$( dirname "$0"  )" && pwd  )"
cd $DIR
SUFFIX=`date +'%Y-%m-%d_%H%M%S'`
nohup python scheduler.py > logs/scheduler_${SUFFIX}.log 2>&1 &
