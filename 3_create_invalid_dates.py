#!/usr/bin/env python
"""
This script creates new questions with invalid dates from
TriviaQA by distorting valid dates in existing questions.
"""

import os
import re
import sys
import json
import random
import argparse
from copy import deepcopy


def distort_question(original, qid, dataset, counter):
    new_qs = []
    match1 = date_and_month_re.search(original)
    match2 = month_and_date_re.search(original)
    match3 = month_only_re.search(original)
    match4 = numeric_date_re.search(original)
    match5 = year_only_re.search(original)
    if match1 or match2 or match3:
        if match1:
            matched_string = match1.group(0)
            span = match1.span()
            date, month = matched_string.split()
        elif match2:
            matched_string = match2.group(0)
            span = match2.span()
            month, date = matched_string.split()
        elif match3:
            # Skip month only matches to avoid cases like 3rd of June, "red october", etc.
            return None, counter

        if month.lower() == "february":
            # Check if year is available
            if match1:
                full_match = expanded_year_dm_re.search(original)
            elif match2:
                full_match = expanded_year_md_re.search(original)
            else:
                full_match = False

            if full_match:
                year = int(full_match.group(0).split()[2])
                if year % 4 != 0:
                    distorted_dates = list(
                        range(29, 99)
                    )  # If we know it's not leap year, use 29
                else:
                    distorted_dates = list(
                        range(30, 99)
                    )  # If we know it's leap year, use 30
            else:
                distorted_dates = list(range(30, 99))  # If we're not sure, use 30
        else:
            distorted_dates = list(range(month_wise_num_dates[month.lower()] + 1, 99))

        for i in range(args.num_variations):
            new_qid = f"{qid}_{i}"
            new_date = str(random.sample(distorted_dates, 1)[0])
            if new_date[-1] == "1":
                new_date += "st"
            elif new_date[-1] == "2":
                new_date += "nd"
            elif new_date[-1] == "3":
                new_date += "rd"
            else:
                new_date += "th"

            if random.random() > 0.5:
                new_string = f"{new_date} {month}"
            else:
                new_string = f"{month} {new_date}"

            # If the date preceded with a the, remove it
            preceding_str = original[: span[0]].split()
            if len(preceding_str) > 1 and preceding_str[-1].strip().lower() == "the":
                new_question = original.replace("the " + matched_string, new_string)
            else:
                new_question = original.replace(matched_string, new_string)
            new_qs.append(f"{original}\t{new_question}\t{args.date_template_str}")

        counter += 1
    elif match4:
        matched_string = match4.group(0)
        month, date, year = [int(x) for x in matched_string.split("/")]
        if month > 12:
            date, month = month, date

        if month == 2:
            if year % 4 != 0:
                distorted_dates = list(
                    range(29, 99)
                )  # If we know it's not leap year, use 29
            else:
                distorted_dates = list(
                    range(30, 99)
                )  # If we know it's leap year, use 30
        else:
            distorted_dates = list(
                range(list(month_wise_num_dates.values())[month - 1] + 1, 99)
            )

        for i in range(args.num_variations):
            new_qid = f"{qid}_{i}"
            new_date = str(random.sample(distorted_dates, 1)[0])
            if new_date[-1] == "1":
                new_date += "st"
            elif new_date[-1] == "2":
                new_date += "nd"
            elif new_date[-1] == "3":
                new_date += "rd"
            else:
                new_date += "th"

            new_string = f"{new_date}/{month}/{year}"
            new_question = original.replace(matched_string, new_string)
            new_qs.append(f"{original}\t{new_question}\t{args.date_template_str}")

        counter += 1
    elif match5:
        year = match5.group(0)
        distorted_years = list(range(2025, 2100))

        for i in range(args.num_variations):
            new_qid = f"{qid}_{i}"
            new_year = str(random.sample(distorted_years, 1)[0])
            new_question = original.replace(year, new_year)
            new_qs.append(f"{original}\t{new_question}\t{args.year_template_str}")

    else:
        return None, counter

    return new_qs, counter


def select_rows(data_list, num_to_select, answer_to_select):
    rows_with_this_answer = [x for x in data_list if answer_to_select in x]
    if len(rows_with_this_answer) < num_to_select:
        num_to_select = len(rows_with_this_answer)
    return random.sample(rows_with_this_answer, num_to_select)


def apply_template(row):
    tmp_l = row.split("\t")
    assert len(tmp_l) == 3
    new_question = deepcopy(template)
    new_question["valid_question"] = tmp_l[0]
    new_question["invalid_question"] = tmp_l[1]
    new_question["answer_to_invalid_question"] = tmp_l[2]
    return json.dumps(new_question, ensure_ascii=False)


# Regular expressions to match dates and years
expanded_year_dm_re = re.compile(
    r"\b[0-9]{1,2}(st|nd|rd|th)?\b[\s]+\b(?:january|february|march|april|may|june|july|august|september|october|november|december)\b[\s]+\b(?:1[0-9][0-9][0-9]|20[0-9][0-9])\b",
    re.IGNORECASE,
)
expanded_year_md_re = re.compile(
    r"\b(?:january|february|march|april|may|june|july|august|september|october|november|december)\b[\s]+\b[0-9]{1,2}(st|nd|rd|th)?\b[\s]+\b(?:1[0-9][0-9][0-9]|20[0-9][0-9])\b",
    re.IGNORECASE,
)
date_and_month_re = re.compile(
    r"\b[0-9]{1,2}(st|nd|rd|th)?\b[\s]+\b(?:january|february|march|april|may|june|july|august|september|october|november|december)\b",
    re.IGNORECASE,
)
month_and_date_re = re.compile(
    r"\b(?:january|february|march|april|may|june|july|august|september|october|november|december)\b[\s]+\b[0-9]{1,2}(st|nd|rd|th)?\b",
    re.IGNORECASE,
)
numeric_date_re = re.compile(r"\b[0-9]{1,2}/[0-9]{1,2}/[0-9]{4}\b", re.IGNORECASE)
# Matching for month only had some false positives ("...may have been...", "began the march...") so skipping these months
month_only_re = re.compile(
    r"\b(?:january|february|april|june|july|august|september|october|november|december)\b",
    re.IGNORECASE,
)
year_only_re = re.compile(r"\b1[0-9][0-9][0-9]|20[0-9][0-9]\b", re.IGNORECASE)

month_wise_num_dates = {
    "january": 31,
    "february": 28,
    "march": 31,
    "april": 30,
    "may": 31,
    "june": 30,
    "july": 31,
    "august": 31,
    "september": 30,
    "october": 31,
    "november": 30,
    "december": 31,
}

template = {
    "valid_question": "",
    "invalid_question": "",
    "answer_to_invalid_question": "",
}

parser = argparse.ArgumentParser(description="Create questions with invalid dates")
parser.add_argument(
    "--data_dir",
    help="File path to <data_dir> from step 0",
    required=True,
)
parser.add_argument("--random_seed", default=1000, type=int, help="Random seed value")
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
    "--num_variations", default=10, type=int, help="Number of distortions per question"
)
parser.add_argument(
    "--max_selection",
    default=10000,
    type=int,
    help="Maximum number of rows for each <dataset and type> combination to include in selected files",
)
args = parser.parse_args()

triviaqa_input_path = os.path.join(args.data_dir, "triviaqa")
if not os.path.exists(triviaqa_input_path):
    print(
        f"Error: TriviaQA directory not found in {args.data_dir}, please run 0_download_data.sh first."
    )
    sys.exit(2)
triviaqa_data_files = [
    os.path.join(triviaqa_input_path, "qa", "wikipedia-test-without-answers.json"),
    os.path.join(triviaqa_input_path, "qa", "web-test-without-answers.json"),
]

for fname in triviaqa_data_files:
    if not os.path.exists(fname):
        print(
            f"Error: File {fname} not found in {triviaqa_input_path}, please rerun 0_download_data.sh and ensure there are no errors."
        )
        sys.exit(2)

output_dir = os.path.join(triviaqa_input_path, "generated_questions")
if not os.path.exists(output_dir):
    os.mkdir(output_dir)
output_file = os.path.join(output_dir, "invalid_dates_questions.json")

# Set random seed
random.seed(args.random_seed)

counter = 0
# Extract data from TriviaQA
trivial_qa_test_all = []
visited_so_far = []
for f in triviaqa_data_files:
    with open(f) as inptr:
        jdict = json.loads(inptr.read())

    for data in jdict["Data"]:
        cur_id = data["QuestionId"]
        if cur_id in visited_so_far:
            continue
        else:
            visited_so_far.append(cur_id)
        cur_question = data["Question"]

        new_qs, counter = distort_question(cur_question, cur_id, "TriviaQA", counter)
        if new_qs is not None:
            trivial_qa_test_all.extend(new_qs)

selected_invalid_dates = select_rows(
    trivial_qa_test_all, args.max_selection, args.date_template_str
)
random.shuffle(selected_invalid_dates)
selected_invalid_years = select_rows(
    trivial_qa_test_all, args.max_selection, args.year_template_str
)
random.shuffle(selected_invalid_years)
# Select max 5k rows of this type
trivial_qa_test_selected = (
    selected_invalid_dates
    + selected_invalid_years[: 5000 - len(selected_invalid_dates)]
)

# Write extracted questions to file
with open(output_file, "w") as outptr:
    data_rows = trivial_qa_test_selected
    outptr.write("\n".join([apply_template(row) for row in data_rows]))
print(f"Created new test set at {output_file}")
