#!/bin/bash

INPUT_FILE=${1:-'Contacts.pdf'}
TODAY=$(date +%Y%m%d)
DEF_OUTPUT=${TODAY}.txt
OUTPUT_FILE=${2:-$DEF_OUTPUT}

ps2ascii $INPUT_FILE | grep -v 'Lehi.*YSA' |  grep -v 'For Church Use' | grep -v 'Preferred Name' | grep -v 'Count:' | sed -e 's/^\s\+\(\S.*\)/\1/g' | sed -e 's/  \+\(\S\)/|\1/g' > $OUTPUT_FILE
python3 ./lds_contacts_v3.py -i $OUTPUT_FILE -o ${OUTPUT_FILE%.txt}.vcard -g LEHI_YSA_2
#if [ $? -eq 0 ]; then
#    rm -rf $OUTPUT_FILE
#fi
