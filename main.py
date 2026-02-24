from fastapi import FastAPI
import uvicorn
from utils import post_description_generation, PostRequest, PostResponse, TopicRequest, RepostRequest, EventsData
from utils import clear_events_date


app = FastAPI()


@app.get("/")
def welcome():
    return {"message": "My name is PostMaker",
             "version": "1.0.0",
             "author": "Szymon Suchodolski"}


@app.post("/generate-post", response_model=PostResponse)
async def generate_post(request: PostRequest):
    post_description = await post_description_generation(company_description=request.company_description, task="post", media=request.media, topic=request.topic)
    return post_description


@app.post("/repost", response_model=PostResponse)
async def repost(request: RepostRequest):
    repost_description = await post_description_generation(company_description=request.company_description, task="repost", media=request.media, 
    post_description=request.post_description, post_comment=request.post_comment, topic=request.topic)
    return repost_description


@app.post("/generate-topic", response_model=PostResponse)
async def generate_topic(request: TopicRequest):
    topic = await post_description_generation(company_description=request.company_description, task="topic", media=request.media, topic_list=request.topic_list)
    return topic


@app.post("/available/events")
async def available_events(request: EventsData):
    events = clear_events_date(request.events_list)
    request_post = await post_description_generation(task="availability_events", media=request.media, events=events, oryginal_post=request.oryginal_post)
    return request_post



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8003)