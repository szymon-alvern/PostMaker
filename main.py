from fastapi import FastAPI
import uvicorn
from utils import post_description_generation, CompanyDescriptionRequest


app = FastAPI()


@app.get("/")
def welcome():
    return {"message": "My name is PostMaker",
             "version": "1.0.0",
             "author": "Szymon Suchodolski"}


@app.post("/generate-post")
async def generate_post(request: CompanyDescriptionRequest):
    post_description = await post_description_generation(request.company_description, request.topic, request.media)
    return {"post_description": post_description}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8003)