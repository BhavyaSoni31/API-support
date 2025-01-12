from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from langchain_groq import ChatGroq
from langchain.text_splitter import RecursiveCharacterTextSplitter, MarkdownHeaderTextSplitter
from langchain_community.document_loaders import WebBaseLoader, TextLoader
from langchain_community.vectorstores import Chroma
from langchain_cohere import CohereEmbeddings
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
from constants import *
load_dotenv()

# Set embeddings
embedding_model = CohereEmbeddings(model="embed-english-v3.0")

llm = ChatGroq(model=MODEL, temperature=0)


def get_retriever():
    """Get the document retriever object to fetch the documents from vector database."""
    example_vectorstore = Chroma(
    collection_name=COLLECTION_NAME,
    persist_directory=PERSISTENT_DIR,
    embedding_function=embedding_model
    )
    retriever = example_vectorstore.as_retriever(
                    search_type="similarity",
                    search_kwargs={'k': NUMBER_OF_DOC}, # number of documents to retrieve
                )
    docs_in_coll = len(example_vectorstore.get()['documents'])
    print(f'Existing docs: {docs_in_coll}')
    return retriever


def get_relevent_docs(retriever, question):
    docs = retriever.invoke(question)
    return docs

# Data model
class GradeDocuments(BaseModel):
    """Binary score for relevance check on retrieved documents."""

    binary_score: str = Field(
        description="Documents are relevant to the question, 'yes' or 'no'."
    )

def get_valid_documents(question, docs):
    # LLM with function call
    structured_llm_grader = llm.with_structured_output(GradeDocuments)

    # Prompt
    system = """You are a grader assessing relevance of a retrieved document to a user question. \n 
        If the document contains keyword(s) or semantic meaning related to the user question, grade it as relevant. \n
        It does not need to be a stringent test. The goal is to filter out erroneous retrievals. \n
        Give a binary score 'yes' or 'no' score to indicate whether the document is relevant to the question."""
    grade_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system),
            ("human", "Retrieved document: \n {document} \n\n User question: \n {question}"),
        ]
    )
    docs_to_use = []
    retrieval_grader = grade_prompt | structured_llm_grader
    for doc in docs:
        print(doc.page_content, '\n', '-'*50)
        res = retrieval_grader.invoke({"question": question, "document": doc.page_content})
        print(res,'\n')
        if res.binary_score == 'yes':
            docs_to_use.append(doc)

    return docs_to_use

# Post-processing
def format_docs(docs):
    return "\n".join(f"<doc{i+1}>:\nContent:{doc.page_content}\n</doc{i+1}>\n" for i, doc in enumerate(docs))


def generate_answer(question, context):
    # Prompt
    print("generating answer")
    system = """You are an assistant for question-answering tasks. Answer the question based upon your knowledge."""
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system),
            ("human", "Retrieved documents: \n\n <docs>{documents}</docs> \n\n User question: <question>{question}</question>"),
        ]
    )
    # Chain
    rag_chain = prompt | llm | StrOutputParser()

    # Run
    generation = rag_chain.invoke({"documents":format_docs(context), "question": question})
    return generation

# Data model
class GradeHallucinations(BaseModel):
    """Binary score for hallucination present in 'generation' answer."""

    binary_score: str = Field(
        ...,
        description="Answer is grounded in the facts, 'yes' or 'no'"
    )

def check_hellucincation(context, generated_answer):
    print("Checking hellucination")
    # LLM with function call
    structured_llm_grader = llm.with_structured_output(GradeHallucinations)

    # Prompt
    system = """You are a grader assessing whether an LLM generation is grounded in / supported by a set of retrieved facts. \n 
        Give a binary score 'yes' or 'no'. 'Yes' means that the answer is grounded in / supported by the set of facts."""
    hallucination_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system),
            ("human", "Set of facts: \n\n <facts>{documents}</facts> \n\n LLM generation: <generation>{generation}</generation>"),
        ]
    )
    hallucination_grader = hallucination_prompt | structured_llm_grader
    response = hallucination_grader.invoke({"documents": format_docs(context), "generation": generated_answer})
    return response