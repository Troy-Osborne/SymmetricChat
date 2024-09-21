from copy import copy
from functools import reduce
from itertools import zip_longest
from struct import pack
from random import random
from time import time
import math
import hashlib

try:
    import win32api
    win32api.GetCursorPos()
    WINMOUSE=True
except:
    WINMOUSE=False

try:
    import pyaudio
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100 #44100Khz
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)
    ##Open Microphone
    USINGMIC=True
except:
    USINGMIC=False

print("Using Mic" if USINGMIC else "Mic Unavailable")
#replace with a test to see i mouse is available
if WINMOUSE==False:
    USINGMOUSE=False
else:
    USINGMOUSE=True

print("Using Mouse" if USINGMIC else "Mouse Unavailable")

def grouper(iterable, n, fillvalue=None):
    "Collect data into fixed-length chunks or blocks"
    # grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx"
    args = [iter(iterable)] * n
    return zip_longest(*args, fillvalue=fillvalue)

        
class entropypool:
    def __init__(self,maxsize=2**32):
        self.maxsize=maxsize
        self.bytecount=0
        self.Digest=hashlib.sha512()
        self.pool=b""
    def addbits(self,bits):
        if self.bytecount<self.maxsize:
            self.Digest.update(bytes(bits))
            val=self.Digest.digest()
            length=len(val)
            self.pool+=val
            self.bytecount+=length
            if random()<0.05:
                #1 in 20 change to reset digest
                self.Digest=hashlib.sha512()
        else:
            #reached maximum size
            pass
                        


class entropypoolfile:#write directly to file (Doesn't use max size atm)
    def __init__(self,filename="entropy.noise",maxsize=2**32):
        self.bytes=b""#every 256 bytes add to pool
        self.bytecount=0
        self.outfile=open(filename,"wb")
        self.Digest=hashlib.sha512()
    def addbits(self,bits):
        self.Digest.update(bytes(bits))
        val=self.Digest.digest()
        length=len(val)
        self.bytes+=val
        self.bytecount+=length
        if self.bytecount>=2048:
            toadd=copy(self.bytes[0:2048]) #copy first 2048 bits
            self.bytes=b"" #remove those bits from the FIFO stack
            self.bytecount=0 #subtract them front the bit count
            self.outfile.write(toadd)
            self.outfile.flush()
            #append bytes to pool
            #print('256 New Bytes Added to Pool:')
            #print(len(self.Pool)) #print pool volume in bytes
            del toadd #delete the copy from memory

class entropypoolfileNODIGEST: #write directly to file without hashing the inputs (used for checking bias on SHA-2 inputs)
    def __init__(self,filename="entropyNODIGEST.noise",maxsize=2**32):
        self.maxsize=maxsize
        self.bits=[]#every 256 bytes add to pool
        self.bitcount=0
        self.outfile=open(filename,"wb")
    def addbits(self,bits):
        length=len(bits)
        self.bits+=bits
        self.bitcount+=length
        while self.bitcount>=2048:
            toadd=copy(self.bits[0:2048]) #copy first 2048 bits
            self.bits=self.bits[2048:] #remove those bits from the FIFO stack
            self.bitcount-=2048 #subtract them front the bit count
            mybytes = bytes([reduce(lambda byte, bit: byte << 1 | bit, eight_bits) for eight_bits in grouper(toadd, 8, fillvalue=0)]) #convert 2048 bits into 256 bytes
            self.outfile.write(mybytes)
            self.outfile.flush()
            #append bytes to pool
            #print('256 New Bytes Added to Pool:')
            #print(len(self.Pool)) #print pool volume in bytes
            del toadd #delete the copy from memory
            del mybytes #delete the bytes from memory (they're in self.pool now)

def GetMicLSBs():#get least significant bits of microphone
    currentchunk=stream.read(CHUNK,exception_on_overflow=False)
    val=currentchunk[7]+currentchunk[8]
    return list(int(i) for i in bin(val)[6:])
    
    
    
pool=entropypoolfile("ChatEntropy.noise")
#pool=entropypoolfileNODIGEST()## For bias checking
if USINGMOUSE:
    MousePos=win32api.GetCursorPos()
    print("Keep Moving Your Mouse")
if USINGMIC:
    print("Keep Making Noise.\n\nMake sure there is ample background noise, breathing, fans, music, tapping on computer, dragging mouse near microphone, anything will help, the more the better.")
while 1:
    NewBin=[round(random())]
    if USINGMOUSE:
        #Get From Mouse
        NewPos=win32api.GetCursorPos()
        if MousePos!=NewPos:
            MouseMovementX=MousePos[0]-NewPos[0]
            MouseMovementY=MousePos[1]-NewPos[1]
            if MouseMovementX>0:
                NewBin+=[int(i) for i in bin(MouseMovementX+NewPos[0]%16)[2:]]
            elif MouseMovementX<0:
                NewBin+=[int(i) for i in bin(MouseMovementX-NewPos[0]%16)[3:]]
            else:
                NewBin.append(round(random()))
            if MouseMovementY>0:
                NewBin+=[int(i) for i in bin(MouseMovementY+NewPos[1]%16)[2:]]
            elif MouseMovementY<0:
                NewBin+=[int(i) for i in bin(MouseMovementY-NewPos[1]%16)[3:]]
            else:
                NewBin.append(round(random()))
            MousePos=NewPos
    if len(NewBin)>1:
        ##uses milli/nano-seconds of mouse movements for noise
        timestr=str(time())
        lts=len(timestr)
        if lts<18:
            timestr+="0"*(18-lts)
        #time defaults to truncating off any trailing zeros so check that it doesn't fall precisely on a time lacking trailing nanoseconds
        timenum=int(timestr[14:])%2048
        mousetimebits=[int(i) for i in bin(timenum)[2:]] #clip time and turn nanoseconds into binary
        ltb=len(mousetimebits)
        if ltb<11:
           mousetimebits=[0]*(11-ltb)+mousetimebits
        NewBin+=mousetimebits #add the time to the newbin binary stream
    #Get From Keypresstime (key + milliseconds since last key)
    #Get From Microphone
    if USINGMIC:
        NewBin+=GetMicLSBs()
    if len(NewBin)>1:
        pool.addbits(NewBin) #add the bits to the entropy pool class                  
