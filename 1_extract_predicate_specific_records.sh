#!/usr/bin/env bash

if [[ $# -ne 2 ]]; then
    echo "Usage: 1_extract_predicate_specific_records.sh <data_dir> <predicates_file>" >&2
    exit 2
fi

data_dir=$1
predicates_list_file=$2

dbpedia_dir=${data_dir}/dbpedia/
if [ ! -d "$dbpedia_dir" ]; then
    echo "DBPedia directory not found in $data_dir. Please run 0_download_data.sh first" >&2
    exit 2
fi

outdir=$dbpedia_dir/predicate_wise_datafiles/

mkdir -p $outdir    # Create directory if it does not exist
for pred in `cat $predicates_list_file`; do
    echo "Extracting data for $pred"
    pred_name=${pred/http:\/\/dbpedia.org\/ontology\//}
    cat $dbpedia_dir/mappingbased-literals_lang\=en.ttl $dbpedia_dir/mappingbased-objects_lang\=en.ttl | grep $pred > $outdir/$pred_name;
done
