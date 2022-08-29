from socket import socket 
from threading import Thread 
from zlib import compress 
from mss import mss 
from zlib import decompress 
import pygame 
WIDTH = 1366 
HEIGHT = 768 
host='192.168.1.82' 
port=9000 
ch=int(input('Do you want to share your screen?\n1.Yes\n2.No\nEnter your choice : ')) 
if(ch==1): 
    def retreive_screenshot(conn): 
        with mss() as sct: # The region to capture 
            rect = {'top': 0, 'left': 0, 'width': WIDTH, 'height': HEIGHT} 
            while 'recording': # Capture the screen 
                img = sct.grab(rect) # Tweak the compression level here (0-9) 
                pixels = compress(img.rgb, 6) # Send the the pixels length 
                size = len(pixels) 
                size_len = (size.bit_length() + 7) // 8 
                conn.send(bytes([size_len])) # Send the actual pixels length 
                size_bytes = size.to_bytes(size_len, 'big') 
                conn.send(size_bytes) # Send pixels conn.sendall(pixels) 
                def server(): 
                    sock = socket() 
                    sock.bind((host, port)) 
                    try: 
                        sock.listen(5) 
                        print('Server started.')
                        while 'connected': 
                            conn, addr = sock.accept() 
                            print('Client connected IP:', addr) 
                            thread = Thread(target=retreive_screenshot, args=(conn,)) 
                        thread.start() 
                    finally: 
                        sock.close() 
                        server() 
elif ch==2: 
    def recvall(conn, length):
        buf=b'' 
        while len(buf) < length: 
            data = conn.recv(length - len(buf)) 
            if not data: return data 
        buf += data 
        return buf

    def client(): 
        pygame.init() 
        screen = pygame.display.set_mode((WIDTH, HEIGHT)) 
        clock = pygame.time.Clock() 
        watching = True 
        sock = socket() 
        sock.connect((host, port)) 
        try: 
            while watching: 
                for event in pygame.event.get(): 
                    if event.type == pygame.QUIT: 
                        watching = False 
                        break # Retreive the size of the pixels, the pixels length and pixels 
                size_len = int.from_bytes(sock.recv(1), byteorder='big') 
                size = int.from_bytes(sock.recv(size_len), byteorder='big') 
                pixels = decompress(recvall(sock, size)) # Create the Surface from raw pixels 
                img = pygame.image.fromstring(pixels, (WIDTH, HEIGHT), 'RGB') # Display the picture 
                screen.blit(img, (0, 0)) 
                pygame.display.flip()
                clock.tick(60) 
        finally: sock.close() 
        client() 
else: 
    print('Invalid Choice.')