from langchain_google_genai import ChatGoogleGenerativeAI

# Ye Gemini model hai (gpt jaisa hi use hota hai)
llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro", temperature=0.3)

# Test prompt
response = llm.invoke("Tell me how alumni can contribute to university fundraising.")
print(response.content)


