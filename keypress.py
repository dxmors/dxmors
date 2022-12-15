import keyboard

num = 1
while True:
    i = True
    while i:
        if keyboard.is_pressed('y'):
            break
        if keyboard.is_pressed('n'):
            i = False
    num+=1
    print(f"try {num}")