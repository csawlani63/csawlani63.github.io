import PySimpleGUI as sg
import mysql.connector, cv2, pytesseract, pyotp, pyqrcode, random
from PIL import Image, ImageEnhance

mydb = mysql.connector.connect(
    host='localhost',
    user='sawlani63',
    passwd='cz839t60',
    database='ATM'
)

mycursor = mydb.cursor()

##-----DEFAULT SETTINGS----------------------------------##
bw = {'size':(7,1), 'font':('Franklin Gothic Book', 24), 'button_color':('black','#F8F8F8')}
bt = {'size':(15,1), 'font':('Franklin Gothic Book', 24), 'button_color':('black','#FF0000'),'key':'return'}
bo = {'size':(7,1),'font':('Franklin Gothic Book',24),'button_color':('black','#FFFF00'),'key':'clear'}
bc = {'size':(7,1),'font':('Franklin Gothic Book',24),'button_color':('black','#008000'),'key':'enter'}
pin, valid_pin, total_amount, counter, account_number, option_letter, mobile_number = '', '', '', 0, '', '', ''
list_event = ['1','2','3','4','5','6','7','8','9','0']

##-----WINDOW AND LAYOUT---------------------------------##
layout = [
    [sg.Text(' ATM ', size=(99,1), justification='right', background_color='#272533',
        text_color='white', font=('Franklin Gothic Book', 14, 'bold'))],
    [sg.Text('Enter account number:\nPress K to scan account number', size=(50,7), justification='center', background_color='white', text_color='black',
        font=('Digital-7',14), relief='sunken', key='_DISPLAY_')],
    [sg.Button('Return',**bt), sg.Button('←',**bw)],
    [sg.Button(' 1 ',**bw,key='1'), sg.Button(' 2 ',**bw,key='2'), sg.Button(' 3 ',**bw,key='3')],
    [sg.Button(' 4 ',**bw,key='4'), sg.Button(' 5 ',**bw,key='5'), sg.Button(' 6 ',**bw,key='6')],
    [sg.Button(' 7 ',**bw,key='7'), sg.Button(' 8 ',**bw,key='8'), sg.Button(' 9 ',**bw,key='9')],    
    [sg.Button('Clear',**bo), sg.Button('0',**bw), sg.Button('Enter',**bc)]
]

window = sg.Window('Atm system', layout=layout, background_color='#272533', size=(450, 600), return_keyboard_events='True')

layout_2 = [ [sg.Text('Enter Otp Here', size=(12,1), text_color = 'black', font=('Franklin Gothic Book', 14, 'bold')), sg.InputText()],
             [sg.Button('Enter', key = 'enter')]]



##----ATM FUNCTIONS-------------------------------##
##------------WEBCAM OCR--------------------------##
def ocr():
    key = cv2. waitKey(1)
    webcam = cv2.VideoCapture(0)
    while True:
        check, frame = webcam.read()
        print(check,'\n')#prints true as long as webcam is running
        cv2.imshow('Capturing', frame)
        key = cv2.waitKey(1)
        if key == ord('s'):
            cv2.imwrite(filename='ocr_example_1.png', img=frame)
            webcam.release()
            img_new = cv2.imread('ocr_example_1.png', cv2.IMREAD_GRAYSCALE)
            img_new = cv2.imshow('Captured Image', img_new)
            cv2.waitKey(1650)
            cv2.destroyAllWindows()
            break
        elif key == ord('q'):
            print('Turning off camera.')
            webcam.release()
            print('Camera off.')
            print('Program ended.')
            cv2.destroyAllWindows()
            break

def adjust_sharpness():
    image = Image.open('ocr_example_1.png')
    enhancer_object = ImageEnhance.Sharpness(image)
    out = enhancer_object.enhance(20)
    output = image.resize((640,480), Image.NEAREST)
    out.save('ocr_example_1.png')
    output.save('ocr_example_1.png')
    pytesseract.pytesseract.tesseract_cmd = r'C:\Users\charm\AppData\Local\Tesseract-OCR\tesseract.exe'
    text = pytesseract.image_to_string(Image.open('ocr_example_1.png'))
    window['_DISPLAY_'].update(text)
    global account_number
    account_number=text

##-------------OTP---------------------##
def Otp():
    global randno
    hotp = pyotp.HOTP('base32secret3232')
    randno = random.randint(1000,10000)
    otp = hotp.at(randno)
    generate_qr(otp,hotp)

def generate_qr(otp,hotp):
    otp_data = pyqrcode.create(otp)
    otp_data.png('otp_data.png', scale=8)
    otp_data = cv2.imread('otp_data.png', cv2.IMREAD_GRAYSCALE)
    otp_data = cv2.imshow('QR code', otp_data)
    window_2 = sg.Window('Otp', layout_2, background_color='#272533')
    event_2, values_2 = window_2.read()
    if values_2 != '':
        verify_otp(hotp, event_2, values_2, window_2)

def verify_otp(hotp, event_2, values_2, window_2):
    if event_2 == 'enter':
        verify = hotp.verify(values_2[0], randno)
        window_2.close()
        cv2.destroyAllWindows()
        if verify == True:
            beginning_text()
        else:
            window['_DISPLAY_'].update('Wrong otp entered')

##-------------MAIN FUNCTIONS-------------##
def account_number_entry(option_letter, list_event, event):
    global account_number
    if len(account_number)<=13 and option_letter=='':
        if event in list_event:
            account_number_function(event)
        elif event in ['enter', 'o']:
            account_number_verify(account_number)
            if right is True:
                window['_DISPLAY_'].update('Press O for OTP')
                if event in ['o']:
                    Otp()
            else:
                account_number = ''
                window['_DISPLAY_'].update('Account number doesnt exist in database')
                
def account_number_verify(account_number):
    mycursor.execute('SELECT account FROM accountandpin')
    myresult=mycursor.fetchall()
    global right
    for x in myresult:
        list_poa = x[0]
        if account_number == list_poa.strip():
            right = True
        else:
            right = False
            
def account_number_function(event):
    global account_number
    account_number = account_number + event
    window['_DISPLAY_'].update(account_number)
    
def proper_pin_login(event, list_event):
    if valid_pin=='' and event not in ['←']:
        window['_DISPLAY_'].update('Enter PIN')
        if event in list_event and counter==0:
            pin_update(event)
        if event in ['enter'] and Found=='False':
            pin_login(account_number)

def beginning_text():
    window['_DISPLAY_'].update('Welcome. Please type:\nA to Register a new PIN\nB to Check account balance\nC to Deposit funds\nD to Withdraw funds\nE to Change atm pin\nF to recharge mobile number')
   
def pin_update(event):
    global pin
    pin = pin + event
    window['_DISPLAY_'].update(pin)

def cancel_click():
    global option_letter, counter, pin, total_amount, account_number
    if account_number!='':
        option_letter, counter, pin, total_amount, mobile_number='', 0, '', '', ''
        beginning_text()
    else:
        window['_DISPLAY_'].update('Enter account number:\nPress K to scan account number')

def clear_click():
    ''' Clear button click event '''
    global pin
    pin=''
    window['_DISPLAY_'].update('0')

def pin_login(account_number):
    global Found, valid_pin
    mycursor.execute('SELECT pin FROM accountandpin WHERE account = %s',(account_number,))
    myresult=mycursor.fetchall()
    for x in myresult:
        list_poa = x[0]
        if pin == list_poa.strip():
            Found = 'True'
            valid_pin=pin
        else:
            Found='Return'

def amount():
    global myresult
    if option_letter in ['b','c','d','e','f']:
         mycursor.execute('SELECT amount FROM pinandamount WHERE pin = %s',(valid_pin,))
         myresult = mycursor.fetchall()

#-----MAIN EVENT LOOP------------------------------------##
while True:
    event, values = window.read()
    text_elem = window.FindElement('_DISPLAY_')
    if valid_pin!='':
        Found='True'
    else:
        Found='False'
    if event is None:
        break
    if event in ['return']:
        cancel_click()
    if event in ['clear']:
        clear_click()
    if event in ['←']:
        if option_letter=='':
            account_number=account_number[:-1]
            window['_DISPLAY_'].update(account_number)
        else:
            pin=pin[:-1]
            window['_DISPLAY_'].update(pin)
    if event is not None:
        event = event.lower()
        account_number_entry(option_letter, list_event, event)
        if event in ['a','b','c','d','e','f'] and account_number!='':
            option_letter=event
        if event in ['k','s','q']:
            ocr()
            adjust_sharpness()
            
#--------PART A--------------------------------#            
        if option_letter in ['a']:
            window['_DISPLAY_'].update('Enter PIN\nto register:')
            if event in list_event:
                pin_update(event)
            if event in ['enter']:
                mycursor.execute(f'INSERT INTO accountandpin (account,pin)VALUES({account_number},{pin})')
                mycursor.execute('INSERT INTO pinandamount (pin,amount)VALUES(%s,%s)',(pin,'0'))
                mydb.commit()
                window['_DISPLAY_'].update('PIN registered\nPress Return to return to\nmain menu')
           
#----------PART B-----------------------------#
        if option_letter in ['b']:
            proper_pin_login(event, list_event)
            if Found == 'True':
                amount()
                for x in myresult:
                    window['_DISPLAY_'].update(x)
            if Found == 'Return':
                window['_DISPLAY_'].update('Wrong Pin entered')

#----------PART C----------------------------#
        if option_letter in ['c']:
            proper_pin_login(event, list_event)
            if Found == 'True' and counter==0:
                pin, counter='', 1
                window['_DISPLAY_'].update('Enter amount to deposit:')
            elif event in list_event and counter==1:
                total_amount=total_amount+event
                window['_DISPLAY_'].update(total_amount)
            elif event in ['enter']:
                amount()
                for x in myresult:
                    total_amount=int(total_amount)+int(x[0])
                total_amount=str(total_amount)
                mycursor.execute('UPDATE pinandamount SET amount=%s WHERE pin=%s',(total_amount, valid_pin))
                mydb.commit()
                window['_DISPLAY_'].update('Amount deposited\nReturn to return to menu')
            if Found == 'Return':
                window['_DISPLAY_'].update('Wrong Pin entered')

#--------------PART D--------------------#
        if option_letter in ['d']:
            proper_pin_login(event, list_event)
            if Found == 'True' and counter==0:
                pin, counter='', 1
                window['_DISPLAY_'].update('Enter amount to withdraw')
            elif event in list_event and counter==1:
                total_amount=total_amount+event
                window['_DISPLAY_'].update(total_amount)
            elif event in ['enter']:
                amount()
                for x in myresult:
                    if int(total_amount) > int(x[0]):
                        window['_DISPLAY_'].update('Not enough account balance\nReturn to main menu')
                    else:
                        total_amount=int(x[0])-int(total_amount)
                        total_amount=str(total_amount)
                        mycursor.execute('UPDATE pinandamount SET amount=%s WHERE pin=%s',(total_amount, valid_pin))
                        mydb.commit()
                        window['_DISPLAY_'].update('Amount withdrawn\nReturn to return to menu')
            if Found == 'Return':
                window['_DISPLAY_'].update('Wrong Pin entered')

#----------------PART E---------------#
        if option_letter in ['e']:
            proper_pin_login(event, list_event)
            if Found=='True' and counter==0:
                pin, counter='', 1
                window['_DISPLAY_'].update('Enter new PIN')
            elif event in list_event and counter==1:
                pin_update(event)
            elif event in ['enter']:
                mycursor.execute('UPDATE accountandpin SET pin=%s WHERE account=%s',(pin,account_number))
                mycursor.execute('UPDATE pinandamount SET pin=%s WHERE pin=%s',(pin, valid_pin))
                mydb.commit()
                valid_pin = pin
                window['_DISPLAY_'].update('PIN changed\nReturn to main menu')

#---------------PART F----------------#
        if option_letter in ['f']:
            proper_pin_login(event, list_event)
            if Found == 'True' and counter==0:
                pin, counter='', 1
                window['_DISPLAY_'].update('Enter mobile number')
            elif event in list_event and counter==1:
                mobile_number = mobile_number+event
                window['_DISPLAY_'].update(mobile_number)
            elif event in ['enter'] and counter==1:
                window['_DISPLAY_'].update('Enter amount to recharge')
                counter=2
            elif event in list_event and counter==2:
                total_amount=total_amount+event
                window['_DISPLAY_'].update(total_amount)
            elif event in ['enter'] and counter==2:
                amount()
                for x in myresult:
                    if int(total_amount) > int(x[0]):
                        window['_DISPLAY_'].update('Not enough account balance\nReturn to main menu')
                    else:
                        total_amount=int(x[0])-int(total_amount)
                        total_amount=str(total_amount)
                        mycursor.execute('UPDATE pinandamount SET amount=%s WHERE pin=%s',(total_amount, valid_pin))
                        mydb.commit()
                        window['_DISPLAY_'].update('Balance updated\nReturn to return to menu')
            if Found == 'Return':
                window['_DISPLAY_'].update('Wrong Pin entered')
