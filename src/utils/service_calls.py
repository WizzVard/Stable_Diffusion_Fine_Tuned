from utils.load_config import LoadConfig
from random import randint
import os
import aiohttp
import asyncio

CONFIG = LoadConfig()

image_index = 1


async def fetch_image(session, url, path_to_save_directory):
    """
    Asynchronously fetch an image from the given URL and save it to the specified directory.

    :param session: The aiohttp session to use for making requests.
    :param url: The URL to fetch the image from.
    :param path_to_save_directory: The directory where the image will be saved.
    :return: The path to the saved image or None if the request failed.
    """
    try:
        async with session.get(url) as img_response:
            if img_response.status == 200:
                image_data = await img_response.read()
                path_to_save = os.path.join(path_to_save_directory, f"image{randint(1, 100000)}.jpg")
                with open(path_to_save, 'wb') as f:
                    f.write(image_data)
                print(f"Image saved as {path_to_save}")
                return path_to_save
            else:
                print(f"Failed to load image from {url}")
                return None
    except Exception as e:
        print(f"Error fetching image from {url}: {e}")
        return None


async def ask_stable_diffusion(message: str, model_name: str):
    """
    Asynchronously send a POST request to the /generate_image endpoint of the FastAPI Server
    to generate an image based on the given prompt.

    :param message: The prompt message.
    :param model_name: The model name.
    :return: A list of paths where images are saved.
    """
    try:
        data = {'prompt': message, 'model': model_name}
        fastapi_endpoint = f"{CONFIG.fastapi_endpoint}/generate_image"
        path_to_save_directory = CONFIG.data_directory

        # Ensure directory exists
        os.makedirs(CONFIG.data_directory, exist_ok=True)

        async with aiohttp.ClientSession() as session:
            async with session.post(fastapi_endpoint, json=data) as response:
                if response.status == 200:
                    response_data = await response.json()
                    image_paths = response_data.get("images", [])

                    tasks = [
                        fetch_image(session, f"{CONFIG.fastapi_endpoint}/{image_path}", path_to_save_directory)
                        for image_path in image_paths
                    ]
                    saved_paths = await asyncio.gather(*tasks)
                    saved_paths = [path for path in saved_paths if path is not None]

                    return saved_paths
                else:
                    error_message = await response.text()
                    print("Error:", error_message)
                    return "No path"

    except Exception as e:
        print("Error sending message:", e)
        return "No path"
