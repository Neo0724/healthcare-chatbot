import json
import pandas as pd

# 1. Load the JSON data
# with open('./.deepeval/.temp_test_run_data.json', 'r', encoding='utf-8') as file:
with open('./results/faithfulness_2.json', 'r', encoding='utf-8') as file:
    json_data = json.load(file)

test_cases = json_data["testCases"]

metric_data = {}

for tc in test_cases:
    for metric in tc["metricsData"]:
        metric_name = metric["name"]
        metric_score = metric["score"]
        if metric_name not in metric_data:
            metric_data[metric_name] = metric_score
        else:
            metric_data[metric_name] += metric_score

metric_avg = {}

for k, v in metric_data.items():
    metric_avg[k] = v / len(test_cases)

print(f"Total: {len(test_cases)}")

print(metric_avg)
