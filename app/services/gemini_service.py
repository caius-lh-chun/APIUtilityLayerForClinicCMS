import pandas as pd
from pathlib import Path
from google import genai
from google.genai import types

from dotenv import load_dotenv
import time
import os


try:
    from dotenv import load_dotenv

    base_dir = Path(__file__).resolve().parent.parent
    load_dotenv(dotenv_path=base_dir / ".env")  # Works locally, no error if .env missing

except ImportError:
    pass  # dotenv not installed in prod or not needed


api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)


## TODO: model name selection in params
def invoking_gemini(
                    path_to_image, prompt, max_retries=10, retry_count=0, model = "gemini-2.5-flash"):
    
    # client = self.client

    try:
        start_time = time.time()  # record start time

        if path_to_image is not None:
            myfile = client.files.upload(file=path_to_image)
            contents = [myfile, "\n\n", prompt]
        else:
            contents = ["\n\n", prompt]

        result = client.models.generate_content(
            # model="gemini-2.5-pro",
            model = model,
            contents=contents,
            config=types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(thinking_budget=1536),
                response_mime_type="application/json"
            )
            # {"response_mime_type": "application/json"}
        )
        end_time = time.time()  # record end time
        duration = end_time - start_time
        print(f"This successful call to LLM took {duration:.4f} seconds")

        return result.text

    except genai.errors.APIError as e:
        if hasattr(e, "code") and e.code in [429, 500, 502, 503]:
            print(f"retrying for {retry_count}")
            end_time = time.time()  # record end time
            duration = end_time - start_time
            print(f"This unsuccessful call to LLM took {duration:.4f} seconds")
            if retry_count < max_retries:
                # wait_time = 2 ** retry_count  # exponential backoff: 1s, 2s, 4s, ...
                # time.sleep(wait_time)
                return invoking_gemini(path_to_image, prompt, max_retries, retry_count + 1)
            else:
                print(f"Max retries reached ({max_retries}). Raising exception.")
                raise
        else:
            raise