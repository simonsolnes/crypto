#!/usr/bin/env python3
from requests import get
from json import loads
import sys
from table import Table
from colorstring import Color

## CONFIG

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
    printall = False
    usrcoins = []

    if len(sys.argv) > 1:
        if sys.argv[1] == 'all':
            printall = True
        else:
            usrcoins = sys.argv[1:]
    else:
        usrcoins = mycoins
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
        self.name = data['name']
        self.change = {i: float(data['percent_change_' + i]) for i in ['1h', '24h', '7d']}
        self.symbol = data['symbol']

    def render(self):
        getfg = lambda x: 'red' if float(x) < 0 else 'green'

        retval = []
        retval = []
        retval.append(Color(self.symbol, 'bold'))
        retval.append(Color(self.name))
        retval.append(Color(self.price.lstrip('0'), 'bold', getfg(self.change['24h'])))


        if self.symbol in portfolio:
            port = portfolio[self.symbol]
            cost = str(port['cost'] / port['amount'])
            cost = cost[:6]
            if cost[-1] == '.':
                cost = cost[:-1]
            retval.append(cost)
        else:
            retval.append('')
            

        for timeframe, percentage in self.change.items():
            change = ('%.2f' % percentage + '%').rjust(7)
            fg = 'red' if percentage < 0 else 'green'
            retval.append(Color(change, 'normal', getfg(percentage)))

        return retval

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

def main():

    printall, usrcoins = parse_args()

    register = loads(get('https://api.coinmarketcap.com/v1/ticker/').text)

    coins = []

    for coin in register:

        is_match = any([matchname(coin[tag], usrcoins) for tag in ['symbol', 'id', 'name']])

        if is_match or printall:
            coins.append(Coin(coin))

    data = []
    for coin in coins:
        data.append(coin.render())
    header = [Color(i, 'bold') for i in ['ticker', 'name', 'price', 'buy', '1h', '24h', '7d']]

    print(Table(data, header))

    print_portfolio(portfolio, coins)
if __name__ == '__main__':
    main()
