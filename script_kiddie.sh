#!/bin/bash

while true; do
   Xvfb :10 -ac &
   pid=$!;
   sleep 5;
   DISPLAY=:10 python script_kiddie.py;
   kill -INT $pid;
   sleep 60;
   kill -KILL $pid;
   sleep 30;
   rm -rf /tmp/tmp*
done
