# -*- coding: utf-8 -*-
"""
Created on Thu Dec  3 11:33:00 2020

@author: Neo
"""

import socket
import numpy as np
import matplotlib.pyplot as plt
import time
import os
import sys
import json
_ICEBLOC_IP = ("192.168.1.222",39933)


#%%
def m2_connect(verbose=True):
    check, dic = _ask_m2("start_link",{"ip_address" : "192.168.1.107"})
    if check and dic['status'] == 'ok' and verbose:
        print(u"✔ M2 SolsTiS")
    else:
        print(u"✕ M2 SolsTiS")

def set_m2_wavelength(wl_nm,verbose=False):
    check, dic = _ask_m2("move_wave_t",{"wavelength":[wl_nm],'report':'finished'})
    if not check:
        m2_connect(False)
        check, dic = _ask_m2("move_wave_t",{"wavelength":[wl_nm],'report':'finished'})
    if check:
        status = dic['status'][0]
        
        if verbose:
            status_s = _move_wave_t_status[status]
            print("{}".format(status_s))
        
        op_received, dic = _read_m2()
        if op_received == "move_wave_t":
            report = dic["report"][0]
            
            if verbose:
                report_s = _set_wave_m_report[report]
                print("\n{}".format(report_s))
            
        #check for etalon lock
        status, wavelength, status_etalon, condition_etalon = get_m2_status(verbose)
        if condition_etalon == "on":
            pass
        else:
            status, report = m2_lock_wavelength(verbose)
#        else:
#            if verbose:
#                print("Etalon is not locked")
        status, wavelength, status_etalon, condition_etalon = get_m2_status(verbose=False)
        return wavelength, condition_etalon

def get_m2_wavelength(verbose=False):
    status, wavelength, status_etalon, condition_etalon = get_m2_status(verbose)
    return wavelength

def m2_lock_wavelength(verbose=False):
    check, dic = _ask_m2("etalon_lock",{"operation":"on","report":"finished"})
    if not check:
        m2_connect(False)
        check, dic = _ask_m2("etalon_lock",{"operation":"on","report":"finished"})
    if check:
        status = dic['status'][0]
        
        if verbose:
            status_s = _etalon_lock_status_status[status]
            print("{}".format(status_s))
        
        op_received, dic = _read_m2()
        if op_received == "etalon_lock":
            report = dic["report"][0]
            
            if verbose:
                report_s = _set_wave_m_report[report]
                print("{}".format(report_s))
        
        return status, report
        

def get_m2_status(verbose=True):
    check, dic = _ask_m2("poll_move_wave_t")
    if not check:
        m2_connect(False)
        check, dic = _ask_m2("poll_move_wave_t")
    if check:
        status = dic['status'][0]
        wavelength = dic['current_wavelength'][0]
    
        if verbose:
            status_s = _poll_move_wave_t_status[status]
            print("Wavelength Table Tuning:\n{}\n{}\n".format(status_s,wavelength))
        
        check, dic = _ask_m2("etalon_lock_status")
        if check:
            status_etalon = dic['status'][0]
            condition_etalon = dic['condition']
            
            if verbose:
                status_s = _etalon_lock_status_status[status]
                condition_etalon_s = _etalon_lock_status_condition[condition_etalon]
                print('Etalon Lock:\n{}\n{}'.format(status_s,condition_etalon_s))
            
            return status, wavelength, status_etalon, condition_etalon

#def set_m2_wavelength(wl_nm,verbose=False):
#    check, dic = _ask_m2("set_wave_m",{"wavelength":[wl_nm], "report":"finished"})
#    if check:
#        status = dic['status'][0]
#        wavelength = dic['wavelength'][0]
#        extended_zone = dic['extended_zone'][0]
#        
#        if verbose:
#            status_s = _set_wave_m_status[status]
#            extended_zone_s = _set_wave_m_extended_zone[extended_zone]
#            print("{}\n{}\n{}".format(wavelength,status_s,extended_zone_s))
#            
#        #do something to wait for report
#        pass
#    
#        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#        sock.connect(_ICEBLOC_IP)
#        received = sock.recv(1024)
#        op_received, dic = _decode_msg(received)
#        if op_received == "set_wave_m":
#            report = dic["report"][0]
#            wavelength = dic["wavelength"][0]
#            extended_zone = dic["extended_zone"][0]
#            duration = dic["duration"][0]
#            
#            if verbose:
#                report_s = _set_wave_m_report[report]
#                extended_zone_s = _set_wave_m_extended_zone[extended_zone]
#                print("\n{}\n{}\n{}\nTime taken is {} s".format(report_s, wavelength, extended_zone_s, duration))
#            
#            status, current_wavelength, lock_status, extended_zone = get_m2_status(verbose)
#            if lock_status == 0:
#                m2_lock_wavelength(verbose)
#                get_m2_status(verbose)
#
#def get_m2_wavelength(verbose=False):
#    status, current_wavelength, lock_status, extended_zone = get_m2_status(verbose)
#    return current_wavelength
#
#def m2_lock_wavelength(verbose=False):
#    check, dic = _ask_m2("lock_wave_m",{"operation":"on"})
#    if check:
#        status = dic['status'][0]
#        if verbose:
#            status_s = _lock_wave_m_status[status]
#            print("{}".format(status_s))
#        return status
#
#def get_m2_status(verbose=True):
#    check, dic = _ask_m2("poll_wave_m")
#    if check:
#        status = dic['status'][0]
#        current_wavelength = dic['current_wavelength'][0]
#        lock_status = dic['lock_status'][0]
#        extended_zone = dic['extended_zone'][0]
#        
#        if verbose:
#            status_s = _poll_wave_m_status[status]
#            lock_status_s = _poll_wave_m_lock_status[lock_status]
#            extended_zone_s = _poll_wave_m_extended_zone[extended_zone]
#            print("{}\n{}\n{}\n{}".format(current_wavelength,status_s,lock_status_s,extended_zone_s))
#        
#        return status, current_wavelength, lock_status, extended_zone

#%%
_poll_wave_m_status = {0 : "Tuning software not active",
                       1 : "No link to wavelength meter or no meter configured",
                       2 : "Tuning in progress",
                       3 : "Wavelength is being maintained"
                       }
_poll_wave_m_lock_status = {0 : "Wavelength is not being maintained",
                            1 : "Wavelength is being maintained"
                            }
_poll_wave_m_extended_zone = {0 : "Current wavelength is not in an extended zone",
                              1 : "Current wavelength is in an extended zone"
                              }

_lock_wave_m_status = {0 : "Operation successful",
                       1 : "No link to wavelength meter or no meter configured"
                       }

_set_wave_m_status = {0 : "Command successful",
                      1 : "No link to wavelength meter or no meter configured",
                      2 : "Wavelength out of range"
                      }
_set_wave_m_extended_zone = {0 : "Current wavelength is not in an extended zone",
                             1 : "Current wavelength is in an extended zone"
                             }
_set_wave_m_report = {0 : "Task completed",
                      1 : "Task failed"
                      }
_move_wave_t_status = {0 : "Command successful",
                       1 : "Command failed",
                       2 : "Wavelength out of range"
                       }
_poll_move_wave_t_status = {0 : "Tuning completed",
                            1 : "Tuning in progress",
                            2 : "Tuning operation failed"
                            }
_etalon_lock_status_status = {0 : "Operation completed",
                              1 : "Command failed"}
_etalon_lock_status_condition = {"off" : "Etalon lock is off",
                                 "on" : "Etalon lock is on",
                                 "debug" : "Etalon lock is in a debug condition",
                                 "error" : "Etalon lock operatioin is in error",
                                 "search" : "Etalon lock serach algorithm is active",
                                 "low" : "Etalon lock is off due to low output"}
#%%
def _encode_msg(op,params_dic={}):
    if params_dic == {}:
        python_dic = {
                    "message" : 
                        {
                         "transmission_id" : [0],
                         "op" : op
                         }
                     }
    else:
        python_dic = {
                    "message" :
                        {
                            "transmission_id" : [0],
                            "op" : op,
                            "parameters" : params_dic
                        }
                     }
    return json.dumps(python_dic, sort_keys=False, indent=None).encode('ascii')

def _decode_msg(msg_s):
    python_dic = json.loads(msg_s)
    if "_reply" in python_dic["message"]["op"]:
        op = python_dic["message"]["op"].split("_reply")[0]
    else:
        op = python_dic["message"]["op"].split("_f_r")[0]
    params_dic = python_dic["message"]["parameters"]
    return op, params_dic

def _read_m2():
    global sock
#    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#    sock.connect(_ICEBLOC_IP)
    trial_number = 0
    while trial_number < 10:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(_ICEBLOC_IP)
            break
        except:
            trial_number += 1
            continue
    received = sock.recv(1024)
    op_received, dic = _decode_msg(received)
    return op_received, dic
    
def _ask_m2(op,params_dic={},verbose=False):
    global sock
    msg = _encode_msg(op,params_dic)
#    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#    sock.connect(_ICEBLOC_IP)
    trial_number = 0
    while trial_number < 10:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(_ICEBLOC_IP)
            break
        except:
            trial_number += 1
            continue
    sock.sendall(msg)
    received = sock.recv(1024)
    op_received, dic = _decode_msg(received)
    if op == op_received:
        check = True
    else:
        check = False
        if verbose:
            print("Operator of send ({}) and receive ({}) are different.".format(op,op_received))
    return check, dic

#%%
m2_connect()