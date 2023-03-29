#TestMain File 
from machine import ADC, Pin 
from machine import Timer
import time

taster1 = Pin(1, Pin.IN) #number is GPx
flow26 = ADC(Pin(26))
temp27 = ADC(Pin(27))

AUFLOESUNG = 2**16

def taster_loop(l):
    tasterwert1 = taster1.value() #reads the value of "taster1"
    if tasterwert1 == 1: #if "taster1" is pushed
        flow()
        temp()
        print("--------------------")

def flow():
    flowvalue = flow26.read_u16()
    flow_V = 3.0/AUFLOESUNG*flowvalue #converts the bits into voltage
    print("Flow Signal:",'\t',flowvalue)
    print("flow_V:",'\t',flow_V)

def temp():
    global temp_V
    tempvalue = temp27.read_u16()
    temp_V = 3.0/AUFLOESUNG*tempvalue #converts the bits into voltage
    print("Temperatur Signal:",'\t',tempvalue)
    print("temp_V:",'\t',temp_V)
    table_con() 

def table_con():
    global temp_V
    #lists from Datasheet
    cvsdata_temp = []

    delim = ','
    with open('cvs_SMF3100_Temperaturliste.csv','r') as file:
        for line in file:
            cvsdata_temp.append(line.rstrip('\n').rstrip('\r').split(delim))
    cvsdata_temp.pop(0)

    for i in range(len(cvsdata_temp)):
        cvs_temp_V=float(cvsdata_temp[i][1])
        if cvs_temp_V < temp_V:
            temp_C_f = float(cvsdata_temp[i][0]) #first temperature value lower than meassured
            temp_V_f = float(cvsdata_temp[i][1]) #first voltage value lower than meassured
            temp_C_s = float(cvsdata_temp[i-1][0]) #second value, temperature higher than meassured
            temp_V_s = float(cvsdata_temp[i-1][0]) #second value, voltage higher than meassured           
            break    
"""
    print("+++++++++++++++++++++")
    print("temp_C_f",temp_C_f)
    print("temp_V_f",temp_V_f)
    print("temp_C_s",temp_C_s)
    print("temp_V_s",temp_V_s)
    print("temp_V",temp_V)
"""

    temp_C = (((temp_C_s-temp_C_f)/(temp_V_s-temp_V_f))*(temp_V)*(temp_V-temp_V_f)+temp_C_f) #interpolation der Temperatur
    #(y=((yo*(x1-x)+(y1*(x-xo))/(x1-xo)
    print("temp_C",temp_C)
    
    
tim1 = Timer(-1)
tim1.init(period=500, mode=tim1.PERIODIC, callback = taster_loop) #reads the value of "taster1" every 500ms

print("bing")
