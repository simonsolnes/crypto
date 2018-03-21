#!/usr/bin/env python3
from requests import get
from json import loads
import sys

## CONFIG

# Print the price you bought at for each coin
use_portfolio = True

# The coins you want to track in addition to the portfolio
mycoins = ['XRP', 'XMR']

# Leave empty if you don't want to print this
portfolio = {
    'BTC': {
        'amount': 0.01,
        'cost' : 160.2
    },
    'ETH': {
        'amount': 1.5,
        'cost' : 1338.14
    },
    'LTC' : {
        'amount': 3,
        'cost' : 627.25
    },
    'MIOTA': {
        'amount': 120.62,
        'cost' : 256.921
    },
}

def parse_args():
    global use_portfolio
    printall = False
    usrcoins = []

    if len(sys.argv) > 1:
        if sys.argv[1] == 'all':
            printall = True
        else:
            usrcoins = sys.argv[1:]
        use_portfolio = False
    else:
        usrcoins = mycoins
        if use_portfolio:
            for coin in portfolio:
                usrcoins.append(coin)

    return printall, usrcoins



def colorize(x, frmt='normal', fg='normal', bg='normal'):
    c = ['black','red','green','yellow','blue','magenta','cyan','white','normal']
    c = {name: idx for idx, name in enumerate(c)}
    f = {'normal' : 0, 'bold' : 1, 'faint' : 2, 'italic' : 3, 'underline' : 4}
    return '\x1b['+str(f[frmt])+';'+str(30+c[fg])+';'+str(40+c[bg])+'m'+x+'\x1b[0m'

def matchname(name, repository):
    return name.lower() in [i.lower() for i in repository]

    

class Coin():
    def __init__(self, data):
        self.price = data['price_usd']
        self.change = {i: float(data['percent_change_' + i]) for i in ['1h', '24h', '7d']}
        self.symbol = data['symbol']

    def __repr__(self):
        retval = []
        retval.append(colorize(self.symbol.ljust(5), 'bold') + ' ')

        fg = 'red' if self.change['24h'] < 0 else 'green'
        if self.price[0] == '0':
            self.price = self.price[1:]
        price = self.price.rjust(10)
        retval.append(colorize(price, 'bold', fg))

        retval.append(' ')

        if use_portfolio:
            if self.symbol in portfolio:
                port = portfolio[self.symbol]
                cost = str(port['cost'] / port['amount'])
                if len(cost) > 6:
                    cost = cost[:6]
                if cost[-1] == '.':
                    cost = cost[:-1]
                cost = cost.ljust(6)
                retval.append(colorize(cost, 'faint'))
            else:
                retval.append(' ' * 6)
            retval.append('   ')
            

        for timeframe, percentage in self.change.items():
            retval.append(timeframe + ': ')

            change = ('%.2f' % percentage + '%').rjust(8)
            fg = 'red' if percentage < 0 else 'green'
            retval.append(colorize(change, fg=fg) + '    ')

        return ''.join(retval)

def print_portfolio(portfolio, coins):
    def frmt(num):
        return colorize(str('%.2f' % num) + ' USD', 'bold')
        
    header = colorize('Portfolio:', 'bold')
    print(header, end = ' ')
    cost = sum([coin['cost'] for symbol, coin in portfolio.items()])
    print('Cost:', frmt(cost), end = '  ')
    value = 0
    for symbol, portcoin in portfolio.items():
        for coin in coins:
            if symbol == coin.symbol:
                value += float(coin.price) * portcoin['amount']
    print('Value:', frmt(value), end='  ')
    gainnum = value - cost
    fg = 'red' if gainnum < 0 else 'green'
    print('Gain:', colorize(str('%.2f' % gainnum), 'bold', fg) + colorize(' USD', 'bold'), end = ' ')
    gainpercent = (gainnum / cost) * 100

    print('(' + colorize(str('%.2f' % gainpercent) + '%', 'bold', fg) + ')')


printall, usrcoins = parse_args()

register = loads(get('https://api.coinmarketcap.com/v1/ticker/').text)

coins = []

for coin in register:

    is_match = any([matchname(coin[tag], usrcoins) for tag in ['symbol', 'id', 'name']])

    if is_match or printall:
        coins.append(Coin(coin))

for coin in coins:
    print(coin)

if use_portfolio:
    print_portfolio(portfolio, coins)
