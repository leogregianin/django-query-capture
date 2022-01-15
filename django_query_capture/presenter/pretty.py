import re

from django.utils import termcolors
from tabulate import tabulate

from django_query_capture import BasePresenter
from django_query_capture.classify import ClassifiedQuery
from django_query_capture.printer import (
    DuplicateMinCountPrinter,
    SimilarMinCountPrinter,
    SlowMinTimePrinter,
)
from django_query_capture.utils import colorize, get_value_from_django_settings


class PrettyPresenter(BasePresenter):
    @staticmethod
    def is_printable_type(value):
        return isinstance(value, (str, int, float))

    @staticmethod
    def format_print_value(value):
        return f"{value:.2f}" if isinstance(value, float) else value

    @classmethod
    def get_is_warning(cls, classified_query: ClassifiedQuery):
        for captured_query, count in classified_query["duplicates_counter"].items():
            if cls.is_allow_pattern(captured_query["sql"]):
                if (
                    count
                    > get_value_from_django_settings("PRINT_THRESHOLDS")[
                        "DUPLICATE_MIN_COUNT"
                    ]
                ):
                    return True

        for captured_query, count in classified_query["similar_counter"].items():
            if cls.is_allow_pattern(captured_query["sql"]):
                if (
                    count
                    > get_value_from_django_settings("PRINT_THRESHOLDS")[
                        "SIMILAR_MIN_COUNT"
                    ]
                ):
                    return True

        for captured_query in classified_query["captured_queries"]:
            if cls.is_allow_pattern(captured_query["sql"]):
                if (
                    captured_query["duration"]
                    > get_value_from_django_settings("PRINT_THRESHOLDS")[
                        "SLOW_MIN_TIME"
                    ]
                ):
                    return True

    @classmethod
    def get_stats_table(
        cls, classified_query: ClassifiedQuery, is_warning: bool = False
    ):
        return colorize(
            tabulate(
                [
                    [
                        cls.format_print_value(value)
                        for value in classified_query.values()
                        if cls.is_printable_type(value)
                    ]
                ],
                [key for key in classified_query.keys()],
                tablefmt=get_value_from_django_settings("PRETTY")["TABLE_FORMAT"],
            ),
            is_warning,
        )

    @classmethod
    def print(cls, classified_query: ClassifiedQuery):
        is_warning = cls.get_is_warning(classified_query)
        print("\n" + cls.get_stats_table(classified_query, is_warning=is_warning))

        for captured_query in classified_query["captured_queries"]:
            SlowMinTimePrinter.print(captured_query, is_warning=is_warning)

        for captured_query, count in classified_query["duplicates_counter"].items():
            DuplicateMinCountPrinter.print(
                captured_query, count=count, is_warning=is_warning
            )

        for captured_query, count in classified_query["similar_counter"].items():
            SimilarMinCountPrinter.print(
                captured_query, count=count, is_warning=is_warning
            )
