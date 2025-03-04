import socket
import select
import time
import os
import threading
import sys

# 并发最大线程数
max_thread = 1
timeout = 10
sleep_time = 1
socket.setdefaulttimeout(timeout)

# [print(chr(i)) for i in range(ord("a"),ord("z")+1)]
def get_tld():
    tld = list()
    with open("tld", "r") as f:
        for line in f:
            if not line.startswith("//"):
                tld.append(line)
    return tld


# 域名信息，域名后缀，whois服务器
def whois_query(domain_name, name_server, whois_server):
    retry = 3
    domain = domain_name + "." + name_server

    info = ""
    while not info and retry > 0:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.connect((whois_server, 43))
            s.send(f"{domain} \r\n".encode())
            while True:
                res = s.recv(1024)
                if not len(res):
                    break
                info += str(res)
            s.close()
            retry -= 1
            time.sleep(sleep_time)
        except:
            pass
    return info


def get_reginfo(name, tld_info):
    can_reg = False
    info = whois_query(name, tld_info[0], tld_info[1])
    reg = tld_info[2]
    # print(reg)
    if info == "":
        print(f"{name}.{tld_info[0]} => 查询失败")
        return
    # print(info)
    if info.find(reg) >= 0:
        print(f"{name}.{tld_info[0]} => 未注册")
        can_reg = True
    # if info include 'Number of allowed queries exceeded.\r\n'
    # it means the whois server has been blocked
    # so we need to sleep for a while and query again
    while info.find("Number of allowed queries exceeded.") >= 0:
        # sleep for 10 sec and query again, show a count down during sleep
        for i in range(120, 0, -1):
            print(f"{name}.{tld_info[0]} => 查询被限制，{i} 秒后重试", end="\r", flush=True)
            time.sleep(1)
        info = whois_query(name, tld_info[0], tld_info[1])
        if info.find(reg) >= 0:
            print(f"{name}.{tld_info[0]} => 未注册")
            can_reg = True
    else:
        print(info)

        can_reg = False
    if can_reg:
        with open(f"result.txt", "a") as f:
            f.write(f"{name}.{tld_info[0]} \n")


def get_domain_name(name):
    tld_list = get_tld()
    tld_array = [x.split("=")[:-1] for x in tld_list][1:]
    # [print(y) for y in tld_array]
    for domain in tld_array:
        while threading.active_count() > max_thread:
            time.sleep(sleep_time)
            
        t = threading.Thread(
            target=get_reginfo,
            args=(
                name,
                domain,
            ),
        )
        t.start()
        time.sleep(sleep_time)


def get_domain_free(name, domain):
    name_list = []
    with open(name, "r") as f:
        for line in f:
            if line:
                name_list.append(line.strip())
    tld_list = get_tld()[1:]
    tld_array = [x.split("=")[0] for x in tld_list]

    if domain not in tld_array:
        print(f"域名 {domain} 不在tld列表中")
    tld_index = tld_array.index(domain)
    tld_par_list = [x.split("=")[:-1] for x in tld_list]
    for name in name_list:
        while threading.active_count() > max_thread:
            time.sleep(sleep_time)
            
        t = threading.Thread(
            target=get_reginfo,
            args=(
                name,
                tld_par_list[tld_index],
            ),
        )
        t.start()
        time.sleep(sleep_time)


if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) == 1:
        ## python asura
        get_domain_name(args[0])
    else:
        ## python lu 2letter
        get_domain_free(args[1], args[0])
