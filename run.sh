#!/bin/bash

timeoutInSeconds=600
totalTime=0

if [ ! -f ttp-checker ]; then
    echo "Before running this script you need to unzip the ttp-checker (compiled for your OS) in this directory."
    exit 0
fi

chmod +x project2.py ttp-checker

for f in public-tests/*.ttp
# for f in public-tests/t20.ttp
do
    fbase="${f%.*}"
    fbase=$(basename $fbase)
    outfile=public-tests/"$fbase.myout"
    checkfile=public-tests/"$fbase.check"
    echo "Executing on instance $f"
    startTime=$(date +%s.%N)
    time timeout $timeoutInSeconds"s" ./project2.py < "$f" > "$outfile"
    endTime=$(date +%s.%N)
    elapsedTime=$(echo "$endTime - $startTime" | bc)
    totalTime=$(echo "$totalTime + $elapsedTime" | bc)
    ./ttp-checker "$f" "$outfile" > "$checkfile"
    cat "$checkfile"
    printf "Cumulative time so far: %.2f seconds\n" "$totalTime"
    echo
    echo
    echo
done
