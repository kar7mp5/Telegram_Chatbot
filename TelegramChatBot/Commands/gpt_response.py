# gpt_response.py
from telegram.ext import ContextTypes
from telegram import Update


# llm libaries
# from langchain_community.llms import Ollama
# from langchain import PromptTemplate


import wikipedia

# VecDB libaries
# from langchain.docstore.document import Document
# from langchain.text_splitter import RecursiveCharacterTextSplitter
# from langchain.chains import RetrievalQA
# from langchain.vectorstores import Chroma
# from langchain.embeddings import SentenceTransformerEmbeddings


from dotenv import load_dotenv
import os


load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


async def gpt_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """GPT response
    
    Args:
        update (Update): Incoming update containing the message.
        context (ContextTypes.DEFAULT_TYPE): Contextual information related to the command.
    
    Returns:
        chat_completion (str): gpt response
    """
    # Set llm model that gemma2:2b
    model = Ollama(model='gemma2:2b', stop=["<|eot_id|>"])
    
    user_prompt = update.message.text

    keyword_extract_system_prompt = """
Think and write your step-by-step reasoning before responding.  
Please write only the fully spelled-out form of the acronym in English that corresponds to the following user's question, without abbreviations or additional text.  

For example, if the user asks 'RAG,' output 'Retrieval-Augmented Generation,' or for 'CNN,' output 'Convolutional Neural Network.'

If the user asks about 'MoE,' the output should be 'Mixture of Experts' and nothing else.
And you don't know how to response, just say false.
"""
    # Set prompt template
    template = """
<|begin_of_text|>
<|start_header_id|>system<|end_header_id|>
{system_prompt}
<|eot_id|>
<|start_header_id|>user<|end_header_id|>
{user_prompt}
<|eot_id|>
<|start_header_id|>assistant<|end_header_id|>
"""

    # Search the keyword of sentence
    prompt = PromptTemplate(
        input_variables=['system_prompt', 'user_prompt'],
        template=template
    )

    # Extract the keyword
    key_word = model(prompt.format(system_prompt=keyword_extract_system_prompt, user_prompt=user_prompt)).strip()
    
    # Initialize variables
    search_keyword = None
    response = None
    
    # Request 404
    if key_word == "false":
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="문서를 찾을 수 없습니다. 문서 검색 없이 답변하겠습니다."
        )

        user_prompt = f"{user_prompt} on detail."
        system_prompt = """
Please write all conversations in Korean(한국어).
Think and write your step-by-step reasoning before responding.
Write the article title using ## in Markdown syntax.
"""     
        # Inference without RAG
        response = model(prompt.format(system_prompt=system_prompt, user_prompt=user_prompt)).strip()
        
        # Send output message
        await context.bot.send_message(
            chat_id=update.effective_chat.id, 
            text=response
        )

    # Request 200
    else:
        search_keyword = wikipedia.search(key_word)

        # Send message to confirm document search
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"{search_keyword[0]} 문서를 검색하시겠습니까?",
            reply_markup={
                'inline_keyboard': [
                    [
                        {'text': '예', 'callback_data': 'yes_search'},
                        {'text': '아니오', 'callback_data': 'no_search'}
                    ]
                ]
            }
        )

        # Store search keyword in user data for later use
        context.user_data['question'] = user_prompt
        context.user_data['search_keyword'] = search_keyword[0]

        return  # Exit the function to wait for user's response


async def handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Set llm model that gemma2:2b
    model = Ollama(model='gemma2:2b', stop=["<|eot_id|>"])

    # Set prompt template
    template = """
<|begin_of_text|>
<|start_header_id|>system<|end_header_id|>
{system_prompt}
<|eot_id|>
<|start_header_id|>user<|end_header_id|>
{user_prompt}
<|eot_id|>
<|start_header_id|>assistant<|end_header_id|>
"""

    # Search the keyword of sentence
    prompt = PromptTemplate(
        input_variables=['system_prompt', 'user_prompt'],
        template=template
    )

    query = update.callback_query
    await query.answer()  # User clicked the button

    search_keyword = context.user_data.get('search_keyword')  # Get the stored search keyword

    if query.data == 'yes_search':
        # Document search logic
        data = wikipedia.page(search_keyword).content
        doc = Document(page_content=data)

        # Add the Wikipedia document on VecDB
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=0) 
        all_splits = text_splitter.split_documents([doc])
        embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
        vectorstore = Chroma.from_documents(documents=all_splits, embedding=embeddings)

        # Add the prompt that inference output on detail
        user_prompt = f"{query.message.text} on detail by korean."
        system_prompt = """
Please write all conversations in Korean(한국어).
Think and write your step-by-step reasoning before responding.
Write the article title using ## in Markdown syntax.
"""

        # Chain RAG
        qachain = RetrievalQA.from_chain_type(model, retriever=vectorstore.as_retriever())
        response = qachain(prompt.format(system_prompt=system_prompt, user_prompt=user_prompt))
        
        # Send output message using RAG
        await context.bot.send_message(
            chat_id=update.effective_chat.id, 
            text=response['result']
        )
    
    elif query.data == 'no_search':
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="문서 검색을 취소했습니다."
        )
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="문서 검색 없이 답변하겠습니다."
        )

        user_prompt = context.user_data.get('question')
        system_prompt = """
Please write all conversations in Korean(한국어).
Think and write your step-by-step reasoning before responding.
Write the article title using ## in Markdown syntax.
"""     
        # Inference without RAG
        response = model(prompt.format(system_prompt=system_prompt, user_prompt=user_prompt)).strip()
        
        # Send output message
        await context.bot.send_message(
            chat_id=update.effective_chat.id, 
            text=response
        )