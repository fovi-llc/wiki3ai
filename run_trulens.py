# %% [markdown]
# # Llama-Index Quickstart
#
# In this quickstart you will create a simple Llama Index App and learn how to log it and get feedback on an LLM response.
#
# For evaluation, we will leverage the "hallucination triad" of groundedness, context relevance and answer relevance.
#
# [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/truera/trulens/blob/main/trulens_eval/examples/quickstart/llama_index_quickstart.ipynb)

# %%
# %pip install -qU "trulens_eval>=0.19.2" "llama_index>0.9.17" "html2text>=2020.1.16" qdrant_client python-dotenv ipywidgets streamlit_jupyter "litellm>=1.15.1" google-cloud-aiplatform

import os
from trulens_eval import Feedback, TruLlama
from trulens_eval.feedback import Groundedness
from trulens_eval import LiteLLM
import numpy as np
from trulens_eval import Tru
from google.cloud import aiplatform
from llama_index.readers.web import SimpleWebPageReader

from llama_index import VectorStoreIndex, StorageContext, ServiceContext
from llama_index.embeddings import GeminiEmbedding
from llama_index.llms import Gemini
from llama_index.vector_stores import QdrantVectorStore
import qdrant_client
from llama_index import StorageContext


GOOGLE_API_KEY = os.environ["GEMINI_API_KEY"]

# This is used by the LiteLLM for Vertex AI models including Gemini.
# The LiteLLM wrapper for Gemini is used by the TruLens evaluation provider.
aiplatform.init(project="fovi-site", location="us-west1")

tru = Tru(database_redact_keys=True)

# ### Create Simple LLM Application
#
# This example uses LlamaIndex which internally uses an OpenAI LLM.

__documents = SimpleWebPageReader(html_to_text=True).load_data(
    ["http://paulgraham.com/worked.html"]
)

# from llama_index.vector_stores import ChromaVectorStore
# import chromadb

# # initialize client, setting path to save data
# db = chromadb.PersistentClient(path="./chroma_db")

# # create collection
# chroma_collection = db.get_or_create_collection("quickstart")

# # assign chroma as the vector_store to the context
# vector_store = ChromaVectorStore(chroma_collection=chroma_collection)

# Create a local Qdrant vector store
__client = qdrant_client.QdrantClient(path="qdrant_gemini_3")

__vector_store = QdrantVectorStore(client=__client, collection_name="collection")

# Using the embedding model to Gemini
__embed_model = GeminiEmbedding(
    model_name="models/embedding-001", api_key=GOOGLE_API_KEY
)
__service_context = ServiceContext.from_defaults(
    llm=Gemini(api_key=GOOGLE_API_KEY), embed_model=__embed_model
)
__storage_context = StorageContext.from_defaults(vector_store=__vector_store)

__index = VectorStoreIndex.from_documents(
    __documents,
    service_context=__service_context,
    storage_context=__storage_context,
    show_progress=True,
)


def load_llamaindex_app():
    return __index.as_query_engine()


query_engine = load_llamaindex_app()

# response = query_engine.query("What does the author say about their education?")
# print(response)

# response = query_engine.query("Where did the author go to school?")
# print(response)

# response = query_engine.query("Who was the author's Harvard PhD advisor?")
# print(response)

# response = query_engine.query("who was Tom Cheatham to the author?")
# print(response)

# response = query_engine.query("who is Tom? why is he in this story?")
# print(response)

# response = query_engine.query("what is this story about?  what are the most important things the author want the reader to learn?")
# print(response)

# ## Initialize Feedback Function(s)

# import litellm
# litellm.set_verbose=True

# Initialize provider class
gemini_provider = LiteLLM(model_engine="gemini-pro")

grounded = Groundedness(groundedness_provider=gemini_provider)

# Define a groundedness feedback function
f_groundedness = (
    Feedback(grounded.groundedness_measure_with_cot_reasons)
    .on(TruLlama.select_source_nodes().node.text.collect())
    .on_output()
    .aggregate(grounded.grounded_statements_aggregator)
)

# Question/answer relevance between overall question and answer.
f_qa_relevance = Feedback(gemini_provider.relevance).on_input_output()

# Question/statement relevance between question and each context chunk.
f_qs_relevance = (
    Feedback(gemini_provider.qs_relevance)
    .on_input()
    .on(TruLlama.select_source_nodes().node.text)
    .aggregate(np.mean)
)

# ## Instrument app for logging with TruLens

tru_query_engine_recorder = TruLlama(
    query_engine,
    tru=tru,
    app_id="PaulGraham",
    initial_app_loader=load_llamaindex_app,
    feedbacks=[f_groundedness, f_qa_relevance, f_qs_relevance],
)

# # or as context manager
# with tru_query_engine_recorder as recording:
#     response = query_engine.query("Why did the author drop AI?")
#     print(response)

# ## Explore in a Dashboard

tru.run_dashboard()  # open a local streamlit app to explore

# tru.run_dashboard_in_jupyter() # open a streamlit app in the notebook

# tru.stop_dashboard(force=True) # stop if needed

# Alternatively, you can run `trulens-eval` from a command line in the same folder to start the dashboard.

# Note: Feedback functions evaluated in the deferred manner can be seen in the "Progress" page of the TruLens dashboard.

# ## Or view results directly in your notebook

# tru.get_records_and_feedback(app_ids=[])[0] # pass an empty list of app_ids to get all


# def load_llamaindex_app():
#     # from llama_index import VectorStoreIndex
#     index = VectorStoreIndex.from_documents(documents)
#     query_engine = index.as_query_engine()

#     return query_engine

# app2 = load_llamaindex_app()
# # tru_app2 = tru.Llama(
# # Can't specify which Tru instance to use with tru.Llama.
# tru_app2 = TruLlama(
#     app2,
#     tru=tru,
#     app_id="llamaindex_appZZ",
#     initial_app_loader=load_llamaindex_app,
#     feedbacks=[f_groundedness, f_qa_relevance, f_qs_relevance]
# )

# tru.add_app(tru_app2)

# from trulens_eval.appui import AppUI

# aui = AppUI(
#     app=tru_app2,

#     app_selectors=[
#     ],
#     record_selectors=[
#         "app.retriever.retrieve[0].rets[:].score",
#         "app.retriever.retrieve[0].rets[:].node.text",
#     ]
# )
# aui.widget
