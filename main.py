#Main File 
from machine import ADC, Pin 
from machine import Timer
import time
import oled_1_3

flow26 = ADC(Pin(26)) #number is GPx
temp27 = ADC(Pin(27))

AUFLOESUNG = 2**16
oled = oled_1_3.OLED_1inch3()

def taster_loop(l):
    temp()
    flow()
    oled_loop()
    print("--------------------")


def temp():
    global temp_V
    tempvalue = temp27.read_u16()
    temp_V = 3.0/AUFLOESUNG*tempvalue #converts the bits into voltage
    print("Temperatur Signal:",'\t',tempvalue)
    print("temp_V:",'\t',temp_V)
    temp_csv() 

def temp_csv():
    global temp_V
    global temp_C
    csvdata_temp = []
    delim = ','
    
    with open('csv_SMF3100_Temperaturliste.csv','r') as file: #opens the csv file
        for line in file:
            csvdata_temp.append(line.rstrip('\n').rstrip('\r').split(delim)) #puts value in array
    csvdata_temp.pop(0) #removes first (position 0) values, here C and Voltage

    for i in range(len(csvdata_temp)):
        csv_temp_V=float(csvdata_temp[i][1]) #converts string into float
        if csv_temp_V < temp_V: #if value of csv is lower than temp than use that number and the one before, then break out of loop
            temp_C_f = float(csvdata_temp[i][0]) #first temperature value, lower than meassured
            temp_V_f = float(csvdata_temp[i][1]) #first voltage value, lower than meassured
            temp_C_s = float(csvdata_temp[i-1][0]) #second temperature value, higher than meassured
            temp_V_s = float(csvdata_temp[i-1][0]) #second voltage value, higher than meassured           
            break

    temp_C = (((temp_C_s-temp_C_f)/(temp_V_s-temp_V_f))*(temp_V)*(temp_V-temp_V_f)+temp_C_f) #interpolation der Temperatur
    #(y=((yo*(x1-x)+(y1*(x-xo))/(x1-xo)
    print("temp_C",temp_C)

def flow():
    global flow_lnmin
    global te_ln
    flowvalue = flow26.read_u16()
    flow_V = 3.0/AUFLOESUNG*flowvalue #converts the bits into voltage
    
    xnullmin = 0.6 #under 0.6 the Flow is backwards
    xnull = 0.691 #start of 0 Flow
    xmax = 1.54 #from 1.5V on up the values, aren't calibrated anymore
    
    if xnull <= flow_V <= xmax :
        flow_lnmin = -934.26351 * flow_V + 1282.96211 * flow_V**2 + -697.52901 * flow_V**3 + 139.81601 * flow_V**4 + 231.25960 #polynom from measurements
        flow_lnmin = round(flow_lnmin)
        flow_lnmin = f'{flow_lnmin} ln/min'
        te_ln = f'Temp: {temp_C:0.2} C'
    if xnullmin <= flow_V <= xnull: #from 0.6V to 0.69V, Flow 0 ln/min 
        flow_lnmin = '0 ln/min'
        te_ln = f'Temp: {temp_C:0.2} C'
    if xnullmin > flow_V:       
        flow_lnmin = 'Error'
        te_ln = 'flowdirection'
    if xmax < flow_V :
        flow_lnmin = 'Error'
        te_ln = 'not calibrated'
    print(te_ln)

    print("Flow Signal:",'\t',flowvalue)
    print("flow_V:",'\t',flow_V)
    print("Durchfluss ",'\t',flow_lnmin)


def oled_loop():
    global te_ln
    global flow_lnmin
    global error_ln
    LINIENHOEHE = 5 #changed form original
    oled.fill(0x0000) #clear display
    linie = 0
    text = "He-Flowmeter: "
    oled.text(text,1,linie * LINIENHOEHE, oled.white)    
    linie = 2
    text = f'{flow_lnmin:}'
    oled.text(text,1,linie * LINIENHOEHE, oled.white)    
    linie = 4
    text = f'{te_ln:}'
    oled.text(text,1,linie * LINIENHOEHE, oled.white)
    oled.show()


tim1 = Timer(-1)
tim1.init(period=1000, mode=tim1.PERIODIC, callback = taster_loop) #reads the value of "taster1" every 500ms

print("bing!")
