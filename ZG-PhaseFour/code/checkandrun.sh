DIR="$( cd "$( dirname "$0"  )" && pwd  )"
cd $DIR
SUFIX=`date '+%Y%m%d%H%M%S'`
nohup python checkandrun.py > logs/checkandrun_${SUFIX}.log &
