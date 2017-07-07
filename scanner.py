# -*- coding: utf-8 -*-

from tkinter import *

import PIL
import json
import requests
import datetime

import time
import random
import _thread
import subprocess
from PIL import Image, ImageTk

root = Tk()
root.wm_attributes("-fullscreen", "true") #fullscreen wo title
#root.wm_attributes("-type", "splash")
screenWidth=320
screenHeight=480
root.geometry(str(screenWidth)+"x" + str(screenHeight))
root.configure(background='white')

list_of_barcodes = [65833254, 12345678, 22222222, 33333333, 44444444]
productcode = 00000000
currentProduct = None
scannedProducts = []
global productBeschrijving
productBeschrijving=' '
global currentProductIndex
currentProductIndex=None
#photo = PhotoImage(file="logo.png")
productCost=1.00

def createImage(filename):
    image = Image.open(filename)
    image = image.rotate(90)
    return ImageTk.PhotoImage(image)

#myimage = Image.open("logo.png")
#myimage = myimage.rotate(90)
#photo = ImageTk.PhotoImage(myimage)
photo = createImage("logo.png")

dataFromApi=""
tokenInfoAPI=""
connectionEstablished = False
timeConnectionEstablished = None

def loop():
    while 1:
        update_info()
        time.sleep(0.1)
        
    
def volgende_artikel():
    #nieuwe code API calls
    prepareBarcodeSend()


    
    #het volgende artikel wordt gescand
    i = random.randint(0,4)
    productcode = list_of_barcodes[i]

    #scannedProducts.append(productcode)
    if productcode == 22222222:
        global productBeschrijving
        productBeschrijving = 'Yoghurt'
        
    elif productcode == 65833254:
        global productBeschrijving
        productBeschrijving = 'melk'
        
    elif productcode == 12345678:
        global productBeschrijving
        productBeschrijving = 'Banaan'
        
    elif productcode == 33333333:
        global productBeschrijving
        productBeschrijving = 'Brood'
        
    elif productcode == 44444444:
        global productBeschrijving
        productBeschrijving = 'Kiwi'

    exists=False
    for p in scannedProducts:
        if p.count(productBeschrijving)!=0:
            exists=True
            p[1]+=1
            global currentProductIndex
            currentProductIndex=scannedProducts.index(p)
##            addOneToAantal(currentProductIndex)
            select_product()
            break
    if exists==False:    
        artikel=[productBeschrijving, 1]
        scannedProducts.append(artikel)
        global currentProductIndex
        currentProductIndex=len(scannedProducts)-1
        select_product()
##        addProductToTable()

    


    print(productcode)
    print(scannedProducts)

def clear_products():
    productCode = 00000000
    scannedProducts[:] = []
    product_text.delete('1.0', END)

    photo2 = PhotoImage(file="")
    picture_label.configure(image = photo2)
    picture_label.image=photo2
    global currentProductIndex
    currentProductIndex=None
##
##    row=0
##    for i in range(0, len(productenTabel)-1):
##        removeProduct(row)
##        row=row+1
##    print('all clear')

def update_info():
    
    list_text.delete('1.0', END)
    for p in scannedProducts:
        list_text.insert('1.0', p[0]+' '+ str(p[1]) + '\n', CENTER)

def select_product():
    product_text.delete('1.0', END)
    if productBeschrijving!='':
        product_text.insert('1.0', str(scannedProducts[currentProductIndex][1]), CENTER)
        if productBeschrijving=='Yoghurt':
            photo2 = PhotoImage(file="yoghurt.gif")
        elif productBeschrijving == 'melk':
            photo2 = PhotoImage(file="milk2.gif")
        elif productBeschrijving == 'Banaan':
            photo2 = PhotoImage(file="banaan.gif")
        elif productBeschrijving == 'Brood':
            photo2 = PhotoImage(file="brood.gif")
        elif productBeschrijving == 'Kiwi':
            photo2 = PhotoImage(file="kiwi.gif")
        picture_label.configure(image = photo2)
        picture_label.image=photo2
        
    print(productBeschrijving)

def plusOne():
    if currentProductIndex!=None and productBeschrijving!='':
        if scannedProducts[currentProductIndex][1]!=9:
           scannedProducts[currentProductIndex][1]+=1
##           addOneToAantal(currentProductIndex)
           print('add one')
           select_product()

def MinusOne():
    if currentProductIndex!=None and productBeschrijving!='':
        if scannedProducts[currentProductIndex][1]>1:
            scannedProducts[currentProductIndex][1]-=1
##            subtractOneOfAantal(currentProductIndex)
            print('subtract one')
            select_product()
        elif scannedProducts[currentProductIndex][1]==1:
            scannedProducts.remove(scannedProducts[currentProductIndex])
##            refreshTable()
            global currentProductIndex
            currentProductIndex=None
            global productBeschrijving
            productBeschrijving=''
            print('subtract to 0')
            photo2 = PhotoImage(file="")
            picture_label.configure(image = photo2)
            picture_label.image=photo2
            select_product()

def cancelProduct():
    root.wm_attributes("-fullscreen", "false")
    root.geometry(str(screenWidth)+"x" + str(screenHeight))
    print("Cancel current product")

def prepareBarcodeSend():
    if prepareTransition():
        barcodeDict = prepareProductSend()
        if checkBarcode(barcodeDict.get("barcode")):
            print("Barcode was send")
        else:
            print("Barcode was not send succesfully")
        

def checkBarcode(productData):
    
    header = {"Authorization":tokenInfoAPI.get("access_token")}
    url = "https://api.scanbutler.nl/V1/product/" + productData
    print(url)
    try:
        r = requests.get(url)
        print(r.text)
        print("statuscode = " + r.statuscode)
        if r.statuscode >=100 and r.statuscode <300:
            print(r.text)
            file = open("barcodeTransmissionLog.txt", "a")
            dataDictionary = json.loads(r.text)
            file.write("\n" + "Current time: "+time.asctime() + "\n")
            print("dictionary created")
            json.dump(r.json(), file)
            print("file written")
            file.close()       
            print("barcode check succesfull")
            return True
        else:
            print("something went wrong with checking the barcode")
            return False
    except:
        print("something went wrong with checking the barcode")
        return False

def sendProduct(productData):
    #print("info: " + str(tokenInfoAPI) + str(tokenInfoAPI.get("access_token")))
    header = {"Authorization":tokenInfoAPI.get("access_token")}
    #print(header)
    try:
        r = requests.post("https://api.scanbutler.nl/V1/storage/checkout", data=productData, headers=header)
        print(r.text)
        print("statuscode = " + r.statuscode)
        if r.statuscode >=100 and r.statuscode <300:
            print(r.text)
            file = open("productTransmissionLog.txt", "w")
            dataDictionary = json.loads(r.text)
            print("dictionary created")
            json.dump(r.json(), file)
            print("file written")
            file.close()
            return True
        else:
            return False
        
    except:
        print("something went wrong with adding the product to checkout")
        return False

def confirmProduct():
    data = prepareProductSend()
    if prepareTransition():
        if sendProduct(data):
            print("product succesfully added")
            productAddingSuccesfull()
        else:
            print("product failed to be added")
            productAddingFailed()

def prepareProductSend():
    barcode = "8710466246424"
    data = {"barcode":barcode}
    return data

def productAddingFailed():
    print("sadface")

def productAddingSuccesfull():
    print("happyface")

def prepareTransition():
    if connectionEstablished:
        return True
    else:
        if establishConnection():
            return True
        else:
            time.sleep(5)
            if establishConnection():
                return True
            else:
                setupConnectionFailed()
                return False

def setupConnectionFailed():
    print("sadface + please check your internetconnection")

def establishConnection():
    global tokenInfoAPI
    global connectionEstablished
    global timeConnectionEstablished
    
    #file = open("dataSave.txt", "r")
    #print("first line= " + file.readline())
    #file.seek(0, 0)
    if connectionEstablished==False: #file.readline()=="":
        #file.close()
        print("starting request")
        loginRequest = {"grant_type":"password", "client_id":"1", "client_secret":"7jqsZLXvYCyaFkpLXaNZ800kduGtCj8LvyU3MjBo", "username":"svandersligte@hotmail.com", "password":"@Scanbutler54321", "scope":""}
        try:
            r = requests.post("https://api.scanbutler.nl/oauth/token", data=loginRequest)
            print(r.text)
            file = open("dataSave.txt", "w")
            dataDictionary = json.loads(r.text)
            print("dictionary created")
            json.dump(r.json(), file)
            #file.write(str(r.text) + "\n" + "Current time: "+time.asctime())
            print("file written")
            timeConnectionEstablished = time.time()
            print("time told")
            file.close()
            print("file closed")
            tokenInfoAPI=dataDictionary
            print("info updated")
            connectionEstablished = True
            print("Connection is established")
            _thread.start_new_thread(tokenTimer,())
            print("Thread to evaluate tokentime started")
            return True
        except:
            return False
    else:
        #tokenInfoAPI = file.readline()
        print("Connection was already established")
        return True
    
def tokenTimer():
    global connectionEstablished
    global timeConnectionEstablished
    while 1:
        if timeConnectionEstablished!=None:
            if time.time()>=timeConnectionEstablished + 30000000:
                connectionEstablished = False
                timeConnectionEstablished = None
                break
        else:
            break



##
##def removeProduct(row):
##    columnNumber=0
##    for columns in productenTabel[row]:
##        changeCel(row, columnNumber, ' ')
##        columnNumber=columnNumber+1
##
##def addOneToAantal(row):
##    #row=row+1
##    #productenTabel[row][1].configure(text=int (productenTabel[row][1].cget("text"))+1)
##    nieuwAantal=int (productenTabel[row+1][1].cget("text"))+1
##    print(nieuwAantal)
##    changeCel(row, 1, nieuwAantal)
##    changeCel(row, 3, "€" +  '%.2f' % (nieuwAantal * productCost))
##    
##
##def subtractOneOfAantal(row):
##    #row=row+1
##    #productenTabel[row][1].configure(text=int (productenTabel[row][1].cget("text"))-1)
##    nieuwAantal=int (productenTabel[row+1][1].cget("text"))-1
##    print(nieuwAantal)
##    changeCel(row, 1, nieuwAantal)
##    changeCel(row, 3, "€" +  '%.2f' % (nieuwAantal * productCost))
##
##def addProductToTable():
##    changeCel(currentProductIndex, 0, productBeschrijving)
##    changeCel(currentProductIndex, 1, "1")
##    changeCel(currentProductIndex, 2, "€" + '%.2f' % (productCost))
##    changeCel(currentProductIndex, 3, "€" + '%.2f' % (productCost))
##    
##def changeCel(row, column, text):
##    row=row+1
##    productenTabel[row][column].configure(text=text)
##
##def changeRow(row, textc0, textc1, textc2, textc3):
##    changeCel(row, 0, textc0)
##    changeCel(row, 1, textc1)
##    changeCel(row, 2, textc2)
##    changeCel(row, 3, textc3)
##
##def refreshTable():
##    i=1
##    global productenTabel
##    print(productenTabel)
##    for rows in productenTabel:
##        if i>currentProductIndex & i<len(productenTabel):
##            j=0
##            for columns in (0, len(productenTabel[i])):
##                productenTabel[i][columns].grid_configure(row=i+1, column=j)
##                j=j+1
##
##        i=i+1
##        
##
##
##    productenTabel+=[productenTabel.pop(currentProductIndex+1)]
##    i=0
##    for columns in productenTabel[currentProductIndex+1]:
##        productenTabel.append(columns[i])
##        productenTabel[currentProductIndex+1][i].grid_remove()
##        i=i+1
##    productenTabel.pop(currentProductIndex)
    
##    tableRow=[]
##    for j in range(4):
##        l = Label(listFrame, text='', font=("Arial", 10), fg='#0080FF', relief=FLAT, bg='white')
##        l.grid(row=i, column=j, sticky=NSEW, padx=1, pady=1)
##        tableRow.append(l)
##    productenTabel.append(tableRow)
    
##    row=0
##    for products in scannedProducts:
##        changeRow(row, products[0], products[1], "€" + str(productCost), "€" + str(productCost*products[1]))
##    print("refreshed")

#top_label = Label(root, text='Scan het volgende artikel', height=2, width=113, bg='light blue')
#top_label.grid(row=0, column=0, columnspan=9)

empty_label1 = Label(root, height=1, bg='white')
empty_label1.grid(row=0, column=0, columnspan=3)

##empty_label2 = Label(root)
##empty_label2.grid(row=2, column=0, rowspan=4)

picture_label = Label(root, image=photo, width=256, height=256, bg='white')
picture_label.photo=photo
picture_label.grid(row=1, column=0, columnspan=3)


quitFrame=Frame(root)
quitFrame.grid(row=1, column=2, sticky=NE)

quitPhoto = PhotoImage(file="cancel.png")
quitPoppup = Button(quitFrame, text="Minus", image=quitPhoto, activebackground='white', relief=SUNKEN, highlightthickness=0, highlightbackground='white', borderwidth=0, bg='white', command=cancelProduct)#, command = quitPoppup)
quitPoppup.photo=quitPhoto
quitPoppup.pack(anchor=NE)

product_text = Text(root, font=("Arial",50), fg='#4d4848', height=1, width=2, relief=FLAT, highlightthickness=0, highlightbackground='white')
product_text.tag_configure("center", justify='center')
product_text.grid(row=2, column=1)
product_text.insert('1.0', '00000000', CENTER)

list_text = Text(root, font=("Arial",20), height=5, width=40)
list_text.tag_configure("center", justify='center')
list_text.grid(row=3, column=1, columnspan=2)
list_text.insert('1.0', '00000000', CENTER)
list_text.grid_forget()
##
##listFrame=Frame(root, bg='#4d4848')
##listFrame.grid(row=2, column=1, columnspan=3)
##
##productenTabel =[]
##for i in range(7):
##    tableRow=[]
##    for j in range(4):
##        l = Label(listFrame, text='', font=("Arial", 10), fg='#0080FF', relief=FLAT, bg='white')
##        l.grid(row=i, column=j, sticky=NSEW, padx=1, pady=1)
##        tableRow.append(l)
##    productenTabel.append(tableRow)

#productenTabel[0][0].configure(text="Product", width=18, font=("Arial", 10, "bold"), fg='#0080FF')
#productenTabel[0][1].configure(text="Aantal", width=7, font=("Arial", 10, "bold"), fg='#0080FF')
#productenTabel[0][2].configure(text="Prijs", width=7, font=("Arial", 10, "bold"), fg='#0080FF')
#productenTabel[0][3].configure(text="Totaal", width=7, font=("Arial", 10, "bold"), fg='#0080FF')

#changeCel(0, 0, "Melk")
#changeCel(0, 1, "1")
#changeCel(0, 2, "€2,50")
#changeCel(0, 3, "€2,50")

plusPhoto = PhotoImage(file="plus.png")
plus1 = Button(root, text="plus", image=plusPhoto, fg="blue", width=111, height=100, activebackground='white', relief=SUNKEN, highlightthickness=0, highlightbackground='white', borderwidth=0, bg='white', command = plusOne)
plus1.photo=plusPhoto
minusPhoto = PhotoImage(file="min.png")
Minus1 = Button(root, text="Minus", image=minusPhoto, fg="blue", width=111, height=100, activebackground='white', relief=SUNKEN, highlightthickness=0, highlightbackground='white', borderwidth=0, bg='white', command = MinusOne)
Minus1.photo=minusPhoto

plus1.grid(row=2, column=2)
Minus1.grid(row=2, column=0)

artikel_button = Button(root, text="volgende artikel", fg="red", command = volgende_artikel, width=20)
artikel_button.grid(row=4, column=0, columnspan=3)
##
##clear_button = Button(root, text="Clear", fg="red", command = clear_products, width=20)
##clear_button.grid(row=4, column=1)

confirmPhoto = PhotoImage(file="confirm.png")
confirm_button = Button(root, image=confirmPhoto, bg='white', activebackground='white', relief=SUNKEN, highlightthickness=0, highlightbackground='white', borderwidth=0, width=310, height=80, command = confirmProduct)
confirm_button.photo=confirmPhoto
confirm_button.grid(row=3, column=0, columnspan=3)


_thread.start_new_thread(loop,())
root.mainloop()
