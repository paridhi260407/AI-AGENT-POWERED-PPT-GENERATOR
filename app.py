#============load modules==============
import os
import time
import langchain
from langchain.agents import create_agent
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
import pytesseract as pyt
from tavily import TavilyClient
import numpy as np
import streamlit as st


#==========API KEYS=============
GOOGLE_KEY=st.sidebar.text_input("Google-API",type="password")
GROQ_KEY=st.sidebar.text_input("Groq-API",type="password")
TAVILY_KEY=st.sidebar.text_input("Tavily-API",type="password")

os.environ["GOOGLE_API_KEY"] = GOOGLE_KEY
os.environ["GROQ_API_KEY"] = GROQ_KEY
os.environ["TAVILY_API_KEY"] = TAVILY_KEY


ALL_API=[GOOGLE_KEY,GROQ_KEY,TAVLIY_KEY]
if not all(ALL_API):
  st.sidebar.error("PASS API-KEYS")
elif any(ALL-API):
  st.sidebar.info("MUST PASS ALL API KEYS")
else:
  st.sidebar.success("API KEYS LOADED SUCCESSFULLY")
  #step:1 model call
  model = ChatGoogleGenerativeAI(
      model="gemini-3.5-flash-lite",
      google_api_key=GOOGLE_API_KEY
  )


#===============FRONTEND================
st.title("AI-AGENT-POWERED PPT GENERATOR")
user_query=st.text_area("write your ppt topic or prompt")
#==================ASSESTs==============
#tool 1
def search_latest_info(query):
  """this function search latest
  news or content from website
  using tavily, helpful to check
  tending content"""
  client = TavilyClient(api_key=TAVILY_API_KEY)
  response = client.search(query)
  return response
#tool 2
def generate_image(img_prompt):
  """this function, helps to generate image
  using free api, with given
  img_prompt using pollination"""
  url = f"https://image.pollinations.ai/{img_prompt}"
  #file handling
  content=r.get(url)
  with open(f"Image.jpeg",'wb') as f:
    f.write(content.content)
  from PIL import Image
  return Image.open("Image.jpeg")
#WITH TABS
tab1, tab2, tab3 = st.tabs(["GENERATE IMAGE",
                           "SEARCH LATEST NEWS",
                           "GENERATE PPT"])
def prompt_generator (model, query):
  prompt = f"""your task is to give detailed prompt instructions for given.
  prompt:
  You are a Professional PPT generator, where
  user will give the query and based on that,
  you have to generate dynamic, HTML output based
  ppt with advanced CSS and Dynamic UI and UX with
  PPT toggle button, Based on Query take image reference to generate
  and embed the same in ppt, using
  Image ref: url = https://images.unsplash.com/photo, 
  or url = https://image.pollinations.ai/, 
  make sure img src must be valid, and image must be
  present inside html, Generate
  with image caption, and no markdowns
  user query given below: {query}
  """

  response = model.invoke(prompt)
  final_prompt = response.content[-1]['text']

  with open("ppt_prompt.txt", 'w') as f:
    f.write(final_prompt)
  return final_prompt

agent = create_agent(
    model = model,
    tools=[search_latest_info,
           generate_image
           ]
)
#=============DISPLAY AGENT==============
st.sidebar.image(agent)
#=============WITH TABS===============
with tab1:
  st.header("GENERATE IMAGE GIVE PROMPT")
  if st.button("click to generate:"):
    with st.spinner("running agent..."):
      data = generate_image(user_query)
      st.image(data)
      st.image(Image.jpeg)
with tab2:
  st.header("CHECK LATEST NEWS")
  if st.button("fetch news"):
    with st.spinner("running agent..."):
      prompt="""give latest news india or world wide related
      to tect,business, jobs, or user requested output
      in properhtml news templates""" + user_query
      response=agent.invoke({'messages':[{'role':"user","content":prompt}]})
      code=response['messages'][-1].content[-1]['text']
      st.html(code,width="stretch",
             unsafe_allow_javascript=True)
with tab3:
  st.header("CHECK LATEST NEWS")
  if st.button("click to generate ppt"):
    with st.spinner("running agent..."):  
      response=agent.invoke({'messages':[{'role':"user","content":final_prompt}]})
      code=response['messages'][-1].content[-1]['text']
      st.html(code,width="stretch",
             unsafe_allow_javascript=True)
      st.download_button(label="DOWNLOAD PPT",
                        data = code,
                        file_name='ppt.html',
                        mimi='text/html')
      st.success("ppt downloaded successfully")    
