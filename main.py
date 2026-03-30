from fastapi import FastAPI
import uvicorn
from utils import post_description_generation, PostRequest, PostResponse, TopicRequest, RepostRequest, EventsDate, MeetingDate, DateList
from utils import clear_events_date, checking_date


app = FastAPI()


@app.get("/")
def welcome():
    return {"message": "My name is PostMaker-test",
             "version": "1.0.0",
             "author": "Szymon Suchodolski"}


@app.post("/generate-post", response_model=PostResponse)
async def generate_post(request: PostRequest):
    post_description = await post_description_generation(company=request.company, task="post", media=request.media, topic=request.topic)
    return post_description


@app.post("/write-post", response_model=PostResponse)
async def write_post(request: RepostRequest):
    repost_description = await post_description_generation(company=request.company, task="repost", media=request.media, 
    post_description=request.post_description, post_comment=request.post_comment, topic=request.topic)
    return repost_description


@app.post("/generate-topic", response_model=PostResponse)
async def generate_topic(request: TopicRequest):
    topic = await post_description_generation(task="topic",company=request.company, media=request.media, topic_list=request.topic_list)
    return topic


@app.post("/available/events")
async def available_events(request: EventsDate):
    events = clear_events_date(request.events_list)
    request_post = await post_description_generation(task="availability_events", media=request.media, events=request.events_list, current_post=request.current_post, conversation_context=request.conversation_context)
    return request_post

@app.post("/available/meeting")
async def available_meeting(request: MeetingDate):
    request_post = await post_description_generation(task="availability_meeting", media=request.media, meeting_date_list=request.meeting_date_list, current_post=request.current_post, conversation_context=request.conversation_context)
    return request_post


@app.post("/checking")
async def checking(request:DateList):
    response = checking_date(request.date_list)
    return {"message": response}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8003)