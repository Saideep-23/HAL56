from llama_index import VectorStoreIndex, SimpleDirectoryReader, ServiceContext
from llama_index.llms import HuggingFaceLLM
from llama_index.llms.llama_utils import messages_to_prompt, completion_to_prompt
from llama_index.indices.postprocessor import SentenceTransformerRerank
import torch
from llama_index.embeddings import HuggingFaceEmbedding

documents = SimpleDirectoryReader("./sample_data").load_data()

llm = LlamaCPP(
    # optionally, you can set the path to a pre-downloaded model instead of model_url
    model_path=None,
    temperature=0.1,
    max_new_tokens=256,
    # llama2 has a context window of 4096 tokens, but we set it lower to allow for some wiggle room
    context_window=3900,
    # kwargs to pass to __call__()
    generate_kwargs={},
    # kwargs to pass to __init__()
    # set to at least 1 to use GPU
    model_kwargs={"n_gpu_layers": 20},
    # transform inputs into Llama2 format
    messages_to_prompt=messages_to_prompt,
    completion_to_prompt=completion_to_prompt,
    verbose=True,
)


service_context = ServiceContext.from_defaults(
    chunk_size=512,
    llm=llm,
    embed_model=embed_model
)

rerank = SentenceTransformerRerank(
    model="cross-encoder/ms-marco-MiniLM-L-12-v2", top_n=3 # Note here
)


query_engine = index.as_query_engine(similarity_top_k=10, node_postprocessors=[rerank]) # Note we are first selecting 10 chunks.

def predict(input, history):
  response = query_engine.query(input)
  return str(response)

import gradio as gr

gr.ChatInterface(predict).launch(share=True,debug=True)