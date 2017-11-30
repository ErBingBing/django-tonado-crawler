# -*- coding: utf-8 -*-
import xlrd
import json
import sys
import os
import traceback
import re
#***********************************************
# 函数名： xls2json
# 输入参数：xls表格
# 输出参数：json文件文本
# 功能：   将固定的xls格式转为json文件
#***********************************************
def xls2json(xlsfilename,outfilename,encoding_override='utf-8'):
    myWorkbook=xlrd.open_workbook(xlsfilename,encoding_override=encoding_override)
    mySheets=myWorkbook.sheets()
    mySheet=mySheets[0]     #获取xls第一张表对象
    nrows=mySheet.nrows     #获取xls第一张表行数
    key=mySheet.row_values(0)
    #key=[item for item in key]
    #print 'xls第一张表行数:',nrows
    f=open(outfilename,'w+')
    try:
        for i in range(1,nrows):
            xpathlist = mySheet.row_values(i)
            newlist = []
            for item in xpathlist:
                if isinstance(item,int) or isinstance(item,float):
                    if int(item) == float(item):
                        item = str(int(item))
                    else:
                        item = str(item)
                newlist.append(item)
            oneline=dict(zip(key,newlist))
            f.write(json.dumps(oneline)+'\n')
    except:
        traceback.print_exc()
    finally:
        f.close()

if __name__ == '__main__':
    path = ''
    if not path:
        path = os.getcwd()
    filelist = os.listdir(path)
    for fp in filelist:
        if fp.endswith('.xls') or fp.endswith('.xlsx'):
            print 'xlsfilename:' + fp
            print 'outfilename:' + os.path.splitext(fp)[0] + '.json'
            xlsfilename=fp
            outfilename=os.path.splitext(fp)[0]+'.json'
            xls2json(xlsfilename, outfilename) 
    
