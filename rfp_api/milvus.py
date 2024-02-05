{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "from pymilvus import connections\n",
    "\n",
    "connections.connect(alias=\"default\", user=\"username\", password=\"password\", host=\"localhost\", port=\"19530\")"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "from libraries.db import DatabaseProxy\n",
    "\n",
    "db = DatabaseProxy()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "import pandas as pd\n",
    "df_questions = pd.DataFrame([x.dict() for x in db.get_questions()])"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "df_questions.head()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "from pymilvus import CollectionSchema, FieldSchema, DataType\n",
    "\n",
    "question_id = FieldSchema(\n",
    "    name=\"id\",\n",
    "    dtype=DataType.INT64,\n",
    "    is_primary=True,\n",
    ")\n",
    "is_active = FieldSchema(\n",
    "    name=\"is_active\",\n",
    "    dtype=DataType.BOOL,\n",
    "    default_value=True,\n",
    ")\n",
    "text = FieldSchema(\n",
    "    name=\"text\",\n",
    "    dtype=DataType.VARCHAR,\n",
    "    max_length=200,\n",
    ")\n",
    "answer_id = FieldSchema(\n",
    "    name=\"answer_id\",\n",
    "    dtype=DataType.INT64,\n",
    ")\n",
    "text_embedding = FieldSchema(name=\"text_embedding\", dtype=DataType.FLOAT_VECTOR, dim=768)\n",
    "schema = CollectionSchema(\n",
    "    # fields=[question_id, is_active, text, text_embedding], description=\"Question search\", enable_dynamic_field=True\n",
    "    fields=[question_id, text_embedding], description=\"Question search\", enable_dynamic_field=True\n",
    ")\n",
    "collection_name = \"questions\""
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "from pymilvus import Collection\n",
    "\n",
    "collection = Collection(name=collection_name, schema=schema, using=\"default\", shards_num=2)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "from sentence_transformers import SentenceTransformer\n",
    "from tqdm import tqdm\n",
    "\n",
    "model = SentenceTransformer('all-mpnet-base-v2')\n",
    "df_questions['text_embedding'] = df_questions['text'].apply(lambda x: model.encode(x))\n",
    "df = df_questions[['id', 'is_active', 'text', 'text_embedding']]\n",
    "\n",
    "df.head()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "collection_name = \"questions\"\n",
    "\n",
    "def insert_question_to_milvus(df_questions):\n",
    "    question_id = FieldSchema(name=\"id\", dtype=DataType.INT64, is_primary=True)\n",
    "    text_embedding = FieldSchema(name=\"text_embedding\", dtype=DataType.FLOAT_VECTOR, dim=768)\n",
    "    schema = CollectionSchema(fields=[question_id, text_embedding], description=\"Question search\", enable_dynamic_field=True)\n",
    "\n",
    "    try:\n",
    "        collection = Collection(collection_name)\n",
    "    except Exception as e:\n",
    "        collection = Collection(name=collection_name, schema=schema, using=\"default\", shards_num=2)\n",
    "\n",
    "    df_questions['text_embedding'] = df_questions['text'].apply(lambda x: model.encode(x))\n",
    "    df_milvus = df_questions[['id', 'text_embedding']]\n",
    "\n",
    "    mr = collection.insert(df_milvus)\n",
    "\n",
    "    return mr\n",
    "\n",
    "insert_result = insert_question_to_milvus(df_questions)\n",
    "print(\"Milvus Insert Result:\", insert_result)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "from pymilvus import Collection\n",
    "\n",
    "collection = Collection(\"questions\")  # Get an existing collection.\n",
    "mr = collection.insert(df)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "from pymilvus import Collection, utility\n",
    "\n",
    "collection = Collection(\"questions\")\n",
    "index_params = {\"metric_type\": \"COSINE\", \"index_type\": \"FLAT\"}\n",
    "collection.create_index(field_name=\"text_embedding\", index_params=index_params)\n",
    "\n",
    "utility.index_building_progress(\"questions\")"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "from pymilvus import Collection\n",
    "collection = Collection(\"questions\")      # Get an existing collection.\n",
    "collection.load()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "search_params = {\n",
    "    \"metric_type\": \"COSINE\", \n",
    "    \"offset\": 0, \n",
    "    \"ignore_growing\": False,\n",
    "}"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "query = \"What is the onboarding process like?\"\n",
    "vector = model.encode(query)\n",
    "\n",
    "results = collection.search(\n",
    "    data=[vector],\n",
    "    anns_field=\"text_embedding\", \n",
    "    # the sum of `offset` in `param` and `limit` \n",
    "    # should be less than 16384.\n",
    "    param=search_params,\n",
    "    limit=10,\n",
    "    expr=None,\n",
    "    # set the names of the fields you want to \n",
    "    # retrieve from the search result.\n",
    "    output_fields=['text'],\n",
    "    consistency_level=\"Strong\"\n",
    ")\n",
    "\n",
    "for result in results[0]:\n",
    "    # id, similarity, text\n",
    "    print(result.id, result.distance, result.entity.get('text'))\n",
    "    \n",
    "hit = results[0][0]\n",
    "hit.entity.get('text')"
   ]
  }
 ],
 "metadata": {
  "language_info": {
   "name": "python"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 2
}
