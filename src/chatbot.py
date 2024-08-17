import chainlit as cl
import traceback
from chainlit.input_widget import Select
from utils.service_calls import ask_stable_diffusion
import asyncio


# Initializes the chat session with avatars and a welcome message, and presents the user with chat settings options.
@cl.on_chat_start
async def on_chat_start():
    try:
        await cl.Message(content=f"Hello, welcome to Image Generation Chatbot! How can I help you?",
                         author="My Assistant").send()
        settings = await cl.ChatSettings(
            [
                Select(id="generation_model",
                       label="Select the generation model",
                       values=["Runway Stable Diffusion v1.5",
                               "Stabilityai Stable Diffusion x1 base 1.0"])
            ]
        ).send()
        cl.user_session.set("generation_model", settings["generation_model"])
    except BaseException as e:
        print(f"Caught error on on_chat_start in app.py: {e}")
        traceback.print_exc()


# Updates the agent's settings based on user preferences.
@cl.on_settings_update
async def setup_agent(settings):
    try:
        user_message = ""
        cl.user_session.set("generation_model", settings["generation_model"])
        if cl.user_session.get("generation_model") is not None:
            user_message += f"{settings['generation_model']} is activated."
        await cl.Message(user_message, author="My Assistant").send()

    except Exception as e:
        await cl.Message("An unexpected error occurred when retrieving the previous sessions. We are looking into it.").send()


# Processes incoming user messages, generates relevant image using the specified models,
# and responds with a generated image.
@cl.on_message
async def on_message(message: cl.Message):
    try:
        # Send a loading message
        loading_message = await cl.Message(
            content="Generating images, please wait...",
            author="My Assistant"
        ).send()

        model_name = cl.user_session.get("generation_model") or "Stabilityai Stable Diffusion x1 base 1.0"
        print(f"Generation model: {model_name}\n")

        # Generate images asynchronously
        image_paths = await ask_stable_diffusion(message.content, model_name)
        print(image_paths)
        images = [cl.Image(path=path, name=f"image{i+1}", display="inline") for i, path in enumerate(image_paths)]

        await loading_message.remove()

        if images:
            # Update the content of the loading message or send a new message with images
            await cl.Message(
                content="Here are images for your prompt!",
                elements=images,
                author="My Assistant"
            ).send()
        else:
            await cl.Message("Failed to generate images. Please try again.", author="My Assistant").send()

    except BaseException as e:
        print(f"Caught error on on_message in app.py: {e}")
        traceback.print_exc()
        await cl.Message("An error occurred while processing your query. Please try again later.").send()
