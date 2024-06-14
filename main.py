import os
import pyttsx3
import google.generativeai as genai
import speech_recognition as sr

# Initialize text-to-speech engine
engine = pyttsx3.init()

# Configure Google Generative AI
genai.configure(api_key="your_api_key")

generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
)

# Initialize speech recognizer
r = sr.Recognizer()
m = sr.Microphone()


def get_approx_50_words(text):
    words = text.split()
    if len(words) > 50:
        return ' '.join(words[:50]) + '...'
    return text


def recognize_and_respond():
    first_input = True

    try:
        print("A moment of silence, please...")
        with m as source:
            r.adjust_for_ambient_noise(source)
        print("Set minimum energy threshold to {}".format(r.energy_threshold))

        while True:
            if first_input:
                engine.say("Hi, how can I assist you today?")
                first_input = False
            else:
                engine.say("Would you like to ask another question or exit?")

            engine.runAndWait()
            print("Say something!")
            with m as source:
                audio = r.listen(source)
            print("Got it! Now to recognize it...")

            try:
                # Recognize speech using Google Speech Recognition
                value = r.recognize_google(audio)
                print("You said: {}".format(value))

                if value.lower() == "exit":
                    engine.say("Goodbye!")
                    engine.runAndWait()
                    break

                # Generate response using Google Generative AI
                chat_session = model.start_chat(
                    history=[
                        {"role": "user", "parts": [value]},
                    ]
                )
                response = chat_session.send_message(value)
                response_text = response.text

                # Ensure the response contains approximately 50 words
                approx_50_words_response = get_approx_50_words(response_text)
                print("Response: {}".format(approx_50_words_response))

                # Read the response aloud
                engine.say(approx_50_words_response)
                engine.runAndWait()

            except sr.UnknownValueError:
                print("Oops! Didn't catch that")
                engine.say("I didn't catch that. Could you please repeat?")
                engine.runAndWait()
            except sr.RequestError as e:
                print("Uh oh! Couldn't request results from Google Speech Recognition service; {0}".format(e))
                engine.say("There was an error with the speech recognition service.")
                engine.runAndWait()
    except KeyboardInterrupt:
        pass


# Run the function to recognize voice and respond
recognize_and_respond()
