from dataclasses import dataclass


@dataclass
class QueryResult:
    question_id: int
    score: float
