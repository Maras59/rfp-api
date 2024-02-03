from collections import defaultdict
from typing import List, Optional, Tuple
from pymilvus import Collection, connections
import sentence_transformers
from .model import QueryResult


class MilvusService:
    index_params = {"metric_type": "COSINE", "index_type": "FLAT"}
    search_params = {
        "metric_type": "COSINE",
        "offset": 0,
        "ignore_growing": False,
    }

    def __init__(self):
        self.connection = connections.connect(
            alias="default", user="username", password="password", host="localhost", port="19530"
        )
        self.collection: Collection = None
        self.embedded_field_name: str = None
        self.embedding_model = sentence_transformers("all-MiniLM-L6-v2")

    def query(self, query: str, k: Optional[int] = 10, threshold: float = float("inf")) -> List[QueryResult]:
        if k > self.collection.count():
            raise ValueError(f"Your index has size {self.collection.count} but you set n_results to {k}.")

        embedding = self.embedding_model.encode([query])
        query_results = self.collection.search(
            data=embedding, anns_field=self.embedded_field_name, param=self.search_params, limit=k
        )
        results = []
        for result in query_results:
            item = QueryResult(question_id=result.id, score=result.distance)
            if item.score > threshold:
                break
            results.append(item)

        if self.verbose:
            self.print_results(results)

        return results

    def nearest_neighbors(self, results: List[QueryResult]) -> List[Tuple[int, float]]:
        classes = defaultdict(int)
        for item in results:
            question = self.db.get_question_by_id(item.question_id)
            score = 1 - item.score
            classes[question.answer_id] += score

        if self.verbose:
            print(dict(classes))

        # create list of tuples (score, class) and sort it
        sorted_classes = sorted(classes.items(), key=lambda x: x[1], reverse=True)
        return sorted_classes

    def inference(
        self, query: str, k: Optional[int] = 10, return_count: Optional[int] = 1, threshold: float = float("inf")
    ) -> List[Tuple[int, float]]:
        results = self.query(query, k=k, threshold=threshold)

        relevant_answers = self.nearest_neighbors(results)
        top_answers = relevant_answers[:return_count]
        return top_answers

    def __sizeof__(self) -> int:
        return self.collection.count()
