pid=`cat pid.txt`
echo $pid
kill $pid
echo "Server is stopped now!"
