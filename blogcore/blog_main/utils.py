import requests
from django.conf import settings
from django.shortcuts import redirect

def generate_summary(text):
    if not text or len(text) < 100:
        return text

    API_URL = "https://router.huggingface.co/hf-inference/models/facebook/bart-large-cnn"

    headers = {
        "Authorization": f"Bearer {settings.HF_API_KEY}"
    }

    response = requests.post(
        API_URL,
        headers=headers,
        json={"inputs": text}
    )

    result = response.json()
    print(result)
    return result[0]["summary_text"]



def is_abusive(text):
    API_URL = "https://router.huggingface.co/hf-inference/models/unitary/toxic-bert"

    headers = {
        "Authorization": f"Bearer {settings.HF_API_KEY}"
    }

    response = requests.post(
        API_URL,
        headers=headers,
        json={"inputs": text},
        timeout=20
    )

    result = response.json()

    # Safety check
    if not isinstance(result, list):
        print("HF ERROR:", result)
        return False

    predictions = result[0]

    for item in predictions:
        if item["label"] == "toxic" and item["score"] > 0.7:
            return True

    return False


def unauthorized_user(view_func):
    def wrapper(request,*args, **kwargs):
        if request.user.is_authenticated:
            return redirect('profile')
        return view_func(request,*args,**kwargs)
    return wrapper
 