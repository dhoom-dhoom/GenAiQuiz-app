from content_module import Generate
import wikipedia

#fastapi imports
from fastapi import FastAPI
from pydantic import BaseModel

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001"],  # Adjust this to your React app's URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TopicRequest(BaseModel):
    topic: str

@app.get("/")
async def root():
    return {"message": "Welcome to the Quiz App"}

@app.post("/submit_topic/")
async def submit_topic(request: TopicRequest):
    topic = request.topic
    search_results = wikipedia.search(topic)
    
    if not search_results:
        return {"error": "enter a valid topic"}
    
    topic = search_results[0]
    try:
        # a = wikipedia.WikipediaPage(topic).content
        summary = wikipedia.summary(topic)
        input = Generate(topic) 
        questions_and_answers = []
        for i in input.get_questions():  # here i is of type string
            question = {"question": i, "options": []}
            j = input.get_content(i)  # here j is a list of string with 4 strings and one integer on the last index
            question["options"] = j[:-1]
            question["answer"] = j[j[-1]]
            questions_and_answers.append(question)
        return {"summary": summary, "quiz": questions_and_answers}
            
    except wikipedia.exceptions.DisambiguationError as e:
        return {"error": "enter a more specific topic"}
    except Exception as e:
        return {"error": str(e)}
 
# JSON STRUCTURE WILL LOOK LIKE   
"""
{
    "summary": "Brief summary of the topic from Wikipedia...",
    "quiz": [
        {
            "question": "Question 1?",
            "options": ["Option A", "Option B", "Option C", "Option D"],
            "answer": "Option A"
        },
        {
            "question": "Question 2?",
            "options": ["Option A", "Option B", "Option C", "Option D"],
            "answer": "Option B"
        }
        
    ]
}

"""



# # Everything modifiable starts here
# topic = input("Enter topic for quiz: ")
# if len(wikipedia.search(topic)) == 0:
#     print("Enter a Valid topic")
# else:
#     topic = wikipedia.search(topic)[0]  # gives an array of key words on the topic that the user has given
#     # print(wikipedia.search(topic))    #(we always use the topic on the 0th index, as it is the most appropriate)
#     print(f"Presenting Q/A for {topic}...")
#     try:
#         a = wikipedia.WikipediaPage(topic).content  # this generates the entire wikipedia page on that topic run -print(a), to see the output
#         input = Generate(topic)  #creating an instance of generate class
#         for i in input.get_questions():  # here i is of type string
#             print(f"\n\nQ){i}\n")
#             j = input.get_content(i)  # here j is a list of string with 4 strings and one integer on the last index
#             print(j)
#             for k in j[:-1]:
#                 print(k)
#             print(f"\nAnswer - {j[j[-1]]}")
#             break
#     except:
#         print("Critical Error Occurred...\nPlease enter a different topic for now!")


