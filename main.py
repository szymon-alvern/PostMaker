from fastapi import FastAPI
import uvicorn


app = FastAPI()


@app.get("/")
def welcome():
    return {"message": "My name is PostMaker",
             "version": "1.0.0",
             "author": "Szymon Suchodolski"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8003)