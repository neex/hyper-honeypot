#!/bin/bash

while true; do
   Xvfb :10 -ac &
   pid=$!;
   sleep 5;
   DISPLAY=:10 python script_kiddie.py 2>&1;
   kill -INT $pid;
   sleep 5;
   kill -KILL $pid;
   sleep 2;
   rm -rf /tmp/tmp*
done
