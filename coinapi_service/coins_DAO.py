from coinpaprika import client as Coinpaprika
import os.path

class Coin:
    def __init__(self, c_id=None, name=None, symbol=None, rank=None, price=None, del_hr=None, del_d=None, del_wk=None, del_m=None,
                 del_y=None):
        self.c_id = c_id
        self.c_name = name
        self.symbol = symbol
        self.rank = rank
        self.technical = {'p': price, 'd_h': del_hr, 'd_d': del_d, 'd_w': del_wk, 'd_m': del_m, 'd_y': del_y}

    def __repr__(self):
        s = ''
        for a in self.__dict__:
            s += f"{a}: {self.__getattribute__(a)}\n"
        return s


class PaprikaDAO:
    """
    Welcome to the crypto-quoter, Robert Silver 2021
    --Thank you to CoinPaprika API and to github user s0h3ck for their useful package
    ---https://api.coinpaprika.com/
    ---https://github.com/s0h3ck/coinpaprika-api-python-client


    """
    def __init__(self):
        self.client = Coinpaprika.Client()
        self.coin_dict = {}
        self.top = []

    def setup(self):
        self.init_coins_dict()
        self.get_top_10()

    def init_coins_dict(self):
        """init_coins_dict: get all the corresponding API specific ids for coins mapped to their symbols, i.e. BTC
           Some coins, duplicate symbols, i.e. BTT for bittorrent and blocktrade. In case of such conflict the duplicate
           will be appended to the list of coins using that symbol
        """
        for c in self.client.coins():
            if c['symbol'] not in self.coin_dict:
                self.coin_dict[c['symbol']] = [(c['id'], c['name'])]
            else:
                self.coin_dict[c['symbol']].append((c['id'], c['name']))


    def get_top_10(self):
        self.top = [c['symbol'] for c in self.client.coins()[:10]]


    def retCoin(self, c_id):
        c_ret = self.client.coin(c_id)
        c_ticker =  self.client.ticker(c_id)
        c_tech = c_ticker['quotes']['USD']
        coin_ret = Coin(c_id,
                        c_ret['name'],
                        c_ret['symbol'], c_ret['rank'],
                        c_tech['price'],
                        c_tech['percent_change_1h'],
                        c_tech['percent_change_24h'],
                        c_tech['percent_change_7d'],
                        c_tech['percent_change_30d'],
                        c_tech['percent_change_1y'])
        return coin_ret

    def ret_symbol(self, c_sym):
        if c_sym not in self.coin_dict:
            raise ValueError(f"Symbol {c_sym}: Not Recognized in API")
        if len(self.coin_dict[c_sym]) == 1:
            c_id = self.coin_dict[c_sym][0][0]
        else:
            name_list = [c_entry[1] for c_entry in self.coin_dict[c_sym]]
            c_id = None
            while c_id is None:
                choice = input(f"Multiple entries for symbol {c_sym}. select: {' '.join(name_list)} ")
                for i, e in enumerate(name_list):
                    if e == choice:
                        c_id = self.coin_dict[c_sym][i][0]
        return c_id


    def __write_coins_file__(self):
        in_str = input("Enter a space separated list of ticket symbols, i.e. BTC ETH ADA: ")
        in_list = in_str.split(" ")
        sym_list = []
        for c in in_list:
            try:
                c_sym = self.ret_symbol(c)
            except ValueError as e:
                print(e)
            else:
                sym_list.append(c_sym)
        txt_string = '\n'.join(sym_list)
        with open('coin_choices.txt', 'w') as f:
            f.write(txt_string)
        return sym_list

    def load_coins(self):
        if os.path.exists('coin_choices.txt'):
            in_txt = ""
            while in_txt != "y" and in_txt != "n":
                in_txt = input("A coin configuration file (coinchoices.txt) already exists.\nwould you like to use it? (y) or create a new one? (n): ")
            if in_txt == "y":
                with open('coin_choices.txt', 'r') as f:
                    sym_list = f.read().split('\n')
            else:
                sym_list = self.__write_coins_file__()
        else:
            print("No file coin_choices.txt exists\nThis will be a list of cryptocurrenices you wish to include in your sheet\n")
            sym_list = self.__write_coins_file__()

        coin_list = []
        for s in sym_list:
            coin_list.append(self.retCoin(s))
        return coin_list




if __name__ == "__main__":
    pDAO = PaprikaDAO()
    pDAO.setup()
    pDAO.load_coins()