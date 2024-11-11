from langchain_google_genai import (
    ChatGoogleGenerativeAI,
    HarmBlockThreshold,
    HarmCategory,
    )
from langchain.prompts import ChatPromptTemplate
from dotenv import load_dotenv

load_dotenv()

def render_llm(input):
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        temperature=0.7,
        safety_settings={
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
        },
    )
    
    messages = [
        (
            "system",
            "You are a helpful health assistant whose job is to strictly provides workout regime, diet (based on their locale) and health advice based on the information provided by the human.",
        ),
        ("human", """
         - Name: {name}
         - Age: {age}
         - Sex: {sex}
         - Weight: {weight}
         - Height: {height}
         - Goals: {goals}
         - Country: {country}
         """),
    ]


    prompt = ChatPromptTemplate.from_messages(
        messages
    )
    chain = prompt | llm
    msg = chain.invoke(input.model_dump())

    return msg


def summarize_message(message):
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        temperature=0.7,
        safety_settings={
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
        },
    )
    
    messages = [
        ('system', "You are an expert text summarizer. Your job is to summarize the user text, while retaining as much information as possible."),
        ('human', "{msg}"),
    ]


    prompt = ChatPromptTemplate.from_messages(
        messages
    )
    chain = prompt | llm
    response = chain.invoke({'msg':message})
    return response.content
