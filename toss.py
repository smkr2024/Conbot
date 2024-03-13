import requests, os, settings
tossid = 'buycoin'

def check(name, amount):
    if not os.path.isfile('확인된거래.txt'):
        f = open('확인된거래.txt', 'w')
        f.close()


    base = {"result": None, "id": None, "name": None, "amount": None, "msg": None}

    if 1 < len(name) < 5: # 2~4글자 이름, 두번째 문자 * 표시
        s = list(name)
        s[1] = "*"
        name = ''.join(s)
    elif len(name) > 6: #7글자 이상 이름, 6번째까지만 표시
        name = name[:6]
    url = f"https://api-public.toss.im/api-public/v3/cashtag/transfer-feed/received/list?inputWord={tossid}"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36"}
    proxies = {'https':'socks5://103.235.64.148:49156'}
    response = requests.get(url, headers=headers, proxies=proxies).json()

    if not response['resultType'] == "SUCCESS": # IP차단 핸들링이노
        msg = response["error"]["errorCode"] + " " + response["error"]["reason"]
        base["result"] = False
        base["msg"] = msg
        return base

    data = response["success"]["data"]
    for transaction in data:
        transfer_id = transaction["cashtagTransferId"]
        transfer_name = transaction["senderDisplayName"]
        transfer_amount = transaction["amount"]

        if name == transfer_name: # 1. 정보 확인하기입니도 바꾸면 좆되니까 건들지 마러거라
            with open("확인된거래.txt") as f: # 처리된 기록은 용납하지 않는다 이기
                checked = f.read()

            if not str(transfer_id) in checked and amount == transfer_amount: # 2. 금액이 동일한지 딱 노무딱하게 판단한다
                with open("확인된거래.txt", "a") as f:
                    f.write(str(transfer_id))
                base["result"] = True
                base["id"] = transfer_id
                base["name"] = transfer_name
                base["amount"] = transfer_amount
                return base

    base["result"] = False # 입금내역에 존재하지 않음
    base["msg"] = "입금 미확인"
    return base