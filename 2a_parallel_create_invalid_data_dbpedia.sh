#!/usr/bin/env bash

if [[ $# -ne 3 ]]; then
    echo "Usage: 2a_parallel_create_invalid_data_dbpedia.sh <data_dir> </path/to/predicates_file> </path/to/mapping_file>" >&2
    exit 2
fi

data_dir=$1
predicates_file=$2
mapping_file=$3

dbpedia_dir=${data_dir}/dbpedia/
if [ ! -d "$dbpedia_dir" ]; then
    echo "DBPedia directory not found in $data_dir. Please run 0_download_data.sh first" >&2
    exit 2
fi

predicate_wise_datadir=$dbpedia_dir/predicate_wise_datafiles/
if [ ! -d "$predicate_wise_datadir" ]; then
    echo "Predicate wise data directory not found in $data_dir. Please run 1_extract_predicate_specific_records.sh before running this script" >&2
    exit 2
fi

log_dir=$data_dir/question_generation_logs
mkdir -p $log_dir

echo "Starting question generation..."
for pred_name in `cat $predicates_file`; 
do 
    pred_name_clean=${pred_name/http:\/\/dbpedia.org\/ontology\//}
    python 2_create_invalid_questions_dbpedia.py --data_dir $data_dir --predicates $pred_name --mapping_file $mapping_file 2>&1 > $log_dir/$pred_name_clean &
done

# Wait till all background jobs complete
echo "Question generation processes running in background, waiting to complete..."
wait
echo "Done! All generated questions stored in $data_dir/dbpedia/predicate_wise_questions/, logs are in $log_dir"
