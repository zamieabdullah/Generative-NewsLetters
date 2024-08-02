from openai import OpenAI
import random
import os
from dotenv import load_dotenv
import json

load_dotenv()
gpt = os.getenv('gpt_token')
org = os.getenv('gpt_org')
client = OpenAI(api_key=gpt, organization=org)

def read_jsonl(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return [json.loads(line) for line in file]

def generate():
    examples = read_jsonl("./example_docs/blog_posts.jsonl")

    seo_terms = []
    with open('./example_docs/seo_tokens.txt', 'r') as file:
        seo_terms = [line.strip() for line in file]

    seo_topics = []
    for _ in range(0, 15):
        seo_topics.append(random.choice(seo_terms))

    sample = []
    for i in range(0,9):
        index = random.randint(0, len(examples))
        sample.append(examples[index])
        
    examples_str = '\n'.join(json.dumps(example, indent=4) for example in sample[0:8])

    allTopics = [
    "Current real estate market conditions",
    "Housing market predictions",
    "Economic factors affecting real estate",
    "Local market updates",
    "Step-by-step guides for first-time homebuyers",
    "Tips for selling a home quickly and for the best price",
    "Advice on choosing a real estate agent",
    "Understanding mortgage options",
    "DIY home improvement projects",
    "Tips for increasing home value",
    "Seasonal maintenance checklists",
    "Energy-efficient home upgrades",
    "Home staging tips for sellers",
    "Interior design trends",
    "Space-saving ideas for small homes",
    "Color schemes and decorating tips",
    "Profiles of different neighborhoods",
    "Community amenities and local attractions",
    "School district information",
    "Local business reviews",
    "Real estate investment strategies",
    "Tips for becoming a landlord",
    "Understanding property taxes",
    "Financial planning for buying a home",
    "Understanding real estate contracts",
    "Changes in real estate laws and regulations",
    "Tenant rights and landlord responsibilities",
    "Zoning laws and property usage",
    "Eco-friendly home features",
    "Sustainable building practices",
    "Benefits of green homes",
    "Solar energy and other renewable resources",
    "Balancing homeownership with lifestyle choices",
    "Home office setups and work-from-home tips",
    "Pet-friendly home ideas",
    "Family-friendly home features",
    "Smart home technology",
    "Virtual tours and augmented reality in home buying",
    "Online real estate platforms",
    "Home security systems"
    ]

    master_prompt = f"""
                You are a real-estate blog writer. Given examples of blog posts and also extra data accumulated from external
                sources, you will write a unique real estate blog post, making use of SEO keywords to make the blog post stand out. In the blog post itself,
                you will provide:
                    - URL: a url for the blog post that follows SEO standards
                    - Title: A title of what will covered in the blog post
                    - Content: The content of the blog post. Write the blog post in markdown. You do not have to tell me it is in markdown, just please
                            write the blog post in markdown. It should consist of at least 5000 words. Make sure that there is a lot to say 
                            within categories and subcategories, making it an information read for the reader. Also please do not write the title
                            inside the content as it is its own section.
                    - SEO Terms: A list of the SEO keywords used in the blog post
                
                Depending on what is asked of you, based on how many blogposts the client requests from, you will always default to one blog post.
                If the user asks for a specific amount, then provide that amount of blogposts in a listed array. However, in the output, you should respond
                with a json object of this structure:
                    "url": "The blog post url",
                    "title": "The blog post title",
                    "content": "The blog post content",
                    "seo_terms": ["keyword1", "keyword2"]
                Please follow the strucure and put a comma after every single key field. The content should be one whole string and any 
                kind of special character like \n for newline should be integrated within the content string to provide for that newline.
                You do not have to tell me or put into a comment that this is a json, the user will already know its a json.
                Please make sure that you follow the structure above and that something like seo terms is not found within "content", but should rather be 
                in the "seo_terms" key of the object body. I REPEAT DO NOT WRITE THE SEO TERMS WITHIN THE CONTENT IN MARKDOWN. IT SHOULD ONLY BE SEEN
                WITHIN "seo_terms". Please make sure that you are not using external links and link them inside the blog post you generate. 
                Please do not mention anything promotional or any footers regarding where the blog post is getting its data from, 
                how it's written, or anything not related to what a blog post is supposed to write. Please do not write a table of contents. 
                You are simply writing content. Please also make use of real estate SEO terms from example blog posts that may be given from the user.
                """

    user_prompt = f"""
                Hello, I would like you to help me generate a unique real estate blog post. May you please write a blog with this topic: {random.choice(allTopics)}
                Here are examples of how real estate blog posts that I saw and would hope you would be able to come up with something unique that consists 
                of similar topics of the examples: {examples_str}. Follow the structure of the examples, and use some context from the examples, but use 
                the context and create your own blog post. And please provide a lot of numbers and statistics. Only write about event in 2024.
                """
    # print(user_prompt)
    response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": master_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    max_tokens=4096,
                    temperature=0.7,
                )
    
    resp = None
    try:
        resp = json.loads(response.choices[0].message.content)
    except:
        resp = None
    return resp