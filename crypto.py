#!/usr/bin/env python3
from requests import get
from json import loads
import sys

mycoins = ['BTC', 'ETH', 'LTC', 'MIOTA', 'XRP', 'XMR']

def colorize(x, frmt='normal', fg='normal', bg='normal'):
    c = {"black":0,"red":1,"green":2,"yellow":3,"blue":4,"magenta":5,"cyan":6,"white":7,"normal":8}
    f = {"normal" : 0, "bold" : 1, "faint" : 2, "italic" : 3, "underline" : 4}
    return '\x1b['+str(f[frmt])+';'+str(30+c[fg])+';'+str(40+c[bg])+'m'+x+'\x1b[0m'

printall = False
usrcoins = []

if len(sys.argv) > 1:
    if sys.argv[1] == 'all':
        printall = True
    else:
        usrcoins = sys.argv[1:]
else:
    usrcoins = mycoins

usrcoins = [usrcoin.lower() for usrcoin in usrcoins]


coins = loads(get('https://api.coinmarketcap.com/v1/ticker/').text)

for coin in coins:
    if any([coin[tag].lower() in usrcoins for tag in ['symbol', 'id', 'name']]) or printall:
        print(colorize(coin['symbol'].ljust(5), 'bold'), end = '')

        price = ('%.2f' % float(coin['price_usd'])).rjust(8) + '     '
        if float(coin['percent_change_24h']) > 0:
            print(colorize(price, 'bold', 'green'), end='')
        elif float(coin['percent_change_24h']) < 0:
            print(colorize(price, 'bold', 'red'), end='')
        else:
            print(colorize(price, 'bold'), end='')
        for unit in ['1h', '24h', '7d']:
            changenum = float(coin['percent_change_' + unit])
            if changenum >= 0:
                change = (' ' + ('%.2f' % changenum) + ' %').rjust(8) + '   '
            else:
                change = ('%.2f' % changenum + ' %').rjust(8) + '   '

            print(unit + ': ', end = '')
            if changenum > 0:
                print(colorize(change, fg='green'), end = '')
            elif changenum < 0:
                print(colorize(change, fg='red'), end = '')
            else:
                print(colorize(change), end = '')
            
        print()
