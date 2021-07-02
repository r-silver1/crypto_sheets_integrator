from sheets_service.sheets_DAO import SheetsDao
from coinapi_service.coins_DAO import Coin, PaprikaDAO


if __name__ == "__main__":
    sDAO = SheetsDao()
    pDAO = PaprikaDAO()
    pDAO.setup()
    coin_choices = pDAO.load_coins()
    values = [[c.symbol, c.technical['p']] for c in coin_choices]
    try:
        sDAO.write_crypto(values)
    except ValueError as e:
        print(e)
