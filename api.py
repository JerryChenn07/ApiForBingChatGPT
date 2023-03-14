import argparse
import json
import logging

from fastapi import FastAPI, Request

import utils
from chatbot import Chatbot
from get_auth import get_auth

logging.basicConfig(filename="logs.txt",
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.INFO)

parser = argparse.ArgumentParser()
parser.add_argument("cookies_U", help="The cookie for authentication.")
args = parser.parse_args()

logging.info(args.cookies_U)

app = FastAPI()


@app.post("/create_conversation")
def create_conversation(request: Request):
    request_body = json.loads(await request.body())
    userId = request_body["userId"]
    if userId not in utils.get_whitelist_users():
        return "You are not allowed to use this feature."  # 还没通过候补

    logging.info(f"User {userId} is creating conversation.")
    cookies = {"_U": args.cookies_U}
    status, text = await get_auth(cookies)
    if status != 200:
        raise Exception(f"Authentication failedstatus={status} text={text}")
    try:
        ConversationAPIResponseBody = json.loads(text)
        response = {
            "conversationId": ConversationAPIResponseBody["conversationId"],
            "clientId": ConversationAPIResponseBody["clientId"],
            "conversationSignature": ConversationAPIResponseBody["conversationSignature"],
            "invocationId": 0
        }
        logging.info(response)
        return response
    except json.decoder.JSONDecodeError as ex:
        raise Exception(
            "Authentication failed. You have not been accepted into the beta.",
        ) from ex


@app.post("/chatgpt")
async def chatgpt_reply(request: Request):
    # initialize the chatbot and connect to the websocket each time.
    bot = Chatbot()
    await bot.chat_hub.connect()
    request_body = json.loads(await request.body())
    prompt = request_body["prompt"]
    conversationId = request_body["conversationId"]
    clientId = request_body["clientId"]
    conversationSignature = request_body["conversationSignature"]
    invocationId = request_body["invocationId"]

    response = await bot.ask(
        prompt=prompt,
        conversationId=conversationId,
        clientId=clientId,
        conversationSignature=conversationSignature,
        invocationId=invocationId)
    conversation_id = response["item"]["conversationId"]
    conversation_message = response["item"]["messages"][1]["adaptiveCards"][0]["body"][0]["text"]
    logging.info(
        f"ConversationId: {conversation_id}\nInvocationId: {invocationId}\nPrompt: {prompt}\nMessage: {conversation_message}")
    return {"conversationId": conversation_id, "message": conversation_message, "invocationId": invocationId + 1}


if __name__ == '__main__':
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, workers=args.cookies_U)
