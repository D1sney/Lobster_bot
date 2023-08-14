import requests
import json
import time
import traceback

from stellar_sdk import *
from stellar_sdk.exceptions import BadRequestError


# публичный и приватные ключи на которых работает приложение
from config import public_key, private_key


# максимальное количество доп попыток выполнить функцию если она завершится с ошибкой 
max_try = 3


 # функция смены работы скриптов, меняет статусы покупки на false, а продажи на true 
def change_scripts(message):
    old_dict = get_data()
    old_arr = old_dict["errors"]
    print(old_arr)
    old_arr.append(message)
    new_arr = old_arr
    old_dict["buy_status"] = False
    old_dict["status"] = True
    old_dict["errors"] = new_arr
    result_dict = old_dict 
    print("Новый json после его перезаписи")
    print(result_dict)
    with open('data.json', 'w') as json_file:
        # Запись данных в JSON файл
        json.dump(result_dict, json_file)

# функция которая завершает работу скрипта (стопает монитор в цикле while), путем изменения статуса работы, также она принимает аргумент - текст ошибки и записывает их в json
def send_error(error_name):
    # получим переменные в скрипте еще раз чтобы потом отправить эти же переменные обратно в json
    old_dict = get_data()
    old_arr = old_dict["errors"]
    print(old_arr)
    old_arr.append(error_name)
    new_arr = old_arr
    old_dict["buy_status"] = False
    old_dict["errors"] = new_arr
    result_dict = old_dict 
    print(result_dict)
    with open('data.json', 'w') as json_file:
        # Запись данных в JSON файл
        json.dump(result_dict, json_file)

# функция которая получит вначале работы скрипта данные из json
def get_data():
    file = open('data.json', 'r')
    try:
        data = json.load(file)  
        return data   
    except:
        global is_work
        is_work = False
        send_error("<i>Произошла ошибка ⚠️</i>\nОшибка при чтении json")

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
buy_volume = None


# функция открытия json файла, она открывается непрерывно в цикле while, ее задача - проверять актуальные данные, открыв json файл в цикле мы понимаем должен ли работать монитор, какую монету отслеживаем, объем и тд
def while_json():
    file = open('data.json', 'r')
    try:
        data = json.load(file) 
        data_dict = data

        global is_work, not_trigger, assetsell, assetAddress, buy_volume

        not_trigger = float(data_dict["buy_not_trigger"])
        is_work = bool(data_dict["buy_status"])
        assetsell = data_dict["assetsell"]
        assetAddress = data_dict["assetAddress"]
        buy_volume = float(data_dict["buy_volume"])
    except:
        is_work = False
    file.close()

# инициализация переменной, которая нужна для добавления 12 или 4 в ссылку (зависит от длины кода монеты)
digit = ""


# ссылка по которой мы узнаем текущие актуальные ордера на аккаунте
url_offers = f"https://horizon.stellar.org/accounts/{public_key}/offers?limit=200"


# функция создания нового ордера на аккунте, принимает цену по которой выставит ордер и объем по которому выставит ордер
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
            .append_manage_buy_offer_op(
                selling = nativeAsset,
                buying = auruxAsset,
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
                print(response)
                return False

        except BadRequestError as e:
            print("Неудачная попытка отправить запрос. (createOrder) Скрипт выключается.")
            if "result_codes" in e.extras: 
                no_money = e.extras["result_codes"]["operations"][0]
                if no_money == 'op_underfunded':
                    print("Недостаточно баланса для совершения операции")

                    return False


            else:
                print(e)
                print(e.title)
                return False

    except Exception as e:
        print("Ошибка в блоке createOrder")
        print(e)
        return False



# функция которая меняет цену текущего ордера на аккаунте, принимает айди ордера, цену по которому выставится ордер и объем
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
            .append_manage_buy_offer_op(
                selling = nativeAsset,
                buying = auruxAsset,
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
                print(f"Ордер успешно создан! По цене - {new_price} Hash ниже.")
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

# функция которая узнает есть ли ордер на покупку с текущей монетой из json'а, если нет - то функция вернет None
def get_order():
    try:
        res = requests.get(url_offers, timeout=5)
        responce_offer = res.json()
        offers = responce_offer["_embedded"]["records"]
        result = [None, None]
        if len(offers) > 0:
            for offer in offers:
                if "selling" in offer:
                    if offer["selling"]["asset_type"] == "native":
                        if offer["buying"]["asset_code"] == assetsell:
                            print(offer["amount"], offer["id"])
                            result[0] = offer["id"]
                            result[1] = offer["amount"]
                            return result
                            
                else:
                    print("На аккаунте нет ордеров на покупку щитка")

        # если в списке ордеров нет подходящего под заданные условия, то вернется None
        if len(result) == 0:
            return None
    except Exception as e:
        print("Ошибка в блоке get_order()")
        print(e)
        send_error("<i>Произошла ошибка ⚠️</i>\nОшибка в блоке get_order()")



# функция которая узнает баланс в торгуемой монете
def get_asset_balance():
    try:
        server = Server("https://horizon.stellar.org")
        keypair = Keypair.from_public_key(public_key)
        account = server.accounts().account_id(keypair.public_key).call()
        balances = account['balances']
        for item in balances:
            if 'asset_code' in item:
                if item["asset_code"] == assetsell:
                    print(item["balance"])
                    return float(item["balance"])
                
    except Exception as e:
        print("Ошибка в блоке get_asset_balance()")
        print(e)
        send_error("<i>Произошла ошибка ⚠️</i>\nОшибка в блоке get_asset_balance()")

        

change_try = 0
create_try = 0

            
# фунция которая определяет - создавать новый ордер или изменять существующий (если он есть), принимает аргумент - текущую цену из монитора
def isCreateOrChange(min_price):
    try:
        global new_price
        new_price = float(min_price) + 0.0000000001

        order_data = get_order()

        # order_data будет равен None в случае если на аккаунте нет подходящего под условия ордера
        print(f"order_data - {order_data}")
        if order_data != None:
            
            order_amount = order_data[1]
            order_id = order_data[0]

            # расчитываем правильный объем в объеме щитка для того чтобы получить точный необходимый объем в XLM
            # делим объем в XLM из ордера на новую цену и получаем объем в щитке
            # new_amount = float(order_amount) / new_price
            # new_amount = round(new_amount, 7)
            
            new_amount = buy_volume

            # вызываем функцию изменения цены ордера
            print("На аккаунте есть ордер на покупку, изменяю...")
            result_req = changeOrder(order_id, new_price, new_amount)

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
            print("Жду 5 секунд чтобы баланс на аккаунте успел обновиться и я получил корректный баланс аккаунта...")
            time.sleep(5)
            asset_balance = get_asset_balance()

            decrease_procent = float(buy_volume) - (0.20 * float(buy_volume))
            print("Исходный покупаемый баланс в монете:", buy_volume)
            print("Уменьшенный на 20% покупаемый баланс в монете:", decrease_procent)

            # учитываем погрешность поэтому уменьшаем на 20 текущий баланс аккаунта и потом его сравниваем с покупочным объемом из json
            
            if asset_balance >= decrease_procent:
                print(f"На аккаунте баланса в монете {assetsell} больше/равно покупочного объема ({asset_balance} - 20%), выключаю покупку и включаю продажу...")

                change_scripts(f"<i>SMSочка 💬</i>\nНа аккаунте баланса в монете {assetsell} больше покупочного объема ({asset_balance} - 20%), выключаю покупку и включаю продажу...")

            # иначе СОЗДАЕМ новый ордер на аккаунте
            else:
                # тут объем будет равен значению из json, тк у нас нет никакого ордера следовательно нам не надо помещать объем текущего ордера
                new_amount = buy_volume

                print(f"Создаю новый ордер по цене - {new_price}, объему - {new_amount}")
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
                    print("create_try = 0")
    

    except Exception as e:
        print("Ошибка в блоке isCreateOrChange")
        print(e)
        send_error("<i>Произошла ошибка ⚠️</i>\nОшибка в блоке isCreateOrChange")


new_price = 0.12345



# кол-во попыток узнать актуальную нижнюю цену в стакане
get_price_try = 0

# фунция которая находит первый ордер в стакане, она игнорирует объем который меньше тригерного в json
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
        bids = response_dict["bids"]

        # вернем счетчик в изначальное состоянии в случае удачного запроса на сервер 
        get_price_try = 0


        # итерируемся по массиву в котором находим и возврщаем ПЕРВЫЙ ордер в котором объем больше тригерного, таким образом мы сможем встать следущими после большого объема
        for bid in bids:
            min_price = bid["price_r"]
            n , d = min_price["n"], min_price["d"]
            min_price = float(n) / float(d)
            amount_min_price = bid["amount"]
            if (float(amount_min_price) /  min_price) > (not_trigger):
                return min_price, amount_min_price, bids
            
    except Exception as e:
        print("Ошибка в блоке get_lower_pricе")
        # проверяем счетчик попыток, если он меньше чем макс кол-во попыток, то функция подождет 9 сек, после чего вернется обратно в цикл while, где она вызовется еще раз, тк в цикле проверится условие if get_actual != None, а тк оно равно None, то функция будет вызываться еще раз до тех пор пока кол-во попыток не достигнет 3 или не выполнится корректно 
        if get_price_try < max_try:
            time.sleep(9)
            pass  

        else:
            print(f"Функция get_lower_price завершилась с ошибкой {max_try} раза. Скрипт остановлен...")
            print(e)
            send_error(f"<i>Произошла ошибка ⚠️</i>\nФункция get_lower_price завершилась с ошибкой {max_try} раза. Скрипт остановлен...")





# функция которая получает спред между моим ордером и ближайшем ордером в стакане
def get_percent_spread(my_min_price, bids):
    bids.pop(0)
    # в эту переменную запишем первую подходящий по объему цену
    stranger_price = None

    for bid in bids:
        min_price = bid["price_r"]
        n , d = min_price["n"], min_price["d"]
        min_price = float(n) / float(d)
        amount_min_price = bid["amount"]
        if (float(amount_min_price) /  min_price) > (not_trigger):
            stranger_price = min_price
            break

    # узнаем разницу между двумя числами в процентах

    difference = my_min_price - stranger_price
    percent_difference = (difference / stranger_price) * 100
    print(f"Процентная разница между объемом {my_min_price} и {stranger_price} равен - {percent_difference}\n--------------------------------\n")

    # если процент разницы меньше 0.2 вызываем функцию изменения цены
    if percent_difference > 0.2:
        # в аргумент передаем цену чужого ордера чтобы встать после него
        print("Вызываю функцию, тк разница в процентах больше 0.2")
        isCreateOrChange(stranger_price)



        

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
                min_price = float(get_actual[0])
                amount_min_price = float(get_actual[1])
                bids = get_actual[2]
                amount_min_price = float(amount_min_price) / min_price

                print(f"в мониторе сейчас объем - {amount_min_price}, цена - {min_price}")

                # проверка в которой мы сверяем цену выставленного последний раз ботом цену с ценой монитора
                if round(min_price, 16) == round(new_price, 16):
                    print(f"Ордер покупки в топе\nитерации - {i}\nминимальная цена - {min_price} XLM\nобъем - {((amount_min_price))} {assetsell}")
                    get_percent_spread(min_price, bids)
                else: 
                    print(f"Кто-то перебил ордер, перебиваю...   {min_price}    {amount_min_price}")
                    start_time = time.time()
                    isCreateOrChange(min_price)
                    end_time = time.time()
                    elapsed_time = end_time - start_time
                    print(f"Функция выполнилась за {elapsed_time} секунд.")
                    # else:
                    #     print("в мониторе цена ниже тригерной")

        # else:
        #     print("скрипт выключен")

    except Exception as e:
        print("Ошибка в блоке WHILE")
        print(e)
        send_error("<i>Произошла ошибка ⚠️</i>\nОшибка в блоке WHILE")
        continue





