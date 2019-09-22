

import psutil
import os
from os.path import isfile
from time import sleep
from threading import Thread

def pause():
    return input("PRESS ENTER TO CONTINUE ")

def choice(obj, min, max):
    try:
        obj= int(obj)
    except ValueError:
        return False,0
    if obj < min:
        return False,0
    if obj > max:
        return False,0
    return True,obj


def load(path):
    if isfile(path):
        f= open(path, 'r')
        cont= f.read()
        f.close()
        cont= cont.split('\n')
        while '' in cont: cont.remove('')
        return cont
    else:
        save(path,[])
        return []
    
def save(path, info):
    print("Saving ",path)
    f= open(path,'w')
    for item in info:
        f.write(str(item)+'\n')
    f.close()
    print("Saved")

def procs_iter():
    for p in psutil.process_iter():
        yield p,p.name()
def procs_info():
    items= []
    for p,info in procs_iter():
        if info not in items:
            items.append(info)
    return items
    
def add_white_list(item):
    global white_list
    if item not in white_list:
        white_list.append(item)
def add_terminate_list(item):
    global terminate_list
    if item not in terminate_list:
        terminate_list.append(item)
def add_kill_list(item):
    global kill_list
    if item not in kill_list:
        kill_list.append(item)
        
not_running_for_the_first_time_file= 'not running for the first time'
dont_show_help_message_file= 'dont show help message'
kill_log_file= "kill log.log"

white_list= load("whitelist")
terminate_list= load("terminatelist")
kill_list= load("killlist")

if not isfile(not_running_for_the_first_time_file):
    print()
    print("It seems that you are running this program for the first time")
    print(f"If you want to see the first-use setup again, delete \"{not_running_for_the_first_time_file}\" ")
    if not isfile(dont_show_help_message_file):
        print()
        print("You will see a list of the running processes")
        print("Choose all that you dont want to be terminated / killed")
        print("The rest will be terminated / killed")
        print("Critical processes to the OS should be protected by the OS")
        print(f"If you want to see this message again, delete \"{dont_show_help_message_file}\" ")
        pause()
        open(dont_show_help_message_file,'w').close()
    
    procs= procs_info()
    for ind in range(len(procs)-1, 0, -1):
        item= procs[ind]
        if (item in white_list) or (item in terminate_list) or (item in kill_list):
            del procs[ind]
    while 1:
        print()
        if len(procs) == 0:
            print("No more processes detected, continuing")
            pause()
            break
        
        for ind,info in enumerate(procs):
            print(f'{ind} / {info}')
        print("w / whitelist the rest")
        print("f / finish setup")
        c= input("> ")
        if c=='w':
            for info in procs:
                add_white_list(info)
            continue
        elif c=='f':
            break
        valid,proc_c= choice(c, 0, len(procs)-1)
        if not valid:
            print("Invalid choice: ",c)
            pause()
            continue
        print("Choosen: ",procs[proc_c])
        c= input("(c)onfirm / abort: ")
        if c=='c':
            add_white_list(procs.pop(proc_c))
        else:
            print("Aborted")
            pause()
       
    save('whitelist',white_list)
    
    open(not_running_for_the_first_time_file,'w').close()



access_denied= []
terminated_processes= []
    
def deal_with_procs():
    global thread_finished
    while thread_running:
        for p,info in procs_iter():
            if (info in white_list) or (info in access_denied):
                continue
            elif info in terminate_list:
                p.terminate()
            elif info in kill_list:
                p.kill()
            else:
                f= open(kill_log_file,'a')
                f.write(str(info)+'\n')
                f.close()
                try:
                    p.terminate()
                except psutil.AccessDenied:
                    if info not in access_denied:
                        access_denied.append(info)
                    f= open(kill_log_file,'a')
                    f.write("access denied\n")
                    f.close()
                    continue
                    
                if info not in terminated_processes:
                    terminated_processes.append(info)
    thread_finished= True

while 1:
    print()
    print("0 / Start terminating processes")
    print("1 / View the terminated processes")
    print("e / Exit")
    c= input("> ")
    if c=='e':
        break
    elif c=='0':
        thread_running= True
        thread_finished= False
        Thread(target=deal_with_procs).start()
        input("Press enter to stop terminating processes and go back ")
        thread_running= False
        print("Stopping...")
        while not thread_finished:
            sleep(0.2)
    elif c=='1':
        while 1:
            print()
            if len(terminated_processes)==0:
                print("No more terminated processes, continuing")
                pause()
                break
                
            for ind,item in enumerate(terminated_processes):
                print(f"{ind} / {item}")
            print("b / go back")
            print("sb / save changed and go back")
            c= input("> ")
            if c=='b':
                break
            elif c=='sb':
                save("whitelist",white_list)
                save("terminatelist",terminate_list)
                save("killlist",kill_list)
                break
            valid,choosen= choice(c,0,len(terminated_processes)-1)
            if not valid:
                print("Invalid choice: ", c)
                pause()
                continue
            while 1:
                print("Choosen: ",terminated_processes[choosen])
                c= input("go (b)ack / (w)hiteList / (t)erminateList /(k)illList: ")
                if c=='b':
                    pass
                elif c=='w':
                    add_white_list(terminated_processes.pop(choosen))
                elif c=='t':
                    add_terminate_list(terminated_processes.pop(choosen))
                elif c=='k':
                    add_kill_list(terminated_processes.pop(choosen))
                else:
                    print("Invalid choice: ",c)
                    pause()
                    continue
                break
                    
    else:
        print("Invalid choice: ",c)
        pause()
    
    
