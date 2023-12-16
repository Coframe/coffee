import os
from openai import OpenAI
from agents.approximate_costs import approximate_image_costs
from typing import Literal
import aiohttp
from aiohttp import FormData
import jinja2
import requests
from PIL import Image
from io import BytesIO

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

class LatteAgent:
    """
    Only makes OpenAI calls
    """
    conversation_history: list = []
    cache = {}

    async def generate_latte_art(
      self,
      prompt: str,
      steam_path: str,
      size: Literal["1024x1024", "1792x1024", "1024x1792"] = "1024x1024",
      quality: Literal["hd", "standard"] = "hd",
      transparent: bool = False
    ):
      if transparent:
        prompt = "Use solid single color background (prefer while, black or very toxic green) for the image to enable easy background removal in the future and DO NOT ADD any shadows or reflections to the image and final prompt: " + prompt

      print ("------PROMPT------")
      print (prompt)
      print ("------DREAMING------")

      response = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size=size,
        quality=quality,
        n=1,
        response_format="url"
      )

      image_url = response.data[0].url

      steam_content =  jinja2.Template("""
        "use client";

        import React from "react";

        const Steam: React.FC<{
          steam?: string | any;
        }> = () => {
           return <img src="{{image_url}}" />
        };

        export default Steam;
      """,
        trim_blocks=True,
        lstrip_blocks=True,
        autoescape=False,
      ).render(image_url=image_url)

      with open(steam_path, 'w') as out_file:
        out_file.write(steam_content)

      print ("-------------------")
      cost = approximate_image_costs({"model": "dall-e-3"})
      print (f"Cost: ${round(cost['total_cost'], 4)}")
      return steam_content


    async def remove_bg(self, image_data):
      url = 'https://clipdrop-api.co/remove-background/v1'
      headers = {
        'x-api-key': os.environ.get("CLIPDROP_API_KEY")}
      data = FormData()
      data.add_field('image_file', image_data, filename='input.png', content_type='image/png')

      async with aiohttp.ClientSession() as session:
        async with session.post(url, data=data, headers=headers) as response:
          if response.status == 200:
            processed_image = await response.read()
            return processed_image
          else:
            response.raise_for_status()


    async def save_img(self, img_url, component_name, file_path, mount_dir):
      response = requests.get(img_url)
      img = Image.open(BytesIO(response.content))
      image_file_path = os.path.join(
          os.path.dirname(file_path), mount_dir, component_name
      )
      img.save(f'{image_file_path}.png', 'PNG')
      return img
