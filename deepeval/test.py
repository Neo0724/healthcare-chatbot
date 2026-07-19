import json
import pandas as pd

# 1. Load the JSON data
with open('./.deepeval/.temp_test_run_data.json', 'r', encoding='utf-8') as file:
    json_data = json.load(file)

test_cases = json_data["testCases"]

total = sum([tc["metricsData"][0]["score"] for tc in test_cases])

print(total / len(test_cases))
