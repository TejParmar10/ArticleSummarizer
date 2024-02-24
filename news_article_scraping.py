import requests
from newspaper import Article
from langchain.schema import (
    HumanMessage
)
# from langchain.chat_models import ChatOpenAI
from langchain_openai import ChatOpenAI
# from langchain_community.chat_models import ChatOpenAI
# from langchain_openai import ChatOpenAICompatibility
from langchain.output_parsers import PydanticOutputParser
from pydantic import validator
from pydantic import BaseModel, Field
from typing import List


# create output parser class
class ArticleSummary(BaseModel):
    title: str = Field(description="Title of the article")
    summary: List[str] = Field(description="Bulleted list summary of the article")

    # validating whether the generated summary has at least three lines
    @validator('summary', allow_reuse=True)
    def has_three_or_more_lines(cls, list_of_lines):
        if len(list_of_lines) < 3:
            raise ValueError("Generated summary has less than three bullet points!")
        return list_of_lines

# set up output parser
parser = PydanticOutputParser(pydantic_object=ArticleSummary)
# Aboce is the code for settup up the output parser
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36'
}
article_url = "https://bleacherreport.com/articles/2375473-the-sports-science-behind-lionel-messis-amazing-dribbling-ability"
session = requests.Session()
try:
    response = session.get(article_url, headers=headers, timeout=10)   
    if response.status_code == 200:
        article = Article(article_url)
        article.download()
        article.parse()
        print(f"Title: {article.title}")
        # print(f"Text: {article.text}")  
        article_title = article.title
        article_text = article.text   
        chat = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.9)   
        # chat=ChatOpenAICompatibility(model_name="gpt-3.5-turbo", temperature=0.8) 
        # template = """You are a very good assistant that summarizes online articles and gives the data in bulleted points.

        #             Here's the article you want to summarize.

        #             ==================
        #             Title: {article_title}

        #             {article_text}
        #             ==================   

        #             Write a summary of the previous article.
        #             """
        template = """
As an advanced AI, you've been tasked to summarize online articles into bulleted points. Here are a few examples of how you've done this in the past:

Example 1:
Original Article: 'The Effects of Climate Change
Summary:
- Climate change is causing a rise in global temperatures.
- This leads to melting ice caps and rising sea levels.
- Resulting in more frequent and severe weather conditions.

Example 2:
Original Article: 'The Evolution of Artificial Intelligence
Summary:
- Artificial Intelligence (AI) has developed significantly over the past decade.
- AI is now used in multiple fields such as healthcare, finance, and transportation.
- The future of AI is promising but requires careful regulation.

Now, here's the article you need to summarize:

==================
Title: {article_title}

{article_text}
==================

Please provide a summarized version of the article in a bulleted list format.
"""

        prompt = template.format(article_title=article.title, article_text=article.text)
        messages = [HumanMessage(content=prompt)]
        summary = chat.invoke(messages)
        print(article_title)
        print(summary.content)
    else:
        print(f"Failed to fetch article at {article_url}")
except Exception as e:
    print(f"Error occurred while fetching article at {article_url}: {e}")
