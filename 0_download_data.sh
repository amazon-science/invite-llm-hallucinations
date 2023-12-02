#!/usr/bin/env bash

if [[ $# -ne 1 ]]; then
    echo "Usage: 0_download_data.sh <data_dir>" >&2
    exit 2
fi

datadir=$1

# Update these links if necessary
dbpedia_url=https://databus.dbpedia.org/dbpedia/collections/latest-core
persondata_url=http://downloads.dbpedia.org/2016-10/core-i18n/en/persondata_en.ttl.bz2
triviaqa_url=https://nlp.cs.washington.edu/triviaqa/data/triviaqa-rc.tar.gz

echo "------------------------------------Fetching DBPedia---------------------------------------"
echo ""
# Download DBPedia
dbpedia_datadir=$datadir/dbpedia
mkdir -p $dbpedia_datadir
cd $dbpedia_datadir
query=$(curl -H "Accept:text/sparql" $dbpedia_url)
files=$(curl -X POST -H "Accept: text/csv" --data-urlencode "query=${query}" https://databus.dbpedia.org/sparql | tail -n +2 | sed 's/\r$//' | sed 's/"//g' | grep -E 'mappingbased-objects_lang\=en.ttl|mappingbased-literals_lang\=en.ttl|geo-coordinates_lang=en.ttl')

for fname in $files; 
do 
    wget $fname;
    fname=`echo $fname | awk -F/ '{ print $NF }'`;
    bunzip2 $fname; 
    mv ${fname}.out ${fname/.bzip2/};
done
cat geo-coordinates_lang\=en.ttl | cut -d/ -f5 | sort | uniq > all_geolocations.txt

# Fetch person data from alternate DBPedia URL since
# the file in latest core is empty,
wget $persondata_url
bunzip2 persondata_en.ttl.bz2
cat persondata_en.ttl | cut -d/ -f5 | sort | uniq > all_persons.txt

echo "------------------------Done with DBPedia, fetching TriviaQA now---------------------------"
echo ""

# Download TriviaQA
triviaqa_datadir=$datadir/triviaqa
mkdir -p $triviaqa_datadir
cd $triviaqa_datadir
wget $triviaqa_url
tar -xvzf triviaqa-rc.tar.gz qa/*
echo "-----------------------------------------Done-----------------------------------------------"
