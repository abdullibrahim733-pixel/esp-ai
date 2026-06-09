try:
    from display import Display
    disp = Display()
except:
    disp = None

from server import Server

print("=== ESP32 Ollama Chat ===")
sv = Server(display=disp)
print(f"Config loaded — WiFi: '{sv.cfg.get('WIFI_SSID', '?')}'")
if sv.connect_wifi():
    sv.run()
else:
    import machine
    print("WiFi failed — will retry in 30s")
    import time
    time.sleep(30)
    machine.reset()
