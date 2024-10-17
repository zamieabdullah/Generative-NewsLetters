from openai import OpenAI
import random
import os
from dotenv import load_dotenv
import json
from bs4 import BeautifulSoup
from sqlalchemy import func
from models.model import db
from models.examples import Examples, Titles

load_dotenv()
gpt = os.getenv('gpt_token')
org = os.getenv('gpt_org')
client = OpenAI(api_key=gpt, organization=org)

def read_jsonl(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return [json.loads(line) for line in file]

def generate():

    topic =  db.session.query(Titles).order_by(func.random()).first()
    print("title" , topic.titles, flush=True)

    random_blog = db.session.query(Examples).order_by(func.random()).limit(8)
    resp = {}
    blogs = []

    for blog in random_blog:
        blogs.append(blog.content)
        
    examples_str = '\n'.join(blogs)

    master_prompt = f"""
                You are a real-estate blog writer. Given examples of blog posts and also extra data accumulated from external
                sources, you will write a unique real estate blog post, making use of SEO keywords to make the blog post stand out. In the blog post itself,
                you will provide:
                    - URL: A URL for the blog post based on the title, following SEO standards. 
                    **The URL should only consist of alphanumeric characters and dashes (-), derived directly from the title. 
                    Do NOT include any slashes (/) or extra prefixes like '/blogs/' or '/'.**
                    - Title: A title for the blog post that captures the main topic. The title should not appear in the content.
                    - Content: The content of the blog post, with at least 5000 words. Write in HTML format, and do not include the title.
                    - SEO Terms: A list of SEO keywords used in the blog post.
                
                Depending on what is asked of you, based on how many blogposts the client requests from, you will always default to one blog post.
                If the user asks for a specific amount, then provide that amount of blogposts in a listed array. However, in the output, you should respond
                with a json object of this structure:
                    "url": "The blog post url",
                    "title": "The blog post title",
                    "content": "The blog post content",
                    "seo_terms": ["keyword1", "keyword2"]
                Please follow the structure and put a comma after every single key field. The content should be one whole string and any 
                kind of special character like \n for newline should be integrated within the content string to provide for that newline.
                You do not have to tell me or put into a comment that this is a json, the user will already know its a json.
                Please make sure that you follow the structure above and that something like seo terms is not found within "content", but should rather be 
                in the "seo_terms" key of the object body. I REPEAT DO NOT WRITE THE SEO TERMS WITHIN THE CONTENT IN MARKDOWN. IT SHOULD ONLY BE SEEN
                WITHIN "seo_terms". Please make sure that you are not using external links and link them inside the blog post you generate. 
                Please do not mention anything promotional or any footers regarding where the blog post is getting its data from, 
                how it's written, or anything not related to what a blog post is supposed to write. Please do not write a table of contents. 
                You are simply writing content. Please also make use of real estate SEO terms from example blog posts that may be given from the user.
                When it comes to the structure of the content, do not add "Introduction" or "Conclusion" headers. Introduce and conclude creatively.
                """

    user_prompt = f"""
                Hello, I would like you to help me generate a unique real estate blog post. 
                Please make sure to surround the topic around buying land, combining the land buying and this topic {topic.titles} into a seamless read in the blog post. 
                Here are examples of how real estate blogs: {examples_str}. Follow the structure of the examples, and use some context from the examples, but use 
                the context and create your own unique blog post. And please provide a lot of numbers and statistics. Write the blog around the current month of 
                September 2024. Make the blog location specific. The setting for the blog is in Texas. You can choose any city in Texas.  Make sure that SEO keywords are also seen frequently.
                Write the blog in HTML format as well and follow SEO formatting. Do not use "Introduction" or "Conclusion" as headers. Be a little more creative than that.
                """
    # print(user_prompt)
    tools = [
        {
            "type": "function",
            "function": {
                "name": "generate_blogpost",
                "description": "Generate a detailed real estate blog post based on user request and make use of SEO terms as keywords when constructing url, title and content",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": "URL for the blog post, derived from the title. Only alphanumeric characters and dashes (-). Do not include any slashes or extra prefixes.",
                        },
                        "title": {
                            "type": "string",
                            "description": "Includes title for real estate blogpost that engages SEO keywords of real estate based on the topic. The title should not appear in the content section",
                        },
                        "content": {
                            "type": "string",
                            "description": """Includes content for real estate blogpost that engages SEO keywords of real estate based on the topic. Put this is HTML and 
                                                make sure to follow SEO format. Do not put the title in the content. The title should only appear in the title section.
                                                Do not use the word "Introduction" or "Conclusion". Introduce the blog post with a creative header and conclude with creative header.
                                            """,
                        },
                        "seo_terms": {
                            "type": "array",
                            "items": {
                                "type": "string"
                            },
                            "description": "Provide the list of SEO terms used when creating the real estate blogpost",
                        }
                    },
                    "required": [
                        "url",
                        "title",
                        "content",
                        "seo_terms",
                    ]
                }
            }
        }
    ]
    # print(user_prompt)
    response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": master_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    tools=tools,
                    tool_choice="required",
                    max_tokens=4096,
                    temperature=0.7,
                )
    
    resp = None
    response_dump = response.model_dump()
    choices = response_dump.get("choices",[])
    if choices:
        message = choices[0].get("message", {})
        tool_calls = message.get("tool_calls", [])
        if tool_calls:
            function = tool_calls[0].get("function", {})
            arguments = function.get("arguments", {})
            if arguments:
                response_json = arguments
    try:
        resp = json.loads(response_json)
    except:
        resp = None
    return resp

def review(content):
    master_prompt_2 = """
        You are a real estate blog post reviewer. Your job is to read through the contents of real estate blog posts and provide suggestions
        on how to make it better in terms of content, SEO, and providing more stats or information that will make the real estate blogpost more 
        accurate to current data.
    """

    user_prompt_2 = f"""
            I wrote a real estate blog post based on this topic: {content["title"]}. Here is the blog post that I wrote: {content["content"]}.
            Can you give me suggestions to make it better in terms of content, writing style, and better SEO suggestions.
    """

    tool2 = [
        {
            "type": "function",
            "function": {
                "name": "generate_edits",
                "description": "Generate a detailed list of suggestions to make the real estate blog post provided by the user better when it comes to content, data, and SEO rules",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "suggestions": {
                            "type": "string",
                            "description": "List of suggestions for improvements on the real estate blog post"
                        }
                    },
                    "required": [
                        "suggestions",
                    ]
                }
            }
        }
    ]

    response2 = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": master_prompt_2},
                        {"role": "user", "content": user_prompt_2},
                    ],
                    tools=tool2,
                    tool_choice="required",
                    max_tokens=4096,
                    temperature=0.7,
                )
    
    response_dump2 = response2.model_dump()
    choices2 = response_dump2.get("choices",[])
    if choices2:
        message2 = choices2[0].get("message", {})
        tool_calls2 = message2.get("tool_calls", [])
        if tool_calls2:
            function2 = tool_calls2[0].get("function", {})
            arguments2 = function2.get("arguments", {})
            if arguments2:
                response_json2 = arguments2
    try:
        data2 = json.loads(response_json2)
        return data2
    except:
        return None
    
def final_draft(content, suggestions):
    master_prompt_3 = """
        You are a skilled real estate blog post writer tasked with crafting the final draft of a blog post. You will receive the first draft of the 
        blog post along with a set of suggestions provided by a real estate blog post reviewer. Your task is to carefully review the first draft 
        and fully incorporate the suggestions provided to create a polished final draft. Enhance the clarity, engagement, and natural flow of 
        the content, ensuring it reads smoothly and appeals to the target audience. Remember to humanize the content, making it feel conversational and 
        approachable while retaining the key messages and SEO elements. There should be a noticeable difference from the original draft.
    """


    user_prompt_3 = f"""
    I wrote an initial draft of a real estate blog post on the topic: {content["title"]}. I want to improve this draft based on suggestions I received from a real estate blog post reviewer.

    Here is the first draft of the blog post:
    {content['content']}

    Here are the suggestions:
    {suggestions['suggestions']}

    Please incorporate these suggestions into the final draft, enhancing readability, tone, and structure. Ensure the final draft is more engaging, flows naturally, and is well-aligned with the topic and SEO objectives.
    """


    tools_3 = [
        {
            "type": "function",
            "function": {
                "name": "generate_reviewed_blogpost",
                "description": "Generate a final draft of a real estate blogpost that was provided by the user and rewrite it with the suggestions they provided",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": "Includes url for real estate blogpost that engages SEO keywords of real estate based on the topic. Only provide everything after the domain name",
                        },
                        "title": {
                            "type": "string",
                            "description": "Includes title for real estate blogpost that engages SEO keywords of real estate based on the topic.",
                        },
                        "content": {
                            "type": "string",
                            "description": "Includes content for real estate blogpost that engages SEO keywords of real estate based on the topic. Can you use html for this. Only provide the content of blog post do not add your own thoughts outside of the blog posts",
                        },
                        "seo_terms": {
                            "type": "array",
                            "items": {
                                "type": "string"
                            },
                            "description": "Provide the list of SEO terms used when creating the real estate blogpost",
                        }
                    },
                    "required": [
                        "url",
                        "title",
                        "content",
                        "seo_terms",
                    ]
                }
            }
        }
    ]

    response3 = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": master_prompt_3},
                        {"role": "user", "content": user_prompt_3},
                    ],
                    tools=tools_3,
                    tool_choice="required",
                    max_tokens=4096,
                    temperature=1.0,
                )
    
    response_dump3 = response3.model_dump()
    choices3 = response_dump3.get("choices",[])
    if choices3:
        message3 = choices3[0].get("message", {})
        tool_calls3 = message3.get("tool_calls", [])
        if tool_calls3:
            function3 = tool_calls3[0].get("function", {})
            arguments3 = function3.get("arguments", {})
            if arguments3:
                response_json3 = arguments3
    try:
        data3 = json.loads(response_json3)
        return data3
    except:
        return None
    
def html_to_str(html_str):
    # Parse the HTML
    soup = BeautifulSoup(html_str, "html.parser")

    # Extract text (strip HTML tags)
    text = soup.get_text()

    # Split the text into words
    words = text.split()

    # Extract the first 30 words
    first_30_words = words[:30]

    # Join them back into a string
    result = ' '.join(first_30_words)

    return result