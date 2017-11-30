# coding=utf-8
"""
# @file: spider.py
# @author: Sun Xinghua
# @date:  2016/12/14 9:44
# @version: Ver0.0.0.100
# @note:
"""
import sys
import os


class LineCount:
    """
    # @class：LineCount
    # @author：Sun Xinghua
    # @date：2016/12/14 9:44
    # @note： 统计代码行数
    """
    @staticmethod
    def trim(docstring):
        """
        trim string
        :param docstring: line in file
        :return: trimmed line
        """
        if not docstring:
            return ''
        lines = docstring.expandtabs().splitlines()
         
        indent = sys.maxint
        for line in lines[1:]:
            stripped = line.lstrip()
            if stripped:
                indent = min(indent, len(line) - len(stripped))
         
        trimmed = [lines[0].strip()]
        if indent < sys.maxint:
            for line in lines[1:]:
                trimmed.append(line[indent:].rstrip())
         
        while trimmed and not trimmed[-1]:
            trimmed.pop()
        while trimmed and not trimmed[0]:
            trimmed.pop(0)
         
        return '\n'.join(trimmed)

    def file_line_count(self, filename):
        """
        Return the file line count
        :param filename: file name
        :type filename: str
        :return: line count in file
        """
        (file_path, temp_filename) = os.path.split(filename)
        (shot_name, extension) = os.path.splitext(temp_filename)
        os.path.basename()
        if extension == '.py':
            fp = open(filename, 'r')
            self.sourceFileCount += 1
            all_lines = fp.readlines()
            fp.close()
             
            line_count = 0
            comment_count = 0
            blank_count = 0
            code_count = 0
            for line in all_lines:
                if line != " ":
                    line = line.replace(" ", "")        # remove space
                    line = line.replace("\t", "")       # remove space
                    line = LineCount.trim(line)         # remove tabIndent
                    if line.startswith('#'):            # comment
                        comment_count += 1
                    else:
                        if line == "":
                            blank_count += 1
                        else:
                            code_count += 1
                line_count += 1
            self.all += line_count
            self.allComment += comment_count
            self.allBlank += blank_count
            self.allSource += code_count
            print filename
            print '           Total      :', line_count
            print '           Comment    :', comment_count
            print '           Blank      :', blank_count
            print '           Source     :', code_count
                     
    def calculate_code_count(self, filename):
        """
        calculate code count in folder or file filename
        :param filename: file or dir name
        :return: None
        """
        if os.path.isdir(filename):
            if not filename.endswith('/'):
                filename += '/' 
            for fl in os.listdir(filename):
                if os.path.isdir(filename + fl):
                    self.calculate_code_count(filename + fl)
                else:
                    self.file_line_count(filename + fl)
        else:
            self.file_line_count(filename)
 
    # Open File
    def __init__(self):
        """
        initialize LineCount
        """
        self.all = 0
        self.allComment = 0
        self.allBlank = 0
        self.allSource = 0
        self.sourceFileCount = 0
        filename = raw_input('Enter file name: ')
        self.calculate_code_count(filename)
        if self.sourceFileCount == 0:
            print 'No Code File'
            pass
        print '\n'
        print '*****************  All Files  **********************'
        print '    Files      :', self.sourceFileCount
        print '    Total      :', self.all
        print '    Comment    :', self.allComment
        print '    Blank      :', self.allBlank
        print '    Source     :', self.allSource
        print '****************************************************'

if __name__ == '__main__':
    myLineCount = LineCount()
