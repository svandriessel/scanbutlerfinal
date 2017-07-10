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
screenWidth=480
screenHeight=320
root.geometry(str(screenWidth)+"x" + str(screenHeight))
root.configure(background='white')

list_of_barcodes = [65833254, 12345678, 22222222, 33333333, 44444444]
productcode = 00000000
currentProduct = None
scannedProducts = []
productBeschrijving=' '
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
    #prepareBarcodeSend()


    global productBeschrijving
    global currentProductIndex
    
    #het volgende artikel wordt gescand
    i = random.randint(0,4)
    productcode = list_of_barcodes[i]

    #scannedProducts.append(productcode)
    if productcode == 22222222:
        productBeschrijving = 'Yoghurt'
        
    elif productcode == 65833254:
        productBeschrijving = 'melk'
        
    elif productcode == 12345678:
        productBeschrijving = 'Banaan'
        
    elif productcode == 33333333:
        productBeschrijving = 'Brood'
        
    elif productcode == 44444444:
        productBeschrijving = 'Kiwi'

    exists=False
    for p in scannedProducts:
        if p.count(productBeschrijving)!=0:
            exists=True
            p[1]+=1
            currentProductIndex=scannedProducts.index(p)
##            addOneToAantal(currentProductIndex)
            select_product()
            break
    if exists==False:    
        artikel=[productBeschrijving, 1]
        scannedProducts.append(artikel)
        currentProductIndex=len(scannedProducts)-1
        select_product()
##        addProductToTable()

    


    print(productcode)
    print(scannedProducts)

def clear_products():
    global currentProductIndex
    
    productCode = 00000000
    scannedProducts[:] = []
    product_text.delete('1.0', END)
    currentProductIndex=None
    prepareBackToStart()
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
    w1.itemconfig(textID, text="\n"+str(scannedProducts[currentProductIndex][1]))
    product_text.delete('1.0', END)
    if productBeschrijving!='':
        product_text.insert('1.0', str(scannedProducts[currentProductIndex][1]), CENTER)
        if productBeschrijving=='Yoghurt':
            photo2 = createImage("yoghurt.gif")
        elif productBeschrijving == 'melk':
            photo2 = createImage("milk2.gif")
        elif productBeschrijving == 'Banaan':
            photo2 = createImage("banaan.gif")
        elif productBeschrijving == 'Brood':
            photo2 = createImage("brood.gif")
        elif productBeschrijving == 'Kiwi':
            photo2 = createImage("kiwi.gif")
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
    global currentProductIndex
    global productBeschrijving
    
    if currentProductIndex!=None and productBeschrijving!='':
        if scannedProducts[currentProductIndex][1]>1:
            scannedProducts[currentProductIndex][1]-=1
##            subtractOneOfAantal(currentProductIndex)
            print('subtract one')
            select_product()
        elif scannedProducts[currentProductIndex][1]==1:
            scannedProducts.remove(scannedProducts[currentProductIndex])
##            refreshTable()
            currentProductIndex=None
            productBeschrijving=''
            print('subtract to 0')
##            photo2 = PhotoImage(file="")
##            picture_label.configure(image = photo2)
##            picture_label.image=photo2
##            resetToStart()
            prepareBackToStart()
            #clear_products()


def resetToStart():
    photo2 = createImage("logo.png")
    picture_label.configure(image = photo2)
    picture_label.image=photo2
    w1.itemconfig(textID, text="\n")

def cancelProduct():
    clear_products()
    #root.wm_attributes("-fullscreen", "false")
    #root.geometry(str(screenWidth)+"x" + str(screenHeight))
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
    print("\n\n"+str(header)+"\n\n")
    try:
        r = requests.post("https://api.scanbutler.nl/V1/user/storage/checkout", data=productData, headers=header)
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
    showOnbekend()

def productAddingSuccesfull():
    print("happyface")
    showSucces()

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
        loginRequest = {}
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

def removeStart():
    #later kan ik hier een pass van maken
    startButton.grid_remove()
    volgende_artikel()

def backToStart():
    startButton.grid()

def prepareBackToStart():
    resetToStart()
    backToStart()

def showSucces():
    succesButton.grid()

def showOnbekend():
    onbekendButton.grid()

def removeSucces():
    succesButton.grid_remove()
    prepareBackToStart()
    
def removeOnbekend():
    onbekendButton.grid_remove()
    prepareBackToStart()

def imagePreparer(filename):
    image = Image.open(filename)
    image = image.rotate(90)
    image = imageScaler(image)
    return ImageTk.PhotoImage(image)

def imageScaler(image):
    return image.thumbnail(256, 256)

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

empty_label1 = Label(root, width=1, bg='white')
empty_label1.grid(row=0, column=0, rowspan=3)

##empty_label2 = Label(root)
##empty_label2.grid(row=2, column=0, rowspan=4)

picture_label = Label(root, image=photo, width=256, height=256, bg='white')
picture_label.photo=photo
picture_label.grid(row=0, column=1, rowspan=3)


quitFrame=Frame(root)
quitFrame.grid(row=0, column=1, sticky=NW)

quitPhoto = createImage("cancel.png")
quitPoppup = Button(quitFrame, text="Minus", image=quitPhoto, activebackground='white', relief=SUNKEN, highlightthickness=0, highlightbackground='white', borderwidth=0, bg='white', command=cancelProduct)#, command = quitPoppup)
quitPoppup.photo=quitPhoto
quitPoppup.pack(anchor=NW)

w1 = Canvas(root, height="2c", width="2c", relief=SUNKEN, highlightthickness=0, highlightbackground='white', borderwidth=0, bg="white")
textID = w1.create_text(5, 5, anchor="e", font=("Arial",50), angle=90, text="\n")
w1.grid(row=1, column=2)


product_text = Text(root, font=("Arial",50), fg='#4d4848', height=1, width=2, relief=FLAT, highlightthickness=0, highlightbackground='white')
product_text.tag_configure("center", justify='center')
#product_text.grid(row=1, column=2)
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

plusPhoto = createImage("plus.png")
plus1 = Button(root, text="plus", image=plusPhoto, fg="blue", width=100, height=111, activebackground='white', relief=SUNKEN, highlightthickness=0, highlightbackground='white', borderwidth=0, bg='white', command = plusOne)
plus1.photo=plusPhoto
minusPhoto = createImage("min.png")
Minus1 = Button(root, text="Minus", image=minusPhoto, fg="blue", width=100, height=111, activebackground='white', relief=SUNKEN, highlightthickness=0, highlightbackground='white', borderwidth=0, bg='white', command = MinusOne)
Minus1.photo=minusPhoto

plus1.grid(row=0, column=2)
Minus1.grid(row=2, column=2)

artikel_button = Button(root, text="O", fg="red", command = volgende_artikel, height=3)
artikel_button.grid(row=0, column=4, rowspan=3)
##
##clear_button = Button(root, text="Clear", fg="red", command = clear_products, width=20)
##clear_button.grid(row=4, column=1)

confirmPhoto = createImage("confirm.png")
confirm_button = Button(root, image=confirmPhoto, bg='white', activebackground='white', relief=SUNKEN, highlightthickness=0, highlightbackground='white', borderwidth=0, width=80, height=310, command = confirmProduct)
confirm_button.photo=confirmPhoto
confirm_button.grid(row=0, column=3, rowspan=3)

startPhoto = createImage("start.png")
startButton = Button(root, image=startPhoto, bg='white', activebackground='white', relief=SUNKEN, highlightthickness=0, highlightbackground='white', borderwidth=0, width=screenWidth, height=screenHeight, command = removeStart)
startButton.photo=startPhoto
startButton.grid(row=0, column=0, rowspan=5, columnspan=5)

onbekendPhoto = createImage("onbekend.png")
onbekendButton = Button(root, image=onbekendPhoto, bg='white', activebackground='white', relief=SUNKEN, highlightthickness=0, highlightbackground='white', borderwidth=0, width=screenWidth, height=screenHeight, command = removeOnbekend)
onbekendButton.photo=onbekendPhoto
onbekendButton.grid(row=0, column=0, rowspan=5, columnspan=5)
onbekendButton.grid_remove()

succesPhoto = createImage("succes.png")
succesButton = Button(root, image=succesPhoto, bg='white', activebackground='white', relief=SUNKEN, highlightthickness=0, highlightbackground='white', borderwidth=0, width=screenWidth, height=screenHeight, command = removeSucces)
succesButton.photo=succesPhoto
succesButton.grid(row=0, column=0, rowspan=5, columnspan=5)
succesButton.grid_remove()


    


_thread.start_new_thread(loop,())
root.mainloop()
