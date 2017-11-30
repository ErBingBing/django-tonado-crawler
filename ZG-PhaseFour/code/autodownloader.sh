DIR="$( cd "$( dirname "$0"  )" && pwd  )"
cd $DIR
SUFIX=`date '+%Y%m%d%H%M%S'`
chmod +x ./autodownloader/phantomjs/bin/phantomjs
nohup python autodownloader.py > logs/autodownloader_${SUFIX}.log &