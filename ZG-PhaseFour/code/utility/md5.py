# coding=utf8
import ctypes
import re
import math

from utility.common import Common


class MD5:
    c = '0123456789abcdef'

    def __init__(self):
        pass

    def e(self, e, t):
        o = e[0]
        r = e[1]
        c = e[2]
        l = e[3]
        o = self.n(o, r, c, l, t[0], 7, -680876936)
        l = self.n(l, o, r, c, t[1], 12, -389564586)
        c = self.n(c, l, o, r, t[2], 17, 606105819)
        r = self.n(r, c, l, o, t[3], 22, -1044525330)
        o = self.n(o, r, c, l, t[4], 7, -176418897)
        l = self.n(l, o, r, c, t[5], 12, 1200080426)
        c = self.n(c, l, o, r, t[6], 17, -1473231341)
        r = self.n(r, c, l, o, t[7], 22, -45705983)
        o = self.n(o, r, c, l, t[8], 7, 1770035416)
        l = self.n(l, o, r, c, t[9], 12, -1958414417)
        c = self.n(c, l, o, r, t[10], 17, -42063)
        r = self.n(r, c, l, o, t[11], 22, -1990404162)
        o = self.n(o, r, c, l, t[12], 7, 1804603682)
        l = self.n(l, o, r, c, t[13], 12, -40341101)
        c = self.n(c, l, o, r, t[14], 17, -1502002290)
        r = self.n(r, c, l, o, t[15], 22, 1236535329)
        o = self.i(o, r, c, l, t[1], 5, -165796510)
        l = self.i(l, o, r, c, t[6], 9, -1069501632)
        c = self.i(c, l, o, r, t[11], 14, 643717713)
        r = self.i(r, c, l, o, t[0], 20, -373897302)
        o = self.i(o, r, c, l, t[5], 5, -701558691)
        l = self.i(l, o, r, c, t[10], 9, 38016083)
        c = self.i(c, l, o, r, t[15], 14, -660478335)
        r = self.i(r, c, l, o, t[4], 20, -405537848)
        o = self.i(o, r, c, l, t[9], 5, 568446438)
        l = self.i(l, o, r, c, t[14], 9, -1019803690)
        c = self.i(c, l, o, r, t[3], 14, -187363961)
        r = self.i(r, c, l, o, t[8], 20, 1163531501)
        o = self.i(o, r, c, l, t[13], 5, -1444681467)
        l = self.i(l, o, r, c, t[2], 9, -51403784)
        c = self.i(c, l, o, r, t[7], 14, 1735328473)
        r = self.i(r, c, l, o, t[12], 20, -1926607734)
        o = self.a(o, r, c, l, t[5], 4, -378558)
        l = self.a(l, o, r, c, t[8], 11, -2022574463)
        c = self.a(c, l, o, r, t[11], 16, 1839030562)
        r = self.a(r, c, l, o, t[14], 23, -35309556)
        o = self.a(o, r, c, l, t[1], 4, -1530992060)
        l = self.a(l, o, r, c, t[4], 11, 1272893353)
        c = self.a(c, l, o, r, t[7], 16, -155497632)
        r = self.a(r, c, l, o, t[10], 23, -1094730640)
        o = self.a(o, r, c, l, t[13], 4, 681279174)
        l = self.a(l, o, r, c, t[0], 11, -358537222)
        c = self.a(c, l, o, r, t[3], 16, -722521979)
        r = self.a(r, c, l, o, t[6], 23, 76029189)
        o = self.a(o, r, c, l, t[9], 4, -640364487)
        l = self.a(l, o, r, c, t[12], 11, -421815835)
        c = self.a(c, l, o, r, t[15], 16, 530742520)
        r = self.a(r, c, l, o, t[2], 23, -995338651)
        o = self.s(o, r, c, l, t[0], 6, -198630844)
        l = self.s(l, o, r, c, t[7], 10, 1126891415)
        c = self.s(c, l, o, r, t[14], 15, -1416354905)
        r = self.s(r, c, l, o, t[5], 21, -57434055)
        o = self.s(o, r, c, l, t[12], 6, 1700485571)
        l = self.s(l, o, r, c, t[3], 10, -1894986606)
        c = self.s(c, l, o, r, t[10], 15, -1051523)
        r = self.s(r, c, l, o, t[1], 21, -2054922799)
        o = self.s(o, r, c, l, t[8], 6, 1873313359)
        l = self.s(l, o, r, c, t[15], 10, -30611744)
        c = self.s(c, l, o, r, t[6], 15, -1560198380)
        r = self.s(r, c, l, o, t[13], 21, 1309151649)
        o = self.s(o, r, c, l, t[4], 6, -145523070)
        l = self.s(l, o, r, c, t[11], 10, -1120210379)
        c = self.s(c, l, o, r, t[2], 15, 718787259)
        r = self.s(r, c, l, o, t[9], 21, -343485551)
        e[0] = self.u(o, e[0])
        e[1] = self.u(r, e[1])
        e[2] = self.u(c, e[2])
        e[3] = self.u(l, e[3])
        return e

    def t(self, e, t, n, i, a, s):
        t = self.u(self.u(t, e), self.u(i, s))
        return self.u(t << a | (t % 0x100000000) >> 32 - a, n)

    def n(self, e, n, i, a, s, o, r):
        return self.t(n & i | ~n & a, e, n, s, o, r)

    def i(self, e, n, i, a, s, o, r):
        return self.t(n & a | i & ~a, e, n, s, o, r)

    def a(self, e, n, i, a, s, o, r):
        return self.t(n ^ i ^ a, e, n, s, o, r)

    def s(self, e, n, i, a, s, o, r):
        return self.t(i ^ (n | ~a), e, n, s, o, r)

    def o(self, t):
        # if re.match('/[\x80-\xFF]/', t) is not None:
        # t = Common.urlenc(t)
        n = len(t)
        i = [1732584193, -271733879, -1732584194, 271733878]
        a = 64
        while a <= len(t):
            i = self.e(i, self.r(t[a - 64:a]))
            a += 64
        t = t[a - 64:]
        s = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        a = 0
        while a < len(t):
            s[a >> 2] |= ord(t[a]) << (a % 4 << 3)
            a += 1
        s[a >> 2] |= 128 << (a % 4 << 3)
        if a > 55:
            self.e(i, s)
            a = 0
            for a in range(0, 16):
                s[a] = 0
        s[14] = 8 * n
        i = self.e(i, s)
        return i

    def r(self, e):
        t = []
        for n in range(0, 64, 4):
            t[n >> 2] = ord(e[n]) + (ord(e[n+1]) << 8) + (ord(e[n+2]) << 16) + (ord(e[n + 3]) << 24)
        return t

    def l(self, e):
        t = ''
        for n in range(0, 4):
            t += self.c[15 & e >> 8 * n + 4] + self.c[15 & e >> 8 * n]
        return t

    def d(self, e):
        for t in range(0, len(e)):
            e[t] = self.l(e[t])
        return ''.join(e)

    def m(self, e):
        return self.d(self.o(e))

    def u(self, e, t):
        return ctypes.c_int32(4294967295 & e + t).value


if __name__ == '__main__':
    sign = MD5().m('100-DDwODVkv&6c4aa6af6560efff5df3c16c704b49f1&1481254449758')
    print sign