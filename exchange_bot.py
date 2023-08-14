import requests
import datetime
import json
import time
import traceback

from stellar_sdk import *
from stellar_sdk.exceptions import BadRequestError
from config import public_key, private_key

data_json = r'C:\Users\ivan3\OneDrive\Рабочий стол\lobster\data.json'

def send_error(error_name):
    # получим переменные в скрипте еще раз чтобы потом отправить эти же переменные обратно в json
    old_dict = get_data()
    old_arr = old_dict["errors"]
    print(old_arr)
    old_arr.append(error_name)
    new_arr = old_arr
    old_dict["status"] = False
    old_dict["errors"] = new_arr
    result_dict = old_dict 
    print(result_dict)
    with open(data_json, 'w') as json_file:
        # Запись данных в JSON файл
        json.dump(result_dict, json_file)


def get_data():
    file = open(data_json, 'r')
    try:
        data = json.load(file)  
        return data   
    except:
        global is_work
        is_work = False
        send_error("Ошибка при чтении json")

    file.close()
data_dict = get_data()
print(data_dict)

take_profit = float(data_dict["take profit"])
stop_loss = float(data_dict["stop loss"])
buy_price = float(data_dict["buy_price"])
not_trigger = float(data_dict["not_trigger"])
is_work = bool(data_dict["status"])
assetsell = data_dict["assetsell"]
procent_amount = float(data_dict["volume"])
assetAddress = data_dict["assetAddress"]

def while_json():
    file = open(data_json, 'r')
    try:
        data = json.load(file) 
        data_dict = data

        global take_profit, is_work, stop_loss, buy_price, not_trigger, assetsell, procent_amount, assetAddress

        take_profit = float(data_dict["take profit"])
        stop_loss = float(data_dict["stop loss"])
        buy_price = float(data_dict["buy_price"])
        not_trigger = float(data_dict["not_trigger"])
        is_work = bool(data_dict["status"])
        assetsell = data_dict["assetsell"]
        procent_amount = float(data_dict["volume"])
        assetAddress = data_dict["assetAddress"]
    except:
        is_work = False
    file.close()


digit = ""





if len(assetsell) <= 4:
    digit = "4"
else:
    digit = "12"

url = f"https://horizon.stellar.lobstr.co/order_book?selling_asset_type=credit_alphanum{digit}&selling_asset_code={assetsell}&selling_asset_issuer={assetAddress}&buying_asset_type=native&limit=10"


url_offers = f"https://horizon.stellar.org/accounts/{public_key}/offers?limit=200"


def get_acc_balance():
    try:
        server = Server("https://horizon.stellar.org")
        public_key_var = public_key
        keypair = Keypair.from_public_key(public_key_var)
        account = server.accounts().account_id(keypair.public_key).call()
        balances = account['balances']
        balance_dict = {}
        for item in balances:
            if 'asset_code' in item:
                balance_dict[item['asset_code']] = item['balance']

        return balance_dict

    except Exception as e:
        print("Ошибка в блоке get_acc_balance")
        send_error("Ошибка в блоке get_acc_balance")


def getOneOrderID():
    try:
        res = requests.get(url_offers)
        responce_offer = res.json()
        offers = responce_offer["_embedded"]["records"]
        offers_dict = {}
        if len(offers) > 0:
            for i in range(len(offers)):
                if offers[i]['buying']['asset_type'] == 'native':
                    print("ОРДЕР - продажа щитка")
                    print(f"щиток - {offers[i]['selling']['asset_code']}")

                    if offers[i]['selling']['asset_code'] == assetsell:
                        offers_dict[offers[i]['selling']['asset_code']] = offers[i]['id']
                        return offers_dict[assetsell]
                    else:
                        return []
                else:
                    return []              
        else:
            print('на аккаунте нет ордеров, ретурн []')
            return []
    except Exception as e:
        print("Ошибка в блоке get_acc_balance")
        send_error("Ошибка в блоке getOneOrderID()")




def createOrder(new_price, new_amount):
    try:
        server = Server(horizon_url="https://horizon.stellar.org")
        auruxAsset = Asset(assetsell, assetAddress)
        nativeAsset = Asset.native()
        root_keypair = Keypair.from_secret(
            private_key
            )
        
        tx = (
                TransactionBuilder(
                source_account=server.load_account(account_id=root_keypair.public_key),
                network_passphrase=Network.PUBLIC_NETWORK_PASSPHRASE,
                base_fee=50000,
            )
            .append_manage_sell_offer_op(
                selling = auruxAsset,
                buying = nativeAsset,
                amount = str(new_amount),
                price = str(new_price),
                offer_id = 0,
            )
            .set_timeout(30)
            .build()
        )

        tx.sign(root_keypair)
        try:
            response = server.submit_transaction(tx)
            if "hash" in response:
                print("Ордер успешно создан! Hash ниже.")
                print(response["hash"])
            else:
                print(f"Произошла ошибка при изменении цены.")
                send_error("Произошла ошибка при создании ордера")
                print(response)

        except BadRequestError as e:
            print("Неудачная попытка отправить запрос. (createOrder) Скрипт выключается.")
            if "result_codes" in e.extras: 
                no_money = e.extras["result_codes"]["operations"][0]
                if no_money == 'op_underfunded':
                    print("Недостаточно баланса для совершения операции")
                    # вызываем функцию которая изменит json
                    send_error("Недостаточно баланса для совершения операции")

            else:
                print(e)
                print(e.title)

                send_error("Возникла непредвиденная ошибка при попытке создать ордер")

    except Exception as e:
        print("Ошибка в блоке createOrder")
        print(e)
        send_error("Ошибка в блоке createOrder")




def changeOrder(order_id, new_price, new_amount):
    try:
        server = Server(horizon_url="https://horizon.stellar.org")
        auruxAsset = Asset(assetsell, assetAddress)
        nativeAsset = Asset.native()
        root_keypair = Keypair.from_secret(
            private_key
            )
        
        tx = (
                TransactionBuilder(
                source_account=server.load_account(account_id=root_keypair.public_key),
                network_passphrase=Network.PUBLIC_NETWORK_PASSPHRASE,
                base_fee=50000,
            )
            .append_manage_sell_offer_op(
                selling = auruxAsset,
                buying = nativeAsset,
                amount = str(new_amount),
                price = str(new_price),
                offer_id = int(order_id),
            )
            .set_timeout(30)
            .build()
        )

        tx.sign(root_keypair)
        try:
            response = server.submit_transaction(tx)
            if "hash" in response:
                print("Ордер успешно создан! Hash ниже.")
                print(response["hash"])
            else:
                print(f"Произошла ошибка при изменении цены.")
                send_error("Произошла ошибка при создании ордера")
                print(response)

        except BadRequestError as e:
            print("Неудачная попытка отправить запрос. (changeOrder) Скрипт выключается.")
            if "result_codes" in e.extras: 
                no_money = e.extras["result_codes"]["operations"][0]
                if no_money == 'op_underfunded':
                    print("Недостаточно баланса для совершения операции")
                    # вызываем функцию которая изменит json
                    send_error("Недостаточно баланса для совершения операции")

            else:
                print(e)
                print(e.title)

                send_error("Возникла непредвиденная ошибка при попытке изменить ордер")

    except Exception as e:
        print("Ошибка в блоке changeOrder")
        print(e)
        send_error("Ошибка в блоке changeOrder")



def isCreateOrChange(min_price):
    try:
        # получаем объем торговли, расчитывая в процентах
        new_amount = get_acc_balance()
        new_amount = float(new_amount[assetsell])
        new_amount = (procent_amount / 100) * new_amount
        new_amount = round(new_amount, 7)

        # проверям чтобы новый объем был больше тригерного объема, иначе будет возникать баг при котором бот пытается выставить ордер по очень маленькому объему бесконечно
        if new_amount > float(not_trigger):
    
            global new_price
            new_price = float(min_price) - 0.0000000001
            print(f"новая цена - {new_price}")

            # получаем один ордер id на аккаунте в виде строки
            currenOneOrderID = getOneOrderID()
            print(currenOneOrderID)

            # если массив равен 0, то на аккаунте нет ордеров и его надо создать в таком случае, иначе поменять цену существущего ордера
            if len(currenOneOrderID) == 0:
                print("на аккаунте нет ордеров, вызываю функцию создания нового ордера")
                new_price_to_create = get_lower_price()
                new_price = float(new_price_to_create[0]) - 0.0000000001

                print(f"новая цена при создании нового ордера - {new_price}")
                createOrder(new_price, new_amount)
            else: 
                print(f"На аккаунте есть ордер {currenOneOrderID}, вызываю функцию изменении цены")
                changeOrder(currenOneOrderID ,new_price, new_amount)





        else:
            print("выключаю скрипт, т.к на аккаунте денег меньше тригерной цены")
            send_error("На аккаунте денег меньше трегерного объема")



    except Exception as e:
        print("Ошибка в блоке isCreateOrChange")
        error_message = traceback.format_exc()
        print(error_message)
        send_error("Ошибка в блоке isCreateOrChange")




# эта функция вызывается в начале работы скрипта для того чтобы создать ордер
def startOrder():
    response = requests.get(url)
    if response.status_code == 200:    
        response_dict = response.json()
        first_asks = response_dict["asks"][0]
        min_price = first_asks["price_r"]
        n , d = min_price["n"], min_price["d"]
        
        min_price = float(n) / float(d) - 0.0000000001

        global new_price
        new_price = min_price

        new_amount_first = get_acc_balance()
        new_amount_first = float(new_amount_first[assetsell])
        new_amount_first = (procent_amount / 100) * new_amount_first
        new_amount_first = round(new_amount_first, 7)

        createOrder(min_price, new_amount_first)
 
startOrder()




def increase_procent():
    # Увеличенное число = Исходное число + (Исходное число * Процент / 100)
    increased = float(buy_price) + (float(buy_price) * float(take_profit) / 100)
    print(f"увеличинное buy_price число - {increased}")
    return increased



def decrease_procent():
    decreased = float(buy_price) - (float(buy_price) * float(stop_loss) / 100)
    print(f"уменьшенное buy_price число - {decreased}")
    return decreased


def get_lower_price():
    try:
        response = requests.get(url)
        response_dict = response.json()
        asks = response_dict["asks"]

        for ask in asks:
            min_price = ask["price_r"]
            n , d = min_price["n"], min_price["d"]
            min_price = float(n) / float(d)
            amount_min_price = ask["amount"]
            print(min_price, amount_min_price)
            if float(amount_min_price) > (not_trigger):
                return min_price, amount_min_price
            
    except Exception as e:
        print("Ошибка в блоке get_lower_price")
        print(e)
        send_error("Ошибка в блоке get_lower_price")

i = 0
while True:
    try:
        # на каждой итерации цикла открываем json файл чтобы узнать актуальную информацию
        while_json()

        if is_work == True:
            i += 1

            # узнаем актуальную информацию о цене и объеме на бирже
            get_actual = get_lower_price()

            # проверяем есть ли корректный возврат, если в функции нет подходящей цены под заданное условие, то она вернет None, здесь мы проверяем это условие чтобы не получить ошибки в будущем            
            if get_actual != None:
                min_price = get_actual[0]
                amount_min_price = get_actual[1]

                print(f"в мониторе сейчас объем - {float(amount_min_price)}, цена - {float(min_price)}")

                # тейк профит и стоп лосс 
                if float(min_price) >= float(increase_procent()) or float(min_price) <= float(decrease_procent()):
                    # проверка в которой мы сверяем цену выставленного последний раз ботом цену с ценой монитора
                    if round(float(min_price), 16) == round(float(new_price), 16):
                        isMine = "Ордер в топе"
                        print(f"{isMine}\n\nитерации - {i}\nминимальная цена - {float(min_price)} XLM\nобъем - {((float(amount_min_price)))} AURAX\n--------------------------------\n")
                    else: 
                        # тут идет проверка на тригер цену
                        if float(amount_min_price) > float(not_trigger):
                            print(f"Кто-то перебил ордер, перебиваю...   {min_price}    {amount_min_price}")
                            start_time = time.time()
                            isCreateOrChange(min_price)
                            end_time = time.time()
                            elapsed_time = end_time - start_time
                            print(f"Функция выполнилась за {elapsed_time} секунд.")
                        else:
                            print("в мониторе цена ниже тригерной")

                else:
                    print("значение тейк профита или стоп лосса не подходит.")

        # else:
        #     print("скрипт выключен")

    except Exception as e:
        print("Ошибка в блоке WHILE")
        print(e)
        send_error("Ошибка в блоке WHILE")
        continue





