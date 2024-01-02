import requests
import re
import random

PT_LOCAL_TOKEN = None
QQ_ACCOUNT = {}
CLIENT_KEY = None


def get_pt_local_token():
    global PT_LOCAL_TOKEN
    try:
        url = (
            "https://ssl.xui.ptlogin2.weiyun.com/cgi-bin/xlogin?appid=527020901&daid=372&low_login=0&qlogin_auto_login"
            "=1&s_url=https://www.weiyun.com/web/callback/common_qq_login_ok.html?login_succ&style=20&hide_title=1"
            "&target=self&link_target=blank&hide_close_icon=1&pt_no_auth=1")
        obj = re.compile(r"pt_local_token=(?P<pt_local_token>.*?);", re.S)
        res = requests.get(url)
        status = res.status_code
        # print("[+] 获取 pt_local_token 中，响应码: ", status)
        if status == 200:
            # print(res.headers.get("Set-Cookie").strip(' ').find("pt_local_token"))
            match_res = obj.search(res.headers.get("Set-Cookie"))
            PT_LOCAL_TOKEN = match_res.group("pt_local_token")
            # print("[+] 获取到 pt_local_token:", PT_LOCAL_TOKEN)

        else:
            print("[-] 请求失败")
            exit(-1)
    except Exception:
        print("[-] 请先关闭代理")
        exit(-3)


def get_qq_uin():
    global QQ_ACCOUNT

    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/120.0.0.0 Mobile Safari/537.36 Edg/120.0.0.0",
        "Referer": "https://ssl.xui.ptlogin2.weiyun.com/",
        "Cookie": f"pt_local_token={PT_LOCAL_TOKEN};",
    }
    obj = re.compile(
        r'"uin":(?P<uin>.*?),"face_index":(?P<face_index>.*?),"gender":(?P<gender>.*?),"nickname":"('
        r'?P<nickname>.*?)","client_type":(?P<client_type>.*?),"uin_flag":(?P<uin_flag>.*?),"account":('
        r'?P<account>.*?)}]',
        re.S)
    account_num = 0
    for port in range(4301, 4309):
        random_num = random.randrange(int('1' * 16), int('9' * 16))
        url = (f"https://localhost.ptlogin2.weiyun.com:{port}/pt_get_uins?callback=ptui_getuins_CB&r=0.{random_num}&"
               f"pt_local_tk={PT_LOCAL_TOKEN}")
        # print(url)
        try:
            res = requests.get(url=url, headers=headers)
            if res.status_code == 200:
                account_num += 1
                print(f"[+] 端口 {port} 访问成功")
                res_text = res.content.decode('utf-8')
                match_res = obj.search(res_text)
                QQ_ACCOUNT.update(
                    {
                        port:
                            {
                                "uin": match_res.group("uin"),
                                "account": match_res.group("account"),
                                "name": match_res.group("nickname"),
                            }
                    }
                )

                print("[!] 账号:", QQ_ACCOUNT[port].get("account"))
                print("[!] 用户名:", QQ_ACCOUNT[port].get("name"))
                # print(res_text)
                print("-------------------------------------------------")

        except Exception:
            # print(f"[-] 端口 {port} 访问失败")
            break

    if account_num == 0:
        print("[-] 请求失败，请先登录电脑QQ")
        exit(-2)


def get_qq_ClientKey():
    global PT_LOCAL_TOKEN, QQ_ACCOUNT

    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/120.0.0.0 Mobile Safari/537.36 Edg/120.0.0.0",
        "Referer": "https://xui.ptlogin2.qq.com/cgi-bin/xlogin?appidc6014201&s_url=http://www.qq.com/qq2012"
                   "/loginSuccess.htm",
        "Cookie": f"pt_local_token={PT_LOCAL_TOKEN};",
    }
    obj = re.compile(r"clientkey=(?P<clientkey>.*?);")
    for port in range(4301, 4309):
        try:
            uin = QQ_ACCOUNT[port].get("uin")
            url = (f"https://localhost.ptlogin2.qq.com:{port}/pt_get_st?clientuin={uin}&callback=ptui_getst_CB"
                   f"&pt_local_tk={PT_LOCAL_TOKEN}")
            res = requests.get(url=url, headers=headers)
            match_res = obj.search(res.headers.get("Set-Cookie"))
            client_key = match_res.group("clientkey")
            QQ_ACCOUNT[port]['client_key'] = client_key
            # print(f"[!] ClientKey: ", client_key)

        except Exception:
            break

    pass


def get_skey():
    global PT_LOCAL_TOKEN, QQ_ACCOUNT
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/120.0.0.0 Mobile Safari/537.36 Edg/120.0.0.0",
        "Referer": "ptlogin2.qq.com/",
        "Cookie": f"pt_local_token={PT_LOCAL_TOKEN};",
    }
    obj = re.compile(r"skey=(?P<skey>.*?);")
    obj2 = re.compile(r"ptsigx=(?P<ptsigx>.*?)&")
    for port in range(4301, 4309):
        try:
            uin = QQ_ACCOUNT[port]['uin']
            client_key = QQ_ACCOUNT[port]['client_key']
            url = (f"https://ptlogin2.qq.com/jump?clientuin={uin}&clientkey={client_key}&keyindex=9&u1=https://www"
                   f".weiyun.com/web/callback/common_qq_login_ok.html?login_succ&pt_local_tk=&pt_3rd_aid=0&ptopt=1"
                   f"&style=40")
            res = requests.get(url=url, headers=headers)
            match_res = obj.search(res.headers.get("set-Cookie"))
            skey = match_res.group("skey")
            QQ_ACCOUNT[port]['skey'] = skey
            if res.content[16:17] == b'0':
                print(f"[+] 账号 {QQ_ACCOUNT[port]['account']} 登录成功")
                match_res = obj2.search(str(res.content))
                ptsigx = match_res.group("ptsigx")
                QQ_ACCOUNT[port]['ptsigx'] = ptsigx
                print("[!] Skey: ", skey)
                print("[!] ptsigx: ", ptsigx)
            else:
                print("[-] 登录失败")

            print("-------------------------------------------------")
        except Exception:
            break
    pass


def get_p_key():
    global PT_LOCAL_TOKEN, QQ_ACCOUNT
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/120.0.0.0 Mobile Safari/537.36 Edg/120.0.0.0",
        "Cookie": f"pt_local_token={PT_LOCAL_TOKEN};",
    }
    obj = re.compile(r"p_skey=(?P<p_skey>.*?);")
    for port in range(4301, 4309):
        try:
            url = (f"https://ssl.ptlogin2.weiyun.com/check_sig?pttype=2&uin={QQ_ACCOUNT[port]['uin']}&service=jump&"
                   f"nodirect=0&ptsigx={QQ_ACCOUNT[port]['ptsigx']}&s_url=https%3A%2F%2Fwww.weiyun.com%2Fweb%2Fcallback"
                   f"%2Fcommon_qq_login_ok.html%3Flogin_succ&f_url=&ptlang=2052&ptredirect=100&aid=1000101&daid=372&"
                   f"j_later=0&low_login_hour=0&regmaster=0&pt_login_type=2&pt_aid=0&pt_aaid=0&pt_light=0&pt_3rd_aid=0")
            res = requests.get(url=url, headers=headers, allow_redirects=False)
            match_res = obj.search(res.headers.get("Set-Cookie"))
            p_skey = match_res.group("p_skey")
            QQ_ACCOUNT[port]["p_skey"] = p_skey
            print("[!] p_skey: ", p_skey)
            print("-------------------------------------------------")

        except Exception:
            break
        pass

if __name__ == '__main__':
    get_pt_local_token()
    get_qq_uin()
    get_qq_ClientKey()
    get_skey()
    get_p_key()

