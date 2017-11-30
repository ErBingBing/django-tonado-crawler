"""
Simple module for getting amount of memory used
by a specified user's processes on a UNIX system.
It uses UNIX ps utility to get the memory usage for
a specified username and pipe it to awk for summing up
per application memory usage and return the total.
Python's Popen() from subprocess module is used
for spawning ps and awk.
"""
import re
import subprocess

import time


class MemoryMonitor(object):
    def __init__(self):
        """Create new MemoryMonitor instance."""
        self.start = False

    def usage(self, keyword):
        """Return int containing memory used by user's processes."""
        self.process = subprocess.Popen(
            'ps -o pid,pcpu,vsz,rss,command | grep {keyword} | grep -v grep'.format(keyword=keyword),
            shell=True,
            stdout=subprocess.PIPE,
            )

        stdout_list = self.process.communicate()[0].split('\n')

        valid = False
        for line in stdout_list:
            if line.strip():
                valid = True
                print time.strftime('%Y-%m-%d %H:%M:%S\t') + re.sub('[\t\r\n ]+', '\t', line.strip())
                if not self.start:
                    self.start = True
        if not valid and self.start:
            return False
        return True


if __name__ == '__main__':
    memory_mon = MemoryMonitor()
    print 'TIME\tPID\tCPU\tVSZ\tRSS\tCOMMAND'
    while memory_mon.usage('spider.py'):
        time.sleep(10)
    # print used_memory
