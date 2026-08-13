from dotenv import load_dotenv
from openai import OpenAI
import json 
import gradio as gr
import os
import requests
from pypdf import PdfReader
load_dotenv(override=True)
load_dotenv(r"C:\Users\PC\projects\agents\.env")
openai = OpenAI()
groq_api_key = os.getenv("GROQ_API_KEY")
groq = OpenAI(api_key=groq_api_key, base_url="https://api.groq.com/openai/v1")

pushover_user = os.getenv("PUSHOVER_USER")
pushover_token = os.getenv("PUSHOVER_TOKEN")
pushover_url = "https://api.pushover.net/1/messages.json"

if pushover_user:
    print(f"Pushover user found and starts with {pushover_user[0]}")
else:
    print("Pushover user not found")

if pushover_token:
    print(f"Pushover token found and starts with {pushover_token[0]}")
else:
    print("Pushover token not found")
def push(message):
    payload = {
        "user": pushover_user,
        "token": pushover_token,
        "message": message
    }

    response = requests.post(
        "https://api.pushover.net/1/messages.json",
        data=payload
    )

    print(response.status_code)
    print(response.text)
def explain_topic(topic): # Tool 1
    system_prompt="""
                    You are an AI study assistant and your role is to provide detailed explanation to the user 
                    about the topic he asks you to explain and all the information and detail should be in 
                    a very organized form
                    """
    message=[{"role":"system","content":system_prompt},{"role":"user","content":topic}]
    response = groq.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=message
        ) 
    push(f"Explanation generated for {topic}")

    return response.choices[0].message.content


def generate_quiz(topic): # Tool 2
    system_prompt="""
                    You are an AI study assistant and your role is to provide a quiz to the user 
                    for the topic he asks you. The quiz should of 5 to 10 mcqs and below the quiz 
                    also provide an answer key of this quiz.
                    """
    message=[{"role":"system","content":system_prompt},{"role":"user","content":topic}]
    response = groq.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=message
        ) 
    push(f"Quiz generated for {topic}")

    return response.choices[0].message.content


def generate_flashcards(topic): # Tool 3
    system_prompt="""
                        You are an AI study assistant and your role is to provide flashcards to the user 
                        for the topic he asks for.
                        """
    message=[{"role":"system","content":system_prompt},{"role":"user","content":topic}]
    response = groq.chat.completions.create(
                model="openai/gpt-oss-120b",
                messages=message
            ) 
    push(f"Flashcards generated for {topic}")

    return response.choices[0].message.content

def create_study_plan(subjects,remaining_days,hours_per_day): # Tool 4
    system_prompt="""
                    You are an AI study assistant and your role is to create a study plan for the student
                    on the info he provides. He will be providing you the details abouts his subjects,the 
                    days remaining and the hours he can study per day. Then you have to provide the plan 
                    accordingly
                    """
    message=[{"role":"system","content":system_prompt},{"role":"user","content":f"""
    {subjects}. These are my subjects, The remaining days are {remaining_days} and I can study
    {hours_per_day} hours per days """}]
    response = groq.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=message
        ) 
    push(f"Study plan generated")

    return response.choices[0].message.content

def save_notes(topic,notes): # tool 5
    with open("notes.txt","a",encoding="utf-8") as file:
        file.write(f"==={topic}===")
        file.write(notes)
        file.write("\n")
        file.write("======\n\n")
    push("Notes saved in notes.txt file")
    return "Notes saved"

def view_notes(): # tool 6
    with open("notes.txt","r") as file:
        notes=file.read()
    push("Viewed all the notes from notes.txt file")
    return notes

def delete_notes(topic): # tool 7
    with open("notes.txt","r") as file:
        lines=file.readlines()
    skip=False
    new_lines=[]
    for line in lines:
        if line.strip()==f"==={topic}===":
            skip=True
            continue
        if skip and line.strip()=="======":
            skip=False
            continue
        if not skip:
            new_lines.append(line)
    with open("notes.txt","w") as file:
        file.writelines(new_lines)
    push(f"Notes of {topic} deleted successfully")
    return "Notes deleted"

def summarize_notes(notes): # tool 8
    system_prompt= """ You are an AI assistant. Your role is to summarize the notes given by the user"""
    message=[{"role":"system","content":system_prompt},{"role":"user","content":notes}]
    response = groq.chat.completions.create(
                model="openai/gpt-oss-120b",
                messages=message
            ) 
    push("Notes summarized sucessfully")
    return response.choices[0].message.content

def read_pdf(question): # tool 9
    reader = PdfReader("me/Data Structures and Algorithms.pdf")
    pdf_text = ""
    for page in reader.pages:
        text = page.extract_text()
        if text:
            pdf_text += text
    system_prompt=f""" You are an AI assisatant and your task is to answer the question which
                  user asks from {pdf_text}"""
    message=[{"role":"system","content":system_prompt},{"role":"user","content":question}]
    response = groq.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=message
        ) 
    push("Answered the question from the pdf")

    return response.choices[0].message.content

def quiz_history(quiz,users_answers,topic): # tool 10
    system_prompt=f"""Here in {quiz} we have our quiz of {topic} with answer key as well. These are the answers given
    by the user which are {users_answers}. Your task is to compare the correct answers with the user's 
    answers and give a score """
    message=[{"role":"system","content":system_prompt},{"role":"user","content":f"""This is the quiz {quiz} of {topic}
     and these are the user's answers {users_answers}"""}]
    response = groq.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=message
        ) 
    score=response.choices[0].message.content
    with open("quiz history.txt","a") as file:
        file.write(f"{topic} Score: {score}\n")
    push("Score Stored Successfully")
    return score

# Starting Tools description

 # Tool 1
json_explain_topic = {   "name": "explain_topic",
    "description": "This is used to give full explanation of the topic which is asked by the user",
    "parameters": {
        "type": "object",
        "properties": {
            "topic": {
                "type": "string",
                "description": "The topic about which the explanation is required"
            },
        },
        "required": ["topic"]}}

# Tool 2
json_generate_quiz={"name": "generate_quiz",
    "description": "This is used to generate a quiz for the topic given by the user",
    "parameters": {
        "type": "object",
        "properties": {
            "topic": {
                "type": "string",
                "description": "The topic for which the quiz is required"
            },
        },
        "required": ["topic"]
    }}


# Tool 3
json_generate_flashcards={   "name": "generate_flashcards",
    "description": "This is used to generate the flashcards for the topic given by user",
    "parameters": {
        "type": "object",
        "properties": {
            "topic": {
                "type": "string",
                "description": "The topic for which flashcards are required"
            },
        },
        "required": ["topic"]
    }}

# Tool 4
json_create_study_plan={ "name": "create_study_plan",
    "description": """This is used to generate a study plan based on the user's subjects,remaining days and the 
     number of hours he can study daily""",
    "parameters": {
        "type": "object",
        "properties": {
            "subjects": {
                "type": "string",
                "description": "The subjects he needs to study"
            },"remaining_days":{
                "type":"integer","description":"The number of days left to prepare for the exams"
            },"hours_per_day":{"type":"integer","description":"The number of hours he can study daily"
        }},
        "required": ["subjects","remaining_days","hours_per_day"]
    }}

# Tool 5
json_save_notes={"name": "save_notes",
    "description": "This is used to save the notes of a topic which user wants to save in notes.txt file",
    "parameters": {
        "type": "object",
        "properties": {
            "topic": {
                "type": "string",
                "description": "The topic whose notes should be stored"
            },"notes":{"type":"string","description":"The notes which are to be saved"}
        },
        "required": ["topic","notes"]
        }}

# Tool 6

json_view_notes={"name": "view_notes",
    "description": "This is used to view all the notes from notes.txt file",
    "parameters": {
        "type": "object",
        "properties":{}
        }}
# Tool 7
json_delete_notes={"name": "delete_notes",
    "description": "This is used to delete the notes of a specific topic which the user wants to delete",
    "parameters": {
        "type": "object",
        "properties": {
            "topic": {
                "type": "string",
                "description": "The topic whose notes the user wants to delete"
            },
        },
        "required": ["topic"]
    }}

# Tool 8
json_summarize_notes={"name": "summarize_notes",
    "description": "This is use to summarize the notes provided by the user",
    "parameters": {
        "type": "object",
        "properties": {
            "notes": {
                "type": "string",
                "description": "The notes which are to be summarized"
            }},
        "required":["notes"]
        }
    }

# Tool 9

json_read_pdf={"name": "read_pdf",
    "description": "This is used to answer the question of the users",
    "parameters": {
        "type": "object",
        "properties": {
            "question": {
                "type": "string",
                "description": "The question asked by the user"
            },
        },
        "required": ["question"]
    }}

# Tool 10
json_quiz_history={"name": "quiz_history",
    "description": "This is used to store the score of the quizzes in quiz history.txt file",
    "parameters": {
        "type": "object",
        "properties": {
            "quiz": {
                "type": "string",
                "description": "The quiz whose score is to be stored"
            },"topic":{"type":"string","description":"The topic of the quiz"},
        "users_answers":{"type":"string","description":"The answers of the quiz given bt the user"
        }},
        "required": ["quiz","topic","users_answers"]
    }}

tools=[{"type":"function","function":json_explain_topic},
       {"type":"function","function":json_generate_quiz},
       {"type":"function","function":json_generate_flashcards},
       {"type":"function","function":json_create_study_plan},
       {"type":"function","function":json_save_notes},
       {"type":"function","function":json_view_notes},
       {"type":"function","function":json_delete_notes},
       {"type":"function","function":json_summarize_notes},
       {"type":"function","function":json_read_pdf},
       {"type":"function","function":json_quiz_history}]

system_prompt="""You are an AI Study Assistant for university students.

Understand the user's request and use the most appropriate available tool when needed.

When a tool is called:
- Use all required arguments correctly.
- Use the tool's result to answer the user.
- Always provide the actual result, not just say that the task was completed.
- Do not invent information or claim a task was completed if it failed.

For study-related questions, explain concepts clearly and simply.
Maintain context from the conversation and answer follow-up questions appropriately. """


def chat(message,history):
    clean_history = []

    for msg in history:
        clean_history.append({
            "role": msg["role"],
            "content": msg["content"]
        })
    print(json.dumps(json_explain_topic, indent=2))
    print(json.dumps(json_generate_quiz, indent=2))
    print(json.dumps(json_generate_flashcards, indent=2))
    print(json.dumps(json_create_study_plan, indent=2))
    print(json.dumps(json_save_notes, indent=2))
    print(json.dumps(json_summarize_notes, indent=2))
    print(json.dumps(json_delete_notes, indent=2))
    print(json.dumps(json_quiz_history, indent=2))
    print(json.dumps(json_view_notes, indent=2))
    print(json.dumps(json_read_pdf, indent=2))
    print(json.dumps(tools, indent=2))

    messages=[{"role":"system","content":system_prompt}] + clean_history + [{"role":"user","content":message}]
    response = groq.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=messages,
        tools=tools
    )

    while response.choices[0].finish_reason == "tool_calls":
         assistant_message = response.choices[0].message
         messages.append(assistant_message)
         for tool_call in assistant_message.tool_calls:
            if tool_call.function.name=="explain_topic": # Tool 1
                topic = json.loads(tool_call.function.arguments).get("topic")
                result=explain_topic(topic)
            elif tool_call.function.name=="generate_quiz": # Tool 2
                topic = json.loads(tool_call.function.arguments).get("topic")
                result=generate_quiz(topic)
            elif tool_call.function.name=="generate_flashcards": # Tool 3
                topic = json.loads(tool_call.function.arguments).get("topic")
                result=generate_flashcards(topic)
                print("FLASHCARD RESULT:")
                print(result)
            elif tool_call.function.name=="create_study_plan": # Tool 4
                subjects = json.loads(tool_call.function.arguments).get("subjects")
                remaining_days= json.loads(tool_call.function.arguments).get("remaining_days")
                hours_per_day = json.loads(tool_call.function.arguments).get("hours_per_day")
                result=create_study_plan(subjects,remaining_days,hours_per_day)
            elif tool_call.function.name=="save_notes": # Tool 5
                notes = json.loads(tool_call.function.arguments).get("notes")
                topic= json.loads(tool_call.function.arguments).get("topic")
                result=save_notes(topic,notes)
            elif tool_call.function.name=="view_notes": # tool 6
                result=view_notes()
            elif tool_call.function.name=="delete_notes": # tool 7
                topic = json.loads(tool_call.function.arguments).get("topic")
                result=delete_notes(topic)
            elif tool_call.function.name=="summarize_notes": # tool 8
                notes = json.loads(tool_call.function.arguments).get("notes")
                result=summarize_notes(notes)
            elif tool_call.function.name=="read_pdf": # tool 9
                question = json.loads(tool_call.function.arguments).get("question")
                result=read_pdf(question)
            elif tool_call.function.name=="quiz_history": # tool 10
                topic = json.loads(tool_call.function.arguments).get("topic")
                quiz = json.loads(tool_call.function.arguments).get("quiz")
                users_answers = json.loads(tool_call.function.arguments).get("users_answers")
                result=quiz_history(quiz,users_answers,topic)
            messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": result})

            response = groq.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=messages,
            tools=tools) 
    return response.choices[0].message.content
gr.ChatInterface(chat).launch()



            
            
            

        


    

    




    
