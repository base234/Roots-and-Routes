import os
from openai import OpenAI
from src.utils.config import OPENAI_API_KEY, OPENAI_MODEL

OpenAIClient = OpenAI(api_key=OPENAI_API_KEY)

def generate_site_story(site):
    """
    Generate a compelling story about a heritage site using OpenAI's GPT model.

    Args:
        site (dict): Dictionary containing site details

    Returns:
        str: Generated story about the site
    """
    try:
        # Construct the prompt
        prompt = f"""Write a compelling and informative story about {site['name']},
        a {site['type']} located in {site['location']}, {site['state']}.
        Built in {site['year_built']}, it is {site['description']}.
        Its UNESCO status is {'a UNESCO World Heritage Site' if site['unesco_status'] else 'not a UNESCO site'}.
        Write a narrative that:
        1. The story behind the site.
        2. Describes the historical significance
        3. Highlights unique architectural or cultural features
        4. Explains its importance to local heritage
        5. Includes interesting facts
        6. Its current state

        Give each section a title. If need to use a colon in titles, instead use dash. The formatting of the titles should be in h4 size. Make it engaging and informative for visitors. Use simple language and avoid using complex words.
        """

        # Call OpenAI API
        response = OpenAIClient.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "You are a knowledgeable heritage site storyteller who creates engaging narratives about historical places. It must not be more than 550 words."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            stream=True
        )

        # Extract and return the generated story
        # return response.choices[0].message.content

        for chunk in response:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    except Exception as e:
        # Return a fallback message if the API call fails
        return f"""Welcome to {site['name']}, a remarkable {site['type']} located in {site['location']}, {site['state']}.
        Built in {site['year_built']}, this site is {site['description']}.
        It is {'a UNESCO World Heritage Site' if site['unesco_status'] else 'not a UNESCO site'}.xddgdfgd"""

def generate_user_custom_site_story(site, user_input):
    """
    Generate a compelling story about a heritage site using OpenAI's GPT model.

    Args:
        site (dict): Dictionary containing site details

    Returns:
        str: Generated story about the site
    """
    try:
        # Construct the prompt
        prompt = f"""Write a compelling and informative story about {site['name']},
        a {site['type']} located in {site['location']}, {site['state']}.
        Built in {site['year_built']}, it is {site['description']}.
        Its UNESCO status is {'a UNESCO World Heritage Site' if site['unesco_status'] else 'not a UNESCO site'}.
        Write a narrative that:
        1. The story behind the site.
        2. Describes the historical significance
        3. Highlights unique architectural or cultural features
        4. Explains its importance to local heritage
        5. Includes interesting facts
        6. Its current state

        Give each section a title. Use dash instead of colon(:). The formatting of the titles should be in h4 size. Make it engaging and informative for visitors. Use simple language and avoid using complex words.

        The user has shared the following input about this site: {user_input}
        Incorporate the user's input in the story where relevant.
        """

        # Call OpenAI API
        response = OpenAIClient.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "You are a knowledgeable heritage site storyteller who creates engaging narratives about historical places. It must not be more than 550 words."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            stream=True
        )

        # Extract and return the generated story
        # return response.choices[0].message.content

        for chunk in response:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    except Exception as e:
        # Return a fallback message if the API call fails
        return f"""Welcome to {site['name']}, a remarkable {site['type']} located in {site['location']}, {site['state']}.
        Built in {site['year_built']}, this site is {site['description']}.
        It is {'a UNESCO World Heritage Site' if site['unesco_status'] else 'not a UNESCO site'}.xddgdfgd"""
