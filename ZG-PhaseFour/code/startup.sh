DIR="$( cd "$( dirname "$0"  )" && pwd  )"
cd $DIR
SUFIX=`date '+%Y%m%d%H%M%S'`
chmod +x ./tools/parse_sstable
chmod +x ./tools/parse_recordio
nohup python spider.py > logs/spider_${SUFIX}.log &
