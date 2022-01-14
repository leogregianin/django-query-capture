from unittest.mock import MagicMock

from django.test import TestCase

from django_query_capture import CapturedQueryClassifier


def create_dict_mock(*args, **kwargs):
    mock = MagicMock(*args, **kwargs)
    mock.__getitem__.side_effect = lambda x: getattr(mock, x)
    return mock


class CapturedQueryClassifierTests(TestCase):
    def test_read_count_when_raw_sql_startswith_select(self):
        captured_queries = [
            create_dict_mock(raw_sql="SELECT *"),
            create_dict_mock(raw_sql="INSERT *"),
            create_dict_mock(raw_sql="UPDATE *"),
            create_dict_mock(raw_sql="DELETE *"),
        ]
        result = CapturedQueryClassifier(captured_queries)()
        self.assertEqual(result["read"], 1)

    def test_writes_count_when_not_raw_sql_startswith_select(self):
        captured_queries = [
            create_dict_mock(raw_sql="SELECT *"),
            create_dict_mock(raw_sql="INSERT *"),
            create_dict_mock(raw_sql="UPDATE *"),
            create_dict_mock(raw_sql="DELETE *"),
        ]
        result = CapturedQueryClassifier(captured_queries)()
        self.assertEqual(result["writes"], 3)

    def test_total_count(self):
        captured_queries = [
            create_dict_mock(raw_sql="SELECT *"),
            create_dict_mock(raw_sql="INSERT *"),
            create_dict_mock(raw_sql="UPDATE *"),
            create_dict_mock(raw_sql="DELETE *"),
        ]
        result = CapturedQueryClassifier(captured_queries)()
        self.assertEqual(result["total"], 4)

    def test_total_duration(self):
        captured_queries = [
            create_dict_mock(duration=10.5),
            create_dict_mock(duration=20.5),
            create_dict_mock(duration=30.5),
            create_dict_mock(duration=40.5),
        ]
        result = CapturedQueryClassifier(captured_queries)()
        self.assertEqual(result["total_duration"], 102.0)

    def test_most_common_duplicates(self):
        captured_queries = [
            create_dict_mock(sql="SELECT *"),
            create_dict_mock(sql="INSERT *"),
            create_dict_mock(sql="SELECT *"),
            create_dict_mock(sql="SELECT *"),
        ]
        result = CapturedQueryClassifier(captured_queries)()
        self.assertEqual(result["most_common_duplicates"], 3)

    def test_most_common_similar(self):
        captured_queries = [
            create_dict_mock(raw_sql="INSERT (%s %s %s %s)", raw_params=(1, 2, 3, 4)),
            create_dict_mock(raw_sql="INSERT *"),
            create_dict_mock(raw_sql="INSERT (%s %s %s %s)", raw_params=(5, 6, 7, 8)),
            create_dict_mock(
                raw_sql="INSERT (%s %s %s %s)", raw_params=(9, 0, "-", "=")
            ),
        ]
        result = CapturedQueryClassifier(captured_queries)()
        self.assertEqual(result["most_common_similar"], 3)
