from unittest.mock import MagicMock

from app.graph_queries.queries import get_diseases_information


def test_get_diseases_information(mocker):
    mock_neo4j_driver = MagicMock()

    mocked_query_result = [
        {
            "disease_name": "diabetes",
            "score": 0.8,
            "definition_node": ["a", "b", "c"],
            "symptom_node": ["a", "b", "c"],
            "treatment_node": ["a", "b", "c"],
        }
    ]

    mock_neo4j_driver.execute_query.return_value = (mocked_query_result, None, None)

    records = get_diseases_information(mock_neo4j_driver, ["disease"], [1.0])

    assert len(records) == 1
    assert records[0]["disease_name"] == "diabetes"
