#!/usr/bin/env python
"""
This script creates new batch of invalid questions for given
predicate type by distorting valid facts from DBPedia
"""

import os
import sys
import json
import random
import argparse
from copy import deepcopy
from collections import defaultdict


def clean_element(elem):
    if "<http://dbpedia.org/resource/" in elem and elem.endswith(">"):
        elem = elem.replace("<http://dbpedia.org/resource/", "")[:-1]
    elem = elem.split("_(")[0]
    if "CareerStation" in elem:
        elem = elem.split("CareerStation")[0]
    if "Tenure" in elem:
        elem = elem.split("Tenure")[0]
    if "^^<http://www.w3.org/2001/XMLSchema#gYear>" in elem:
        elem = elem.replace("^^<http://www.w3.org/2001/XMLSchema#gYear>", "")
    if '"' in elem:
        elem = elem.replace('"', "")
    elem = elem.replace("_", " ")
    elem = elem.strip()
    return elem


def check_person_name(cand):
    # Keep only names with two words to reduce noise
    if len(cand.split()) == 2:
        return True
    else:
        return False


template = {
    "valid_question": "",
    "invalid_question": "",
    "answer_to_invalid_question": "",
}

parser = argparse.ArgumentParser(
    description="Create invalid questions for given predicate(s) using DBPedia"
)
parser.add_argument(
    "--data_dir",
    help="File path to <data_dir> from step 0",
    required=True,
)
parser.add_argument(
    "--predicates",
    nargs="+",
    help="List of predicates to process in this round of data creation",
    required=True,
)
parser.add_argument(
    "--mapping_file",
    help="File containing json to map predicates to question and answer templates",
    required=True,
)
parser.add_argument("--random_seed", default=1000, type=int, help="Random seed value")
parser.add_argument(
    "--num_questions_to_generate",
    default=5000,
    type=int,
    help="Number of questions to sample",
)
args = parser.parse_args()

dbpedia_input_path = os.path.join(args.data_dir, "dbpedia")
if not os.path.exists(dbpedia_input_path):
    print(
        f"Error: DBPedia directory not found in {args.data_dir}, please run 0_download_data.sh first."
    )
    sys.exit(2)

predicate_wise_input_dir = os.path.join(
    args.data_dir, "dbpedia", "predicate_wise_datafiles"
)
if not os.path.exists(predicate_wise_input_dir):
    print(
        f"Error: Predicate wise data files not found in {args.data_dir}, please run 1_extract_predicate_specific_records.sh before running this script."
    )
    sys.exit(2)

output_dir = os.path.join(args.data_dir, "dbpedia", "predicate_wise_questions")
if not os.path.exists(output_dir):
    os.mkdir(output_dir)

persons_file = os.path.join(dbpedia_input_path, "all_persons.txt")
if not os.path.exists(persons_file):
    print(
        "Error: missing all_persons.txt in DBPedia directory, please rerun 0_download_data.sh and ensure there are no errors."
    )
    sys.exit(2)

geolocations_file = os.path.join(dbpedia_input_path, "all_geolocations.txt")
if not os.path.exists(geolocations_file):
    print(
        "Error: missing all_geolocations.txt in DBPedia directory, please rerun 0_download_data.sh and ensure there are no errors."
    )
    sys.exit(2)

# Set random seed
random.seed(args.random_seed)

with open(args.mapping_file) as inptr:
    mapping = json.loads(inptr.read())

with open(persons_file) as inptr:
    all_persons = [clean_element(p) for p in inptr.readlines()]
    all_persons = set([p for p in all_persons if check_person_name(p)])

with open(geolocations_file) as inptr:
    all_geolocations = set([clean_element(g) for g in inptr.readlines()])

for pred in args.predicates:
    print(f"Processing {pred}")
    cur_process_map = mapping[f"<subject> {pred} <object>"]
    checks = cur_process_map["checks"]
    question = cur_process_map["question_template"]
    answer = cur_process_map["answer_template"]
    pred = pred.replace("http://dbpedia.org/ontology/", "")
    pred_specific_infile = os.path.join(
        predicate_wise_input_dir, pred.replace("http://dbpedia.org/ontology/", "")
    )
    pred_specific_outfile = os.path.join(
        output_dir, pred.replace("http://dbpedia.org/ontology/", "")
    )
    subject_to_object = defaultdict(lambda: [])
    object_to_subject = defaultdict(lambda: [])
    pred_related_data = []
    with open(pred_specific_infile) as inptr:
        for line in inptr.readlines():
            line = line.strip()
            rdf_elements = line.split()
            if not rdf_elements[1].endswith(pred + ">"):
                continue
            sub = clean_element(rdf_elements[0])
            obj = clean_element(rdf_elements[2])
            subject_to_object[sub].append(obj)
            object_to_subject[obj].append(sub)
            pred_related_data.append([sub, obj])

    all_subjects = set(subject_to_object.keys())
    all_objects = set(object_to_subject.keys())
    num_pred_related_data = len(pred_related_data)
    shuffled_indices = random.sample(
        range(num_pred_related_data), k=num_pred_related_data
    )
    counter = 0
    lines_to_write = []
    print(f"Loaded data for {pred}, creating new questions now..")
    for ind in shuffled_indices:
        cur_sub, cur_obj = pred_related_data[ind]
        if "," in cur_obj:
            continue
        if len(checks) == 0:
            flag = True
        else:
            c = checks[0]
            if c.endswith("persondata_en.ttl"):
                if c.startswith("<subject>"):
                    flag = cur_sub in all_persons
                    all_subjects = all_subjects.intersection(all_persons)
                elif c.startswith("<object>"):
                    flag = cur_obj in all_persons
                    all_objects = all_objects.intersection(all_persons)
            elif c.endswith("geo-coordinates-mappingbased_en.ttl"):
                if c.startswith("<subject>"):
                    flag = cur_sub in all_geolocations
                    all_subjects = all_subjects.intersection(all_geolocations)
                elif c.startswith("<object>"):
                    flag = cur_obj in all_geolocations
                    all_objects = all_objects.intersection(all_geolocations)

        if flag:  # save to disk
            # get new entities
            cur_question = deepcopy(question)
            cur_question = cur_question.replace("<subject>", cur_sub.replace("_", " "))
            cur_question = cur_question.replace("<object>", cur_obj.replace("_", " "))

            # Create valid question
            valid_question = cur_question
            valid_question = valid_question.replace(
                "<new_subject>", cur_sub.replace("_", " ")
            )
            valid_question = valid_question.replace(
                "<new_object>", cur_obj.replace("_", " ")
            )

            # Create invalid question
            invalid_question = cur_question
            answer_to_invalid_question = deepcopy(answer)
            answer_to_invalid_question = answer_to_invalid_question.replace(
                "<subject>", cur_sub.replace("_", " ")
            )
            answer_to_invalid_question = answer_to_invalid_question.replace(
                "<object>", cur_obj.replace("_", " ")
            )
            new_subject, new_object = "", ""
            if "<new_subject>" in invalid_question:
                subject_choices = list(all_subjects - set(object_to_subject[cur_obj]))
                random.shuffle(subject_choices)
                for sampled_subject in subject_choices:
                    if (
                        cur_sub != sampled_subject
                        and cur_obj not in subject_to_object[sampled_subject]
                    ):
                        new_subject = sampled_subject
                        break
                if new_subject == "":
                    # No viable alternative found, skip this row
                    continue
                else:
                    invalid_question = invalid_question.replace(
                        "<new_subject>", new_subject
                    )
                    answer_to_invalid_question = answer_to_invalid_question.replace(
                        "<new_subject>", new_subject
                    )
                    valid_entities_list = subject_to_object[new_subject]
                del subject_choices, sampled_subject
            if "<new_object>" in invalid_question:
                object_choices = list(all_objects - set(subject_to_object[cur_sub]))
                random.shuffle(object_choices)
                for sampled_object in object_choices:
                    if (
                        cur_obj != sampled_object
                        and cur_sub not in object_to_subject[sampled_object]
                    ):
                        new_object = sampled_object
                        break
                if new_object == "":
                    # No viable alternative found, skip this row
                    continue
                else:
                    invalid_question = invalid_question.replace(
                        "<new_object>", new_object
                    )
                    answer_to_invalid_question = answer_to_invalid_question.replace(
                        "<new_object>", new_object
                    )
                    valid_entities_list = object_to_subject[new_object]
                del object_choices, sampled_object

            # write new sample to file
            new_prompt = deepcopy(template)
            new_prompt["valid_question"] = valid_question
            new_prompt["invalid_question"] = invalid_question
            new_prompt["answer_to_invalid_question"] = answer_to_invalid_question
            new_prompt["valid_entities_list"] = ",".join(valid_entities_list)
            new_prompt["new_subject"] = new_subject
            new_prompt["new_object"] = new_object
            new_prompt["old_subject"] = cur_sub
            new_prompt["old_object"] = cur_obj
            lines_to_write.append(json.dumps(new_prompt, ensure_ascii=False))
            if counter % 1000 == 0:
                print(f"Created question number: {counter}")
            counter += 1
            if counter >= args.num_questions_to_generate:
                break

    with open(pred_specific_outfile, "w") as outptr:
        outptr.write("\n".join(lines_to_write))
    print(f"Done writing {pred_specific_outfile} with {counter} samples")
