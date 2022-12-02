#!/bin/bash

echo > out_.txt
stress-ng --sequential 0 -t 5s
cat out_.txt
