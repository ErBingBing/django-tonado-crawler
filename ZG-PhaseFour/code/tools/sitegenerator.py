import os
import re


def getfilelist(dir, filelist=[]):
    newdir = dir
    if os.path.isfile(dir):
        filelist.append(dir.decode('gbk'))
    elif os.path.isdir(dir):
        for s in os.listdir(dir):
            newdir = os.path.join(dir, s)
            getfilelist(newdir, filelist)
    return filelist


if __name__ == '__main__':
    os.path.dirname(os.path.abspath(__file__))
    os.chdir('..')
    tempaltefile = 'tools/sitefactory.template'
    ofile = 'controller/sitefactory.py'

    # get all website
    filelist = getfilelist('website', [])
    clazzlist = []
    rec = re.compile('class ([0-9a-zA-Z]+)\(WebSite\)')
    for fl in filelist:
        with open(fl, 'r') as fp:
            for line in fp.readlines():
                if '(WebSite)' in line:
                    clazzlist.append(
                        {'package': fl[0:-3].replace('/', '.').replace('\\', '.'), 'clazz': re.findall(rec, line)[0]})
                    break

    with open(tempaltefile, 'r') as srcfp:
        with open(ofile, 'w') as dstfp:
            for line in srcfp.readlines():
                if line.startswith('C: '):
                    dstfp.write(line[3:])
                else:
                    for clazz in clazzlist:
                        dstfp.write(line[3:].format(package=clazz['package'], clazz=clazz['clazz']))
