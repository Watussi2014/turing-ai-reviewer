from openai import OpenAI
import dotenv
import os

dotenv.load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
def query_llm(file_dict, query):
    """
    Queries a language model to find the most fitting filenames for a given query.

    Args:
        file_dict (dict): A dictionary containing file names as keys and their descriptions as values.
        query (str): A query string to match against the file descriptions.

    Returns:
        list: A list containing the two filenames that best match the query, as determined by the language model.
    """

    files_str = "\n".join([f"{name}: {desc}" for name, desc in file_dict.items()])
    prompt = f"""---FILE DICTIONARY---
    {files_str}
    ---Query---
    {query}"""
    response = client.responses.create(
        model="gpt-4.1-nano",
        instructions="You are a computer that precisely precisely matches files and their description to a query."
        "You will receive a dictionary containing file names and their descriptions." 
        "Based on the query that you receive, you need to output the 2 most fitting filenames. Your output must be strictly the filenames separated by a space.",
        input=prompt)
    
    return [file for file in response.output[0].content[0].text.strip().split(" ")]