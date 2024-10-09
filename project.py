import RPi.GPIO as GPIO
import time
from time import sleep
import serial               #import serial pacakge
import os
import re
import picamera

from datetime import datetime
import smtplib
import gps
        
gsm = serial.Serial("/dev/ttyS0", 9600, timeout = 3)

gmail_user = "raspberry1786@yahoo.in" #Sender email address
gmail_pwd = "wtrbgraoiygu" #Sender email password

subject = "***Alert*** EMERGENCY _ NEED HELP"
text = "***Alert*** EMERGENCY _ NEED HELP , please check the attached Photo"

time.sleep(0.3)
to = open('/home/pi/email.txt').read()
print to


img_file = 'img.jpg'
camera = picamera.PiCamera() 
camera.resolution = (1028, 720)

# Define GPIO to LCD mapping
LCD_RS = 11
LCD_E  = 9
LCD_D4 = 10

LCD_D5 = 22
LCD_D6 = 27
LCD_D7 = 17


led = 2;

sw = 3;

sound = 4;

shock = 18

num1 = open('/home/pi/number.txt').read()
print num1

ser = serial.Serial ("/dev/ttyUSB0", 9600, timeout = 1)         #Open port with baud rate


def main():

    GPIO.setmode(GPIO.BCM)       # Use BCM GPIO numbers
    GPIO.setup(LCD_E, GPIO.OUT)  # E
    GPIO.setup(LCD_RS, GPIO.OUT) # RS
    GPIO.setup(LCD_D4, GPIO.OUT) # DB4
    GPIO.setup(LCD_D5, GPIO.OUT) # DB5
    GPIO.setup(LCD_D6, GPIO.OUT) # DB6
    GPIO.setup(LCD_D7, GPIO.OUT) # DB7
    
    GPIO.setup(led, GPIO.OUT) # LED
    
    GPIO.setup(shock, GPIO.OUT) # LED   
    GPIO.setup(sound, GPIO.IN) # LED   
    
    GPIO.setup(sw, GPIO.IN) # LED
    
    GPIO.output(shock, False) # LED
    
    lcd_init()
 
    lcd_string(" Welcome To",LCD_LINE_1)
    lcd_string("Woman Safety",LCD_LINE_2)
    
    GPIO.output(led, True) # LED
    time.sleep(0.7) # 700 milli second delay
    GPIO.output(led, False) # LED
    time.sleep(0.7) # 700 milli second delay    
    GPIO.output(led, True) # LED
    time.sleep(0.7) # 700 milli second delay
    GPIO.output(led, False) # LED
    
    count = 0    
    map_link = ""
    
    
    while True:                         
        gps_data = (str)(ser.readline())                   #read NMEA string received
             
        GPGGA_data_available = gps_data.find(gpgga_info)   #check for NMEA GPGGA string                 
      
      if (GPGGA_data_available>-1):
                    GPGGA_buffer = gps_data.split("$GPGGA,",1)[1]  #store data coming after "$GPGGA," string 
                    NMEA_buff = (GPGGA_buffer.split(','))               #store comma separated data in buffer
                    GPS_Info(NMEA_buff)                                          #get time, latitude, longitude
         
                    print("lat in degrees:", lat_in_degrees," long in degree: ", long_in_degrees, '\n')
                    map_link = 'http://maps.google.com/?q='+(str)(lat_in_degrees) + ',' +(str)(long_in_degrees)   #create link to plot location on Google map
                    #print("------------------------------------------------------------\n")

                    if lat_in_degrees > 0:
                        lcd_byte(0x01, LCD_CMD)
                        lcd_string(lat_in_degrees,LCD_LINE_1) #commands.getoutput('hostname -I')
                        lcd_string(long_in_degrees,LCD_LINE_2)   #commands.getoutput('hostname -I')
                    else:
                        
                        lcd_byte(0x01, LCD_CMD)
                        lcd_string("Searching for",LCD_LINE_1)
                        lcd_string(".... Satellite",LCD_LINE_2)
                    time.sleep(1.6) # 1 second delay
        
                      
        if not GPIO.input(sw) or not GPIO.input(sound):
            while True:
                    
                lcd_string("***ALERT***",LCD_LINE_1) #commands.getoutput('hostname -I')
                GPIO.output(led, True) # LED


                GPIO.output(shock, True) # LED

                camera.capture('image.jpg')
                time.sleep(1)
                
                gsm.write("AT+CMGS=\"%s\"\r\n" % num1 )
                time.sleep(0.3)                            
                gsm.write("***ALERT*** Emergency At:\r\n")
                time.sleep(0.3)                                
                gsm.write("%s\r\n" %(map_link))
               
                lcd_string("Sending Mail         ",LCD_LINE_2) #commands.getoutput('hostname -I')
               
                print "Sending email"
                
                             
                dt_stamp = datetime.now().strftime("%d-%m-%y %H:%M:%S")              
                
                subject = "Emergency "+dt_stamp
                
                text = "***Alert*** EMERGENCY _ NEED HELP , please check the attached Photo, Location: "+map_link
                
                attach = 'image.jpg'
                msg = MIMEMultipart()
                
                msg['From'] = gmail_user
                msg['To'] = to
                msg['Subject'] = subject

                msg.attach(MIMEText(text))

                
                mailServer.login(gmail_user, gmail_pwd)
                mailServer.sendmail(gmail_user, to, msg.as_string())
                mailServer.close()
                print "Email Sent"
                
                lcd_string("Mail Sent...         ",LCD_LINE_2) #commands.getoutput('hostname -I')
                       
                os.remove(attach)
                
                time.sleep(10) # 700 milli second delay
                
        else:
            GPIO.output(led, False) # LED
            
                    
        time.sleep(0.7)
    
 
if __name__ == '__main__':
 
  try:
    main()
  except KeyboardInterrupt:
    pass
  finally:
    lcd_byte(0x01, LCD_CMD)
    lcd_string("Pls Restart...",LCD_LINE_1)
    lcd_string("                 ",LCD_LINE_2)
    GPIO.cleanup()


