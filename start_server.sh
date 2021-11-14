pidfile=`grep pidfile abhishekS.conf | cut -b 11-`
python3 http-server.py &
echo $pidfile
echo $! > $pidfile
