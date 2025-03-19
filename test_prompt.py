# test_prompt_simple.py
from langchain.prompts import PromptTemplate

template = PromptTemplate(
    input_variables=["text"],
    template="Process this: {text}"
)

text_to_process = "1. Diabetes (E11.9)\n2. Hypertension (I10)"
try:
    prompt = template.format(text=text_to_process)
    print(f"Generated prompt: {prompt}")
except Exception as e:
    print(f"Error: {type(e).__name__} - {str(e)}")