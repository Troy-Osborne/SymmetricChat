from random import randint
from struct import pack,unpack

import hashlib
def wrap(a,b):
    if a<0:
        return wrap(a+b,b)
    elif a>=b:
        return wrap(a-b,b)
    else:
        return a


def XORbytes(data1: bytes, data2: bytes) -> bytes:
    # Convert inputs to bytearrays for mutability and use memoryview for efficient slicing
    length = min(len(data1), len(data2))  # XOR only up to the length of the shorter input
    result = bytearray(length)
    view1 = memoryview(data1)
    view2 = memoryview(data2)
    
    # XOR byte by byte
    for i in range(length):
        result[i] = view1[i] ^ view2[i]

    return bytes(result)

def EncryptEntropy(Entropy,Key):#replace with more complex later
    Keydigest=hashlib.sha512()
    Keydigest.update(Key)
    KeyHash=Keydigest.digest()
    Keydigest.update(Key+b" Salty "+Key)
    KeyHash+=Keydigest.digest()
    EntropyLength=len(Entropy)
    KeyLength=len(Key)
    vals=[int(KeyLength**(1+n/64)+(EntropyLength/(3-n/64)**2)+(n**1.6)*64+KeyLength*17+EntropyLength*2)%256 for n in range(64)]
    pos=0
    out=b""
    while pos<EntropyLength:
        out+=pack("B",wrap((Entropy[0]+(KeyHash[pos%128]+vals[pos%64]+vals[(pos+2)%64]+Key[pos%KeyLength])),256))
        Entropy=Entropy[1:]
        
        pos+=1
    return out

def DecryptEntropy(Entropy,Key):#replace with more complex later
    Keydigest=hashlib.sha512()
    Keydigest.update(Key)
    KeyHash=Keydigest.digest()
    Keydigest.update(Key+b" Salty "+Key)
    KeyHash+=Keydigest.digest()
    EntropyLength=len(Entropy)
    KeyLength=len(Key)
    vals=[int(KeyLength**(1+n/64)+(EntropyLength/(3-n/64)**2)+(n**1.6)*64+KeyLength*17+EntropyLength*2)%256 for n in range(64)]
    pos=0
    out=b""
    #Reverse Process
    while pos<EntropyLength:
        out+=pack("B",wrap((Entropy[0]-(KeyHash[pos%128]+vals[pos%64]+vals[(pos+2)%64]+Key[pos%KeyLength])),256))
        Entropy=Entropy[1:]
        
        pos+=1
    return out
        
def EncryptBytes(Input,Key,Entropy):
    EncryptedEntropy=EncryptEntropy(Entropy,Key)
    #print("Encrypted Entropy")#debug only
    #print(EncryptedEntropy)
    EncryptedText=XORbytes(Entropy,Input)
    Output=EncryptedEntropy+EncryptedText
    return Output

def DecryptBytes(Input,Key):
    mid=len(Input)//2
    EncryptedEntropy=Input[:mid]
    #EncryptEntropy(Entropy,Key)
    EncryptedText=Input[mid:]

    #XORbytes(Entropy,Input)
    Entropy=DecryptEntropy(EncryptedEntropy,Key)
    return XORbytes(Entropy,EncryptedText)


Key=input("Please Enter Your Password").encode("utf-8")

#Key=b"Password Test"
EntropyFile=open("C:/Users/User/Documents/Crypt/entropy.noise","rb")
if __name__=="__main__":
    ###TEST VERSION###
    Message=b"Verify receipt with code: R3c31p7 V3r1f13d";MessageLength=len(Message)
    
    EntropyFile=open("C:/Users/User/Documents/Crypt/entropy.noise","rb")
    Entropy=EntropyFile.read(len(Message))#load as many bytes entropy as exist in the Message
    EntropyLength=len(Entropy)
    if len(Entropy)<MessageLength:
        print("Entropy file too small, please create more random data")
        print("Alternatively if security isn't of extreme importance it can be filled with pythons deterministic pseudorandom")
        print("To use python random type \"pr\" or type anything else to cancel")
        if input("->").lower()=="pr":
            print("Please Wait Filling with Python Random")
            while EntropyLength<MessageLength:
                EntropyLength+=1
                pack("B",randint(256))
    Encrypted=EncryptBytes(Message,Key,Entropy)
    plain=DecryptBytes(Encrypted,Key)
    print("CipherText")
    print(Encrypted)
    print("Decrypted PlainText")
    print(plain)

