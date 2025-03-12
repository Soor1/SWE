# **Legislation Chat**

## Mission Statement:

The gap that we’ve chosen to try and fill is the lack of political and legislative understanding that the average student has. With the recent change in administration, the need to understand the rapidly changing legislation being put out has become an increasingly prevalent issue. The way that we hope to tackle this issue is via an application that scrapes various news sources daily and stores passed legislation as vectorized embeddings in a vector database for Retrieval Augmented Generation  which will be implemented in a chatbot interface. This will allow users to learn more about current legislation through a more natural language interface. The general architecture for a RAG application can be shown below:

![](https://docs.aws.amazon.com/images/sagemaker/latest/dg/images/jumpstart/jumpstart-fm-rag.jpg)

*[RAG Overview by AWS](https://aws.amazon.com/what-is/retrieval-augmented-generation/)*

 Legislation Chat is a chatbot that provides a way for students to learn about current legislation via a chatbot unlike alternative mediums such as newsletters or subscription based services. Our product allows students to get a tailored experience where they can not only learn the basics of what legislation is being passed, but they can also ask specific follow up questions with regards to things like personal implications.



| Team Role Assignments |  |
| ----- | :---- |
| Joseph Molina | Project Manager |
| Soor Hansalia | Data Engineer (Data Ingestion Pipeline) |
| Adrian Pelaez | Software Developer (Web App) |
| Varun Yelchur | Software Developer (Web App) |


## Our Stack:

**Language:**  
Python

**Front End (Web App):**  
Chainlit Python Front End Framework:

* [https://github.com/Chainlit/chainlit](https://github.com/Chainlit/chainlit)   
* [https://docs.chainlit.io/authentication/oauth](https://docs.chainlit.io/authentication/oauth) 

**Back End (Web App):**  
FastAPI

* [https://fastapi.tiangolo.com/](https://fastapi.tiangolo.com/) 

Hugging Chat for open source LLM calls

* [https://github.com/Soulter/hugging-chat-api](https://github.com/Soulter/hugging-chat-api) 

**Back End (Data Ingestion Pipeline):**  
Beautiful Soup for Web Scraping

* [https://pypi.org/project/beautifulsoup4/](https://pypi.org/project/beautifulsoup4/) 

All-mpnet-base-v2 embedding model to vectorize text

* [https://huggingface.co/sentence-transformers/all-mpnet-base-v2](https://huggingface.co/sentence-transformers/all-mpnet-base-v2) 

**Databases:**  
Pinecone Vector Database for document/legislation embeddings

* [https://www.pinecone.io/](https://www.pinecone.io/) 

MongoDB for storing user preferences and metadata such as auth data

* [https://www.mongodb.com/](https://www.mongodb.com/) 

**Potential Hosting:**  
Render for long-running cloud compute for web app:

* [https://render.com/](https://render.com/) 

Vercel for function based cloud compute (similar to AWS lambda) to be used in data ingestion:

* [https://vercel.com/](https://vercel.com/) 


* For Development *

Go to a directory where you want the project.
```
git clone https://github.com/Soor1/SWE.git
```

Create a new branch based off of dev.
```
git checkout -b new-branch-name dev
```

Create and activate virtual environment.
```
python -m venv .venv
source .venv/Scripts/activate 
#.venv/Scripts/activate for powershell or command prompt
#.venv/Scripts/activate.bat otherwise
```
You should see a little (.venv) tag in your terminal now.


Run the following for installation requirements (this might take a while so be patient)
```
pip install -r requirements.txt
```

## Getting your API Keys!
* Create account on: https://huggingface.co/
* Login at: https://huggingface.co/chat/
* Remember your username and password!!

Create a .env file in your working directory (SWE/) with the following content:
```
HUGGINGFACE_EMAIL="INSERT_EMAIL_HERE"
HUGGINGFACE_PASSWD="INSERT_PASSWORD_HERE"
```

Message @josephmolina256 for the pinecone API key and add it to your .env file:

```
HUGGINGFACE_EMAIL="INSERT_EMAIL_HERE"
HUGGINGFACE_PASSWD="INSERT_PASSWORD_HERE"
PINECONE_API_KEY="GET_API_KEY_FROM_JOSEPH"
```

Visit https://api.congress.gov/ to get your congress API key to fetch bills and insert into your .env

```
HUGGINGFACE_EMAIL="INSERT_EMAIL_HERE"
HUGGINGFACE_PASSWD="INSERT_PASSWORD_HERE"
PINECONE_API_KEY="GET_API_KEY_FROM_JOSEPH"
API_KEY="INSERT_CONGRESS_API_KEY"
```