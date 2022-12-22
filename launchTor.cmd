:: put the path of the folder
set my_path=C:\\

cd %my_path%

wt.exe --window 0 new-tab -d %my_path% -command python server.py 12000
wt.exe --window 0 new-tab -d %my_path% -command python network.py 6666
wt.exe --window 0 new-tab -d %my_path% -command python relay.py r1 8000
wt.exe --window 0 new-tab -d %my_path% -command python relay.py r2 8001
wt.exe --window 0 new-tab -d %my_path% -command python relay.py r3 8002
wt.exe --window 0 new-tab -d %my_path% -command python client.py c1
