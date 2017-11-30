# encoding=utf-8
##############################################################################################
# @file：const.py
# @author：Sun Xinghua
# @date：2016/11/19
# @version：Ver0.0.0.100
# @note：
# 定义一个常量类实现常量的功能
#
# 该类定义了一个方法__setattr()__，和一个异常ConstError, ConstError类继承
# 自类TypeError. 通过调用类自带的字典__dict__, 判断定义的常量是否包含在字典
# 中。如果字典中包含此变量，将抛出异常，否则，给新创建的常量赋值。
# 最后两行代码的作用是把const类注册到sys.modules这个全局字典中。
##############################################################r################################
import sys


################################################################################################################
# @class：_const
# @author：Sun Xinghua
# @date：2016/11/21 9:44
# @note：常量类
################################################################################################################
class _const:
    class ConstError(TypeError):pass
    def __setattr__(self, name, value):
        if self.__dict__.has_key(name):
            raise self.ConstError, "Can't rebind const (%s)" %name
        self.__dict__[name]=value

sys.modules[__name__] = _const()