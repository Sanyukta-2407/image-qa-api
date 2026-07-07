from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from openai import OpenAI

import os
import base64

load_dotenv()

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url="https://aipipe.org/openrouter/v1"
)


class ImageRequest(BaseModel):
    image_base64: str
    question: str


@app.get("/")
def home():
    return {"status": "running"}


@app.post("/answer-image")
def answer_image(req: ImageRequest):

    image_data = req.image_base64

    # Remove data URL prefix if present
    if image_data.startswith("data:image"):
        image_data = image_data.split(",", 1)[1]

    image_url = f"data:image/png;base64,{image_data}"

    response = client.chat.completions.create(
        model="openai/gpt-4.1-mini",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            req.question
                            + "\nReturn ONLY the answer. "
                            + "If it is numeric, return only the number. "
                            + "Do not include units or extra words."
                        ),
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": image_url
                        },
                    },
                ],
            }
        ],
    )

    answer = response.choices[0].message.content.strip()

    return {
        "answer": str(answer)
    }