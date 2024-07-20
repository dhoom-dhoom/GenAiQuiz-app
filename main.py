from g4f.client import Client
import asyncio,wikipedia,random
from asyncio.windows_events import WindowsSelectorEventLoopPolicy
from g4f.Provider import Ollama,Llama,Blackbox,RetryProvider
asyncio.set_event_loop_policy(WindowsSelectorEventLoopPolicy()) #Comment it out if not in windows
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize, word_tokenize
import nltk
wikipedia.set_lang("en")
# nltk.download('stopwords') # Use if running for the first time
def retry_on_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(f"Error: {e}")
            return None
    return wrapper
class content:
    def __init__(self,topic,length):
        self.topic=topic
        self.length=length
        self.summary=self.summary_final()
    def fetch_wikipedia_content(self):
        page = str(wikipedia.WikipediaPage(wikipedia.search(self.topic)[0]).content)
        return page

    def preprocess_text(self,text):
        sentences = sent_tokenize(text)
        words = word_tokenize(text)

        stop_words = set(stopwords.words('english'))
        words = [word.lower() for word in words if word.isalnum() and word.lower() not in stop_words]
        return sentences, words

    def calculate_sentence_scores(self,sentences, words):
        word_frequency = nltk.FreqDist(words)
        sentence_scores = {}
        for i, sentence in enumerate(sentences):
            for word in word_tokenize(sentence.lower()):
                if word in word_frequency:
                    if i in sentence_scores:
                        sentence_scores[i] += word_frequency[word]
                    else:
                        sentence_scores[i] = word_frequency[word]
        return sentence_scores

    def generate(self,sentences, sentence_scores):
        length=self.length
        sorted_scores = sorted(sentence_scores.items(), key=lambda x: x[1], reverse=True)
        top_sentences = sorted(sorted_scores[:length])

        summary = ' '.join([sentences[index] for index, score in top_sentences])
        return summary
    def summary_final(self):
        content=self.fetch_wikipedia_content()
        sentences,words=self.preprocess_text(content)
        sentence_scores = self.calculate_sentence_scores(sentences,words)
        result = self.generate(sentences,sentence_scores)
        return result
class Generate:
    @retry_on_error
    def __private_method0(self,client, messages):
        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                stream=True
            )
            return response
        except Exception as e:
            print(f"Error: {e}")
    def __private_method1(self,user_input):
        self.infolist.append({"role": "user", "content": user_input}) #Modifying this increases Halluciantions
        response_stream = self.__private_method0(self.client, self.infolist)
        if response_stream is None:
            print("Bot seems to be under repair! Please try again later")
            return
        response = ""
        for chunk in response_stream:
            content = chunk.choices[0].delta.content or ""
            response += content
        self.infolist.append({"role": "assistant", "content": response})
        return response
    def __init__(self, topic):
        self.infolist = []
        self.topic = topic
        contents = content(topic,1)
        content2 = str(wikipedia.WikipediaPage(self.topic).summary)
        min_start=1
        start=1
        max_start=len(word_tokenize(str(wikipedia.WikipediaPage(self.topic).content)))
        stored=max_start
        #Binary Search
        if stored< 300:
            content2 = wikipedia.WikipediaPage(self.topic).content
        else:
            while not (300<=len(word_tokenize(content2))<=600):
                if len(word_tokenize(content2)) >600:
                    max_start=start
                    start=(start+min_start)//2
                    content2=content(topic,start).summary_final()
                elif len(word_tokenize(content2))<300:
                    min_start=start
                    start=(max_start+start)//2
                    content2=content(topic,start).summary_final()
                if start==1 or start==stored:
                    break
                elif (start==min_start and start==max_start+1):
                    break
                elif (start==max_start and start==min_start):
                    break
        self.content = content2 + " "+contents.summary_final()
        self.client = Client(
            provider=RetryProvider([
                Ollama,
                Blackbox,
                Llama
            ])
        )

    def get_questions(self):
        # Base prompt components
        base_prompt = "Ask a new thought provoking question for a student about {self.topic} using 20 words or less."
        note = " Do not start with 'Here's a new thought-provoking question for a student about Eigenvalues'."
        info = f" You may use the following information: {self.content}"
        restriction = "\n\n However you must only write 'textual' question and you must ONLY write the question without options and nothing else."
        condition = f"\n\n Ask objective type questions without answers and be specific about {self.topic}."
        dimensions = ["technical", "ethical", "theoretical", "comparative", "interdisciplinary", "practical",
                      "historical", "legal", "social",  "educational"]
        store = []
        for i in range(1, 11):
            explore = f"\n\n You must only explore the dimension '{dimensions[i % len(dimensions)]}' about {self.topic} as much as possible in this question."
            prompt = base_prompt + note + info + restriction + condition + explore
            result = self.__private_method1(prompt)
            store.append(result)
        return store
    def __private_method2(self,question):
        #This is prompt for the correct option
        self.infolist.clear()
        prompt = f"For this question {question}, generate the most accurate answer possible in 10 words or less."
        info = f"You may use the following information: {self.content}"
        restriction="\n\nHowever, you must only write 'textual' response and you must only write it in the form of '1' option and nothing else"
        condition="\n\n You must not cross the word limit and not provide one word answers.\n\n You must only give objective type answer to the given question"
        require="\nDon't start with indexing like 1. and Don't start with Yes/No"
        result=self.__private_method1(prompt+info+restriction+condition+require)
        return result
    def get_content(self,question):
        # This is prompt for wrong options
        prompt = f"For this question {question}, generate a new highly possible but wrong option in 10 words or less."
        info = f"You may use the following information: {self.content}"
        restriction = "\n\n However, you must only write 'textual' response and you must only write one option and nothing else"
        condition = "\n\n Your option should not be correct, but it should not be unrelated to the question. \n\nPeople should make the mistake of assuming it as answer."
        require="\nDon't start with index And don't give any clues about it being wrong option"
        answer = self.__private_method2(question)
        self.infolist.clear()
        store = []
        for i in range(1,4):
            result = self.__private_method1(prompt+info+restriction+condition+require)
            store.append(result)
        store.append(answer)
        random.shuffle(store)
        store.append(store.index(answer))
        return store

#Everything modifiable starts here
topic=input("Enter topic for quiz: ")
if len(wikipedia.search(topic))==0:
    print("Enter a Valid topic")
else:
    topic=wikipedia.search(topic)[0]
    print(f"Presenting Q/A for {topic}...")
    try:
        a=wikipedia.WikipediaPage(topic).content
        input = Generate(topic)
        for i in input.get_questions():
            print(f"\n\nQ){i}\n")
            j = input.get_content(i)
            for k in j[:-1]:
                print(k)
            print(f"\nAnswer - {j[j[-1]]}")
    except:
        print("Critical Error Occurred...\nPlease enter a different topic for now!")
