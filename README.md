## INVITE: a Testbed of Automatically Generated Invalid Questions to Evaluate Large Language Models for Hallucinations

This repository contains code for the `INVITE` framework, presented in [Ramakrishna et al., EMNLP 2023](https://assets.amazon.science/3f/73/dd51d8824cc0b9b6d3cf3a263908/invite-a-testbed-of-automatically-generated-invalid-questions-to-evaluate-large-language-models-for-hallucinations.pdf). 

The `INVITE` framework generates a fresh batch of questions containing invalid assumptions in each instantiation, to evaluate Large Language Models (LLMs) for their tendancy to hallucinate. Questions generated using `INVITE` induce high rates of hallucinations based on our experiments:

| _LLM_ | _Hallucination Rate_ | 
|---|---|
| GPTNeo-2.7B | 83% | 
| GPTJ-6B | 82% |
| Open-LLaMA-7B | 88% |
| RedPajama-7B | 81% | 
| GPT3.5-Turbo | 17% |
| GPT4 | 6% |

In addition the the released code, this repository also includes the complete question templates generated using crowdsourcing, a further cleaned high quality subset of question templates with answers, and evaluation files for above models. 

For questions and suggestions about this project, please reach out to aniramak@amazon.com/anil.k.ramakrishna@gmail.com.

## Runbook

To generate new questions using INVITE, invoke following commands in order. 

#### Step 0: `bash 0_download_data.sh <data_dir>`
Fetch and prepare relevant files in the provided <data_dir> path. We download the [DBPedia Knowledge Base](databus.dbpedia.org/dbpedia/collections/latest-core) and [the TriviaQA dataset](https://nlp.cs.washington.edu/triviaqa/data/triviaqa-rc.tar.gz).

#### Step 1: `bash 1_extract_predicate_specific_records.sh <data_dir> Data/selected_predicates_list.txt`

Create intermediate representation files for each selected predicate type for downstream use. We provide a few candidate predicates in `Data/selected_predicates_list.txt`, you can edit this file to add/remove predicates. If you chose to add more predicates, please be sure to also create suitable mappings for template questions and answers in the file `Data/cleaned_question_templates_with_answers.json`.

#### Step 2: `bash 2a_create_data_in_parallel.sh <data_dir> Data/selected_predicates_list.txt Data/cleaned_question_templates_with_answers.json`

Generate the invalid questions using DBPedia. To reduce time, this script parallelizes question generation for each selected predicate type.

#### Step 3: `python 3_create_invalid_dates.py --data_dir <data_dir>`

Create questions containing invalid dates from TriviaQA.

#### Step 4 (Optional): `python 4_combine_data_into_final_file.py --data_dir <data_dir> --output_dir <output_dir>`

Aggregate all the generated questions.

## Citing

If you use the code in this repository, please cite

```
@Inproceedings{Ramakrishna2023,
 author = {Anil Ramakrishna and Rahul Gupta and Jens Lehmann and Morteza Ziyadi},
 title = {INVITE: A testbed of automatically generated invalid questions to evaluate large language models for hallucinations},
 year = {2023},
 url = {https://www.amazon.science/publications/invite-a-testbed-of-automatically-generated-invalid-questions-to-evaluate-large-language-models-for-hallucinations},
 booktitle = {EMNLP 2023},
}
```

## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License Summary

This repository is made available under the CC-BY-NC license. See the LICENSE file for more details.
