from collections import defaultdict
from contextlib import suppress
from dataclasses import dataclass
from functools import wraps
from typing import List, Optional, Tuple

import pandas as pd
from pymilvus import Collection, CollectionSchema, DataType, FieldSchema, MilvusException, connections
from retry import retry
from sentence_transformers import SentenceTransformer


@dataclass
class MilvusConnectionSecrets:
    user: str
    password: str
    alias: Optional[str] = "default"
    host: Optional[str] = "localhost"
    port: Optional[str] = "19530"


@dataclass
class QueryResult:
    question_id: int
    score: float


def preload_collection(func):
    @wraps(func)
    def wrapper(self: "MilvusService", *args, **kwargs):
        self.collection.load()
        return func(self, *args, **kwargs)

    return wrapper


class MilvusService:
    index_params = {"metric_type": "COSINE", "index_type": "FLAT"}
    search_params = {
        "metric_type": "COSINE",
        "offset": 0,
        "ignore_growing": False,
    }
    collection_name = "questions"
    index_name = "questions_embedding"

    def __init__(
        self,
        credentials: MilvusConnectionSecrets,
        df: Optional[pd.DataFrame] = None,
        verbose: bool = False,
        reset: bool = False,
    ):
        self.embedding_model = SentenceTransformer("all-mpnet-base-v2")
        self.connect(credentials)
        self.collection: Collection = self.create_or_get_collection(reset)
        if df is not None:
            self.insert(df)
        self.create_index()
        self.verbose = verbose

    @retry(MilvusException, tries=10, delay=30, logger=None)
    def connect(self, credentials: MilvusConnectionSecrets):
        connections.connect(**credentials.__dict__)

    def create_or_get_collection(self, reset: bool) -> Collection:
        with suppress(Exception):
            collection = Collection(self.collection_name)
            if reset:
                collection.drop()
            else:
                return collection
        question_id = FieldSchema(
            name="id",
            dtype=DataType.INT64,
            is_primary=True,
        )
        text_embedding = FieldSchema(name=self.index_name, dtype=DataType.FLOAT_VECTOR, dim=768)
        schema = CollectionSchema(
            fields=[question_id, text_embedding], description="Question search", enable_dynamic_field=True
        )

        return Collection(name=self.collection_name, schema=schema, using="default", shards_num=2)

    def create_index(self):
        self.collection.create_index(field_name=self.index_name, index_params=self.index_params)

    def insert(self, df: pd.DataFrame):
        df[self.index_name] = self.embedding_model.encode(df["text"].tolist()).tolist()
        df = df[["id", self.index_name]]
        self.collection.insert(df)

    @preload_collection
    def search(self, query: str, k: Optional[int] = 10, threshold: float = float("inf")) -> List[QueryResult]:
        # if k > len(self):
        #     raise ValueError(f"Your index has size {len(self)} but you set n_results to {k}.")

        vector = self.embedding_model.encode([query])
        query_results = self.collection.search(
            data=vector, anns_field=self.index_name, param=self.search_params, limit=k, expr=None
        )
        results = []
        for result in query_results[0]:
            item = QueryResult(question_id=result.id, score=result.distance)
            if item.score > threshold:
                continue
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
        results = self.search(query, k=k, threshold=threshold)

        relevant_answers = self.nearest_neighbors(results)
        top_answers = relevant_answers[:return_count]
        return top_answers

    def __sizeof__(self) -> int:
        return self.collection.num_entities

    def __len__(self) -> int:
        return self.__sizeof__()
