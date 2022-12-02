#!/bin/bash

echo > out.txt
stress-ng --sequential 0 -t 5s
cat out.txt
