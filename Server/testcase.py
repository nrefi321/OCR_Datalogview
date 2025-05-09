import requests
import random as rad
import time
import threading

def loop1():
    while(True):
        for i in range(1,10):
            try:
                deviceid = i
                ip = str(rad.randint(10, 255))+'.'+str(rad.randint(10, 255))+'.'+str(rad.randint(10, 255))+'.'+str(rad.randint(10, 255))
                url = 'http://127.0.0.1:2001/Config/'
                data = {
                        "DeviceID": deviceid,
                        "DeviceIP": ip,
                        "MachineNo": str(rad.randint(10, 255)),
                        "MachineModel": str(rad.randint(10, 255)),
                        "Operation": str(rad.randint(10, 255))
                        }
                res = requests.post(url = url,json = data)
                url = 'http://127.0.0.1:2001/Config/{},{}'.format(i,ip)
                #print(url)
                #time.sleep(0.1)
                res = requests.get(url = url)
                #print(res.status_code)
                #print(res.content)
            except:
                print('Error')
                pass

def loop2():
    while(True):
        try:
            ip = str(rad.randint(10, 255))+'.'+str(rad.randint(10, 255))+'.'+str(rad.randint(10, 255))+'.'+str(rad.randint(10, 255))
            url = 'http://127.0.0.1:2001/AlarmData/'
            data = {
                    "MachineNo": str(rad.randint(10, 255)),
                    "MachineModel": str(rad.randint(10, 255)),
                    "Operation": str(rad.randint(10, 255)),
                    "DeviceID": str(rad.randint(10, 255)),
                    "AlarmDetail": ip}
            res = requests.post(url = url,json = data)
            #print(res.status_code)
            res = requests.get(url = url+'ByDevice')
            #print(res.content)
            print('')
        except:
            print('Error')
            pass

def loop3():
    while(True):
        try:
            vpd =['vpd01','vpd02']
            vpdRan = vpd[rad.randint(0, 1)]
            url = 'http://127.0.0.1:2001/Recipe/LastRecipe/'+vpdRan
            res = requests.get(url = url)
            data = res.json()
            recipe = data[vpdRan]
            url = 'http://127.0.0.1:2001/Recipe/LoadRecipe/'+recipe
            res = requests.get(url = url)
            print(url,res.status_code)
            #print(res.text)
            #print('')
        except:
            print('Error')
            pass
t1 = threading.Thread(target=loop1)
t1.start()
t2 = threading.Thread(target=loop2)
t2.start()
t3 = threading.Thread(target=loop3)
t3.start()
a = input()