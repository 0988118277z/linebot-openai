# py -m pip install openai

# set OPENAI_API_KEY=YOUR_API_KEY_HERE
# python chatbot.py

# export OPENAI_API_KEY=YOUR_API_KEY_HERE
# python chatbot.py

api_key = 'api_key'
def txt_to_img_openai(input_text):
    from openai import OpenAI

    client = OpenAI(api_key=api_key)
    # 接下來使用 client 來呼叫 OpenAI 的功能

    response = client.images.generate(
      model="dall-e-3",
      prompt=input_text,
      size="1024x1024",
      quality="standard",
      n=1,
    )

    image_url = response.data[0].url

    return image_url

def img_to_img_openai(img_file):
    from openai import OpenAI
    from PIL import Image as PILImage
    import requests
    from io import BytesIO

    client = OpenAI(api_key=api_key)
    # 接下來使用 client 來呼叫 OpenAI 的功能

    original_image = PILImage.open(img_file)
    new_size = (1024, 1024)
    resized_image = original_image.resize(new_size)

    resized_image_stream = BytesIO()  #將圖片存在記憶體
    resized_image.save(resized_image_stream, format='PNG')

    resized_image_bytes = resized_image_stream.getvalue()

    response = client.images.create_variation(
        image=resized_image_bytes,
        n=1,
        size="1024x1024"
    )
    image_url = response.data[0].url
    return image_url

def txt_to_txt_openai(input_text): 
    from openai import OpenAI
    
    
    client = OpenAI(api_key=api_key)

    stream = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": input_text}],
        stream=True,
    )
    for chunk in stream:
        if chunk.choices[0].delta.content is not None:
            print(chunk.choices[0].delta.content, end="")
    

