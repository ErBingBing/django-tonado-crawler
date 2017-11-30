DIR="$( cd "$( dirname "$0"  )" && pwd  )"
cd $DIR
SUFFIX=`date +'%Y-%m-%d_%H%M%S'`
nohup python downloader.py > logs/downloader_${SUFFIX}.log 2>&1 &
