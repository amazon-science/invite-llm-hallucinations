#!/usr/bin/env python

"""
This script combines the output from 2_create_invalid_questions_dbpedia.py
and 3_create_invalid_dates.py
"""

import os
import sys
import json
import glob
import random
import argparse


def sample_per_category(data_list, cat, num_test, num_val):
    num_total = num_test + num_val
    selected = []
    selected_qs = []
    for d in data_list:
        # Sample unique questions, relevant for dates category
        if d["category"] == cat and d["valid_question"] not in selected_qs:
            selected.append(d)
        if len(selected) == num_total:
            break
    test_split = selected[:num_test]
    val_split = selected[num_test:]
    return test_split, val_split


parser = argparse.ArgumentParser(description="Create questions with invalid dates")
parser.add_argument(
    "--data_dir",
    help="File path to <data_dir> from step 0",
    required=True,
)
parser.add_argument(
    "--output_dir",
    help="File path to directory where all test questions will be written",
    required=True,
)
parser.add_argument("--random_seed", default=1000, help="Random seed value")
parser.add_argument(
    "--date_template_str",
    default="I'm sorry, that's an invalid date.",
    help="Error message for bad date questions",
)
parser.add_argument(
    "--year_template_str",
    default="That date is in the future, I can't answer that.",
    help="Error message for future year questions",
)
parser.add_argument(
    "--num_args.num_date_samples",
    default=5000,
    type=int,
    help="Number of questions with invalid dates",
)
parser.add_argument(
    "--num_dbpediapredicate_samples",
    default=105000,
    type=int,
    help="Number of questions to create from DBPedia over all predicates types",
)
parser.add_argument(
    "--num_date_samples",
    default=5000,
    type=int,
    help="Number of questions to create from DBPedia over all predicates types",
)
parser.add_argument(
    "--num_test_per_category",
    default=50,
    type=int,
    help="Number of questions to create per category in test set",
)
parser.add_argument(
    "--num_val_per_category",
    default=5,
    type=int,
    help="Number of questions to create per category in validation set",
)
parser.add_argument(
    "--create_test_and_validation_splits",
    action="store_true",
    default=False,
    help="Create test and validation splits",
)
args = parser.parse_args()

dbpedia_questions_path = os.path.join(
    args.data_dir, "dbpedia", "predicate_wise_questions"
)
if not os.path.exists(dbpedia_questions_path):
    print(
        "Error: missing invalid questions directory from dbpedia, please run 2_create_invalid_questions_dbpedia.py first"
    )
    sys.exit(2)

date_questions_path = os.path.join(
    args.data_dir, "triviaqa", "generated_questions", "invalid_dates_questions.json"
)
if not os.path.exists(date_questions_path):
    print(
        "Error: missing invalid date questions in triviaqa, please run 3_create_invalid_dates.py first"
    )
    sys.exit(2)

if not os.path.exists(args.output_dir):
    os.mkdir(args.output_dir)

# Set random seed
random.seed(args.random_seed)

categories = []
non_date_data = []
for f in glob.glob(dbpedia_questions_path + "/*"):
    if f.endswith("invalid_dates_and_years"):
        continue
    with open(f) as inptr:
        cur_data = [json.loads(line.strip()) for line in inptr.readlines()]
        for ind, d in enumerate(cur_data):
            d["category"] = os.path.basename(f)
            d["id"] = d["category"] + "_" + str(ind)
            if d["category"] not in categories:
                categories.append(d["category"])
    non_date_data.extend(cur_data)
non_date_data = random.sample(non_date_data, k=args.num_dbpediapredicate_samples)

date_data = []
with open(date_questions_path) as inptr:
    cur_data = [json.loads(line.strip()) for line in inptr.readlines()]
    for ind, d in enumerate(cur_data):
        if d["answer_to_invalid_question"] == args.date_template_str:
            d["category"] = "invalidDate"
        elif d["answer_to_invalid_question"] == args.year_template_str:
            d["category"] = "futureDate"
        d["id"] = "invalidDates_" + str(ind)
    date_data.extend(cur_data)
categories.extend(["invalidDate", "futureDate"])

date_data = random.sample(date_data, k=args.num_date_samples)

all_data = non_date_data + date_data
random.shuffle(all_data)

outfile = os.path.join(args.output_dir, "all_data.json")
with open(outfile, "w") as outptr:
    outptr.write("\n".join([json.dumps(d, ensure_ascii=False) for d in all_data]))
print(f"Dataset written to {outfile}")

if args.create_test_and_validation_splits:
    test_set, validation_set = [], []
    for cat in categories:
        cur_test, cur_val = sample_per_category(
            all_data, cat, args.num_test_per_category, args.num_val_per_category
        )
        test_set.extend(cur_test)
        validation_set.extend(cur_val)

    random.shuffle(test_set)

    # Write to file
    with open(os.path.join(args.output_dir, "testset.json"), "w") as outptr:
        outptr.write("\n".join([json.dumps(d, ensure_ascii=False) for d in test_set]))

    random.shuffle(validation_set)
    with open(os.path.join(args.output_dir, "validationset.json"), "w") as outptr:
        outptr.write(
            "\n".join([json.dumps(d, ensure_ascii=False) for d in validation_set])
        )

    print(f"Test and validation splits written to {args.output_dir}")
