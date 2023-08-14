import requests
import json
import time
import traceback

from stellar_sdk import *
from stellar_sdk.exceptions import BadRequestError
from config import public_key, private_key

# рандом прайс который будет изменен
new_price = 0.12345

# максимальное количество попыток еще раз отправить запрос при получении ошибки от сервера, переменная используется для всех функций для которых есть счетчик попыток
max_try = 3

def change_scripts(message):
    # функция смены работы скриптов
    old_dict = get_data()
    old_arr = old_dict["errors"]
    old_arr.append(message)
    new_arr = old_arr
    old_dict["buy_status"] = True
    old_dict["status"] = False
    old_dict["errors"] = new_arr
    result_dict = old_dict 
    print(f"новый json файл после работы change_scripts{result_dict}")
    with open('data.json', 'w') as json_file:
        # Запись данных в JSON файл
        json.dump(result_dict, json_file, indent=4)



def send_message(message):
# получим переменные в скрипте еще раз чтобы потом отправить эти же переменные обратно в json
    old_dict = get_data()
    old_arr = old_dict["errors"]
    print(old_arr)
    old_arr.append(message)
    new_arr = old_arr
    old_dict["errors"] = new_arr
    result_dict = old_dict 
    print(result_dict)
    with open('data.json', 'w') as json_file:
        # Запись данных в JSON файл
        json.dump(result_dict, json_file, indent=4)


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
    with open('data.json', 'w') as json_file:
        # Запись данных в JSON файл
        json.dump(result_dict, json_file, indent=4)


def get_data():
    file = open('data.json', 'r')
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


# здесь мы просто инициализируем переменные, нам неважно какие тут значения ведь в цикле while вызовется функция while_json() и изменит эти глобальные переменные на актуальные значения 
take_profit = None
stop_loss = None
buy_price = None
not_trigger = None
is_work = None
assetsell = None
procent_amount = None
assetAddress = None

def while_json():
    file = open('data.json', 'r')
    try:
        data = json.load(file) 
        data_dict = data

        global take_profit, is_work, stop_loss, buy_price, not_trigger, assetsell, procent_amount, assetAddress

        take_profit = float(data_dict["take profit"])
        stop_loss = float(data_dict["stop loss"])
        buy_price = float(data_dict["purchase_price"])
        not_trigger = float(data_dict["not_trigger"])
        is_work = bool(data_dict["status"])
        assetsell = data_dict["assetsell"]
        procent_amount = float(data_dict["volume"])
        assetAddress = data_dict["assetAddress"]
    except:
        is_work = False
    file.close()


digit = ""




url_offers = f"https://horizon.stellar.org/accounts/{public_key}/offers?limit=200"

# получаем баланс монеты 
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
        print(f"баланс в монете сейчас в функции get_acc_balance- {balance_dict}")
        return balance_dict

    except Exception as e:
        print("Ошибка в блоке get_acc_balance")
        send_error("Ошибка в блоке get_acc_balance")

# эта фунция также проверят тригер цену, функция узнает минимальную цену ордера у которого объем БОЛЬШЕ ТРИГЕРНОЙ ЦЕНЫ
def getOneOrderID():
    try:
        res = requests.get(url_offers, timeout=5)
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
        print("Ошибка в блоке getOneOrderID()")
        send_error("Ошибка в блоке getOneOrderID()")



# функция создания ордера, принимает цену по которой выставит, а также объем в щитке
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
        # тут обрботка неизвестных ошибок в случае если stellar не создаст ордер по неизвестным причинам и hash не будет в транзе
        try:
            response = server.submit_transaction(tx)
            if "hash" in response:
                print("Ордер успешно создан! Hash ниже.")
                print(response["hash"])
            else:
                print(f"Произошла ошибка при изменении цены.")
                send_error("Произошла ошибка при создании ордера")
                print(response)
                return False

        # обработка ошибок связанных с блокчейном stellar
        except BadRequestError as e:
            if "result_codes" in e.extras: 
                no_money = e.extras["result_codes"]["operations"][0]
                if no_money == 'op_underfunded':
                    print("Недостаточно баланса для совершения операции, возвращаю False")
                    # вызываем функцию которая изменит json
                    # send_error("Недостаточно баланса для совершения операции")
                    return False

            else:
                print(e)
                print(e.title)

                return False

    # тут обработка всех остальных неизвестных ошибок 
    except Exception as e:
        print("Ошибка в блоке createOrder")
        print(e)
        send_error("Ошибка в блоке createOrder")
        return False



# функция которая редактирует существующий ордер, принимает ордер айди, новую цену и объем в щитке
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
                print(response)
                return False


        except BadRequestError as e:
            if "result_codes" in e.extras: 
                no_money = e.extras["result_codes"]["operations"][0]
                if no_money == 'op_underfunded':
                    print("Недостаточно баланса для совершения операции")
                    # вызываем функцию которая изменит json
                    return False

            else:
                print(e)
                print(e.title)
                return False

    except Exception as e:
        print("Ошибка в блоке changeOrder")
        print(e)
        return False


# кол-во попыток при создании/изменении нового ордера
create_try = 0
change_try = 0

# функция которая определяет что делать - редачить существующий ордер или создавать новый
def isCreateOrChange(min_price):
    try:
        # получаем объем торговли, расчитывая в процентах
        new_amount = get_acc_balance()
        new_amount = float(new_amount[assetsell])
        new_amount = (procent_amount / 100) * new_amount
        new_amount = round(new_amount, 7)

        # проверям чтобы новый объем был больше тригерного объема, иначе будет возникать баг при котором бот пытается выставить ордер по очень маленькому объему бесконечно
        if new_amount > int(not_trigger):
            print(f"Новый объем при создании ордера равен - {new_amount}")
    
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
                result_req = createOrder(new_price, new_amount)

                # если запрос был с ошибкой, функция вернет False
                if result_req == False:
                    global create_try
                    create_try += 1
                    print(f"Попытка создать ордер номер - {create_try}")
                    if create_try <= max_try:
                        print("Функция создания вернула False, вызываю функцию isCreateOrChange() снова.")
                        isCreateOrChange(min_price)
                    else:
                        print(f"Попыток больше {max_try}, вызываю функцию выключения скрипта")
                        send_error(f"Ошибка возникла {max_try} раз при создании оредра, скрип выключен...")

                # если запрос выполнился успешно, изменим состочния счетчика на 0
                else:
                    create_try = 0
                    print("create try = 0")


            else: 
                print(f"На аккаунте есть ордер {currenOneOrderID}, вызываю функцию изменении цены")
                new_price = float(min_price) - 0.0000000001
                print(f"новая цена при изменении ордера - {new_price}")
                result_req = changeOrder(currenOneOrderID ,new_price, new_amount)

                # если запрос был с ошибкой, функция вернет False
                if result_req == False:
                    global change_try
                    change_try += 1
                    print(f"Попытка изменить ордер номер - {change_try}")
                    if change_try <= max_try:
                        print("Функция изменения вернула False, вызываю функцию isCreateOrChange() снова.")
                        isCreateOrChange(min_price)
                    else:
                        print(f"Попыток больше {max_try}, вызываю функцию выключения скрипта")
                        send_error(f"Ошибка возникла {max_try} раз при изменении существующего оредра, скрип выключен...")

                # если запрос выполнился успешно, изменим состочния счетчика на 0
                else:
                    change_try = 0
                    print("change_try = 0")





        else:
            print("Переключение скриптов")
            change_scripts(f"На аккаунте в монете {assetsell} баланса меньше тригерной цены (3 {assetsell}), останавливаю продажу, запускаю покупку...")



    except Exception:
        print("Ошибка в блоке isCreateOrChange")
        error_message = traceback.format_exc()
        print(error_message)
        send_error("Ошибка в блоке isCreateOrChange")




# функция которая считает увеличинное число для тейк профита
def increase_procent():
    # Увеличенное число = Исходное число + (Исходное число * Процент / 100)
    increased = float(buy_price) + (float(buy_price) * float(take_profit) / 100)
    return increased


# функция которая считает уменьшенное число для стоп лосса
def decrease_procent():
    decreased = float(buy_price) - (float(buy_price) * float(stop_loss) / 100)
    return decreased

# кол-во попыток узнать актуальную нижнюю цену в стакане
get_price_try = 0

# функция в которой мы узнаем актуальный нижний ордер в стакане, также тут учитываем тригерный объем при поиске
def get_lower_price():

    # увеличиваем счетчик попыток
    global get_price_try
    get_price_try += 1
    print(f"Попытка узнать цену номер - {get_price_try}")

    try:
        if len(assetsell) <= 4:
            digit = "4"
        else:
            digit = "12"

        url = f"https://horizon.stellar.lobstr.co/order_book?selling_asset_type=credit_alphanum{digit}&selling_asset_code={assetsell}&selling_asset_issuer={assetAddress}&buying_asset_type=native&limit=10"


        response = requests.get(url, timeout=5)
        response_dict = response.json()
        asks = response_dict["asks"]

        # вернем счетчик в изначальное состоянии в случае удачного запроса на сервер 
        get_price_try = 0

        for ask in asks:
            min_price = ask["price_r"]
            n , d = min_price["n"], min_price["d"]
            min_price = float(n) / float(d)
            amount_min_price = ask["amount"]
            if float(amount_min_price) > (not_trigger):
                return min_price, amount_min_price, asks
            
    except Exception as e:
        print("Ошибка в блоке get_lower_pricе")
        # проверяем счетчик попыток, если он меньше чем макс кол-во попыток, то функция подождет 9 сек, после чего вернется обратно в цикл while, где она вызовется еще раз, тк в цикле проверится условие if get_actual != None, а тк оно равно None, то функция будет вызываться еще раз до тех пор пока кол-во попыток не достигнет 3 или не выполнится корректно 
        if get_price_try < max_try:
            time.sleep(3)
            pass  

        else:
            print(f"Функция get_lower_price завершилась с ошибкой {max_try} раза. Скрипт остановлен...")
            print(e)
            send_error(f"Функция get_lower_price завершилась с ошибкой {max_try} раза. Скрипт остановлен...")
    


# функция которая получает спред между моим ордером и ближайшем
def get_percent_spread(my_min_price, asks):
    asks.pop(0)
    # в эту переменную запишем первую подходящий по объему цену
    stranger_price = None

    for ask in asks:
            min_price = ask["price_r"]
            n , d = min_price["n"], min_price["d"]
            min_price = float(n) / float(d)
            amount_min_price = ask["amount"]
            if float(amount_min_price) > (not_trigger):
                stranger_price = min_price
                break

    # узнаем разницу между двумя числами в процентах

    difference = stranger_price - my_min_price
    percent_difference = (difference / my_min_price) * 100
    print(f"Процентная разница между объемом {stranger_price} и {my_min_price} равен - {percent_difference}\n--------------------------------\n")

    # если процент разницы меньше 0.2 вызываем функцию изменения цены
    if percent_difference > 0.2:
        # в аргумент передаем цену чужого ордера чтобы встать после него
        print("Вызываю функцию, тк разница в процентах больше 0.5")
        isCreateOrChange(stranger_price)


i = 0
while True:
    try:
        # на каждой итерации цикла открываем json файл чтобы узнать актуальную информацию
        while_json()

        if is_work == True:
            i += 1

            # узнаем актуальную информацию о цене и объеме на бирже, get_actual возвращает данные в кортеже
            get_actual = get_lower_price()
            print(get_actual)
            # проверяем есть ли корректный возврат, если в функции нет подходящей цены под заданное условие, то она вернет None, здесь мы проверяем это условие чтобы не получить ошибки в будущем            
            if get_actual != None:
                min_price = float(get_actual[0])
                amount_min_price = float(get_actual[1])
                asks = get_actual[2]

                print(f"в мониторе сейчас объем - {amount_min_price}, цена - {min_price}")

                # тейк профит и стоп лосс 
                if min_price >= float(increase_procent()) or min_price <= float(decrease_procent()):
                    # проверка в которой мы сверяем цену выставленного последний раз ботом цену с ценой монитора
                    if round(min_price, 16) == round(new_price, 16):

                        isMine = "Ордер в топе"
                        print(f"{isMine}\n\nитерации - {i}\nминимальная цена - {min_price} XLM\nобъем - {((amount_min_price))} {assetsell}")
                        # вызываем функцию проверки спреда между предпоследним ордером
                        get_percent_spread(min_price, asks)
                    else: 
                        # тут идет проверка на тригер цену
                        # if float(amount_min_price) > float(not_trigger):
                        print(f"Кто-то перебил ордер, перебиваю...   {min_price}    {amount_min_price}")
                        start_time = time.time()
                        isCreateOrChange(min_price)
                        end_time = time.time()
                        elapsed_time = end_time - start_time
                        print(f"Функция выполнилась за {elapsed_time} секунд.")
                        # else:
                        #     print("в мониторе цена ниже тригерной")

                else:
                    print("значение тейк профита или стоп лосса не подходит.")

        # else:
        #     print("скрипт выключен")

    except Exception as e:
        print("Ошибка в блоке WHILE")
        print(e)
        send_error("Ошибка в блоке WHILE")
        continue

