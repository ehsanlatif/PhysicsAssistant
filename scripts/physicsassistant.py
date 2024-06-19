import openai
import requests
import base64
from datetime import datetime
import json
import speech_recognition as sr
import pyttsx3
import objc
import tkinter as tk
from PIL import Image, ImageTk, ImageSequence # For animated GIFs
import cv2
import threading
import time



openai.api_key = 'Use your API here'
api_key = 'Use your API here'


conversation_history = []


def encode_image_by_path(image_path):
    """
    Encodes an image file to a base64 string.
    
    Args:
    - image_path (str): Path to the image file.
    
    Returns:
    - str: The base64 encoded string of the image.
    """
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def encode_image(image):
    """
    Encodes an image to base64.

    Args:
    - image (numpy.ndarray): Image array.

    Returns:
    - str: Base64 encoded image.
    """
    _, buffer = cv2.imencode('.jpg', image)
    return base64.b64encode(buffer).decode('utf-8')

def extract_frames(video_path, num_frames=10):
    """
    Extracts frames from a video file.

    Args:
    - video_path (str): Path to the video file.
    - num_frames (int): Number of frames to extract.

    Returns:
    - list: List of base64 encoded images.
    """
    cap = cv2.VideoCapture(video_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frames = []

    for i in range(num_frames):
        frame_id = int((i / num_frames) * total_frames)
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_id)
        ret, frame = cap.read()
        if ret:
            encoded_frame = encode_image(frame)
            frames.append(encoded_frame)
        else:
            break

    cap.release()
    return frames

def ask_chatgpt(question, session_id, image_path=None,video_path=None):
    """
    Modified function to handle both text questions and images.
    
    Args:
    - question (str): The question asked by the student.
    - session_id (str): A unique identifier for the conversation/session.
    - image_path (str, optional): Path to an image file for analysis.
    
    Returns:
    - str: The answer from ChatGPT.
    """
    global conversation_history

    # Headers for the OpenAI API request
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    # Prepare the payload with the question. If an image is provided, encode it and include in the payload
    if image_path:
        base64_image = encode_image_by_path(image_path)
        payload = {
            "model": "gpt-4o",
            "messages": [
                {"role": "system", "content": "You are a physics lab assistant. Your task is to respond to the user question in two sentences and to the point. Do not include markdown in your response"},
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": question
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            "max_tokens": 300
        }
    elif video_path:
        base64Frames = extract_frames(video_path)
        payload = {
            "model": "gpt-4o",
            "messages": [
                {"role": "system", "content": "You are a physics lab assistant. Your task is to respond to the user question in two sentences and to the point. Do not include markdown in your response."},
                {
                    "role": "user",
                    "content": [
                        "These are the frames from the video recorded at 10 frames per second",
                        {
                            "type": "text",
                            "text": question
                        },
                        *map(lambda x: {"type": "image_url", 
                        "image_url": {"url": f'data:image/jpg;base64,{x}', "detail": "low"}}, base64Frames)
                    ]
                }
            ],
            "max_tokens": 300
        }
    else:
        print(question)
        # Fallback to text-only processing if no image is provided
        payload = {
            "model": "gpt-4o",  # Adjust as necessary
            "messages": [
                {"role": "system", "content": "You are a physics lab assistant. Your task is to respond to the user question in two sentences and to the point. Distance should always be positive. Do not include markdown in your response."},
                {"role": "user", "content": question}
            ],
            "max_tokens": 300  # Adjust as necessary
        }
    # Sending request to the OpenAI API
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    print(response)

    if response.status_code == 200:
        # Extract and return the answer
        answer_data = response.json()
        answer = answer_data['choices'][0]['message']['content'] if 'choices' in answer_data else "I couldn't get a response."
    else:
        answer = "There was an error processing your request."

    # Update conversation history (simplified for this example)
    conversation_history.append({"session_id": session_id, "timestamp": datetime.now(), "type": "interaction", "content": question + " | " + answer})
    
    return answer

### Typing on Terminal
# def main():
#     """
#     Main function to start the chat bot and handle student questions.
#     """
#     print("Welcome to the Physics Lab Assistant. Ask me any physics-related question!")
    
#     session_id = str(datetime.now()) # Generate a unique session ID based on the current timestamp
    
#     while True:
#         question = input("What's your question? (Type 'exit' to quit): ")
#         image_path = None
#         if question.lower() == 'exit':
#             break
#         if "attached image" in question.lower():
#              image_path = input("Provide Image Path (image should be in the same folder): ")
        
#         answer = ask_chatgpt(question, session_id,image_path)
#         print("Answer:", answer)


### Speaking and Listening Without GUI
# def main():
#     """
#     Main function to start the chat bot and handle student questions.
#     """
#     recognizer = sr.Recognizer()
#     microphone = sr.Microphone()
#     try:
#         engine = pyttsx3.init("nsss")
#     except Exception as e:
#         print(f"Error initializing pyttsx3: {e}")
#         return

#     welcome_phrase = "Hello! I am your Physics Assistant. Ask me any physics-related question!"
#     continue_Phrase = "How may I help you for further assistance."
#     thinking_phrase = "hmm.. Let me think about it..."
#     audio_error_phrase = "Sorry, I could not understand the audio."+continue_Phrase

#     print(welcome_phrase)
#     engine.say(welcome_phrase)
#     engine.runAndWait()
    
#     session_id = str(datetime.now()) # Generate a unique session ID based on the current timestamp
    
#     while True:
#         try:
#             with microphone as source:
#                 recognizer.adjust_for_ambient_noise(source)
#                 audio = recognizer.listen(source,timeout=5, phrase_time_limit=20)
#                 question = recognizer.recognize_google(audio)
#                 print("You said:", question)
                
#                 if question.lower() == 'exit':
#                     break
                
#                 # image_path = None
#                 # if "attached image" in question.lower():
#                 print(thinking_phrase)
#                 engine.say(thinking_phrase)
#                 engine.runAndWait()
#                 image_path = "img3.png"#input("Provide Image Path (image should be in the same folder): ")
                
#                 answer = ask_chatgpt(question, session_id, image_path)
#                 print("Answer:", answer)
#                 engine.say(answer)
#                 engine.runAndWait()
#                 print(continue_Phrase)
#                 engine.say(continue_Phrase)
#                 engine.runAndWait()
                
#         except sr.UnknownValueError:
#             print(audio_error_phrase)
#             engine.say(audio_error_phrase)
#             engine.runAndWait()
#         except sr.RequestError as e:
#             print(f"Could not request results; {e}")
#             engine.say("Could not request results.")
#             engine.runAndWait()

### GIF GUI
# def main():
#     # ... (GUI setup - same as before)

#     # Animated GIF Labels
#     def animate_gif(label, gif_path):
#         frames = [ImageTk.PhotoImage(frame) for frame in ImageSequence.Iterator(Image.open(gif_path))]
#         def update(ind):
#             frame = frames[ind]
#             ind += 1
#             if ind == len(frames):
#                 ind = 0
#             label.configure(image=frame)
#             window.after(100, update, ind)  # Adjust 100 for animation speed
#         label.after(0, update, 0)

#     listening_label = tk.Label(window)
#     listening_label.pack(pady=20)
#     animate_gif(listening_label, "listening_face.gif")  # Replace with your GIF path

#     speaking_label = tk.Label(window)
#     speaking_label.pack(pady=20)
#     animate_gif(speaking_label, "speaking_face.gif")  

#     # ... (rest of the GUI elements and logic - same as before)

#     def listen_and_respond():
#         try:
#             with microphone as source:
#                 listening_label.pack() # Show listening animation
#                 speaking_label.pack_forget() # Hide speaking animation
#                 # ... (rest of the listening logic - same as before)
#         finally:
#             listening_label.pack_forget()
#             speaking_label.pack()
#     # ... (rest of the code - same as before)

# With Image GUI
def main():
    # GUI Setup
    window = tk.Tk()
    window.title("Physics Assistant")

    # Image Labels
    listening_img = ImageTk.PhotoImage(Image.open("images/listening_emoji.jpeg"))  # Replace with your image paths
    speaking_img = ImageTk.PhotoImage(Image.open("images/speaking_emoji.jpeg"))
    thinking_img = ImageTk.PhotoImage(Image.open("images/thinking_emoji.jpeg"))
    image_label = tk.Label(window, image=listening_img)
    image_label.pack(pady=20)

    # Text Area
    text_area = tk.Text(window, wrap=tk.WORD, width=50, height=10)
    text_area.pack(pady=10)
    text_area.insert(tk.END, "Hello! I am your Physics Assistant. Ask me any physics-related question!\n")

    # Speech Recognition & Text-to-Speech
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()
    engine = pyttsx3.init("nsss")

    welcome_phrase = "Hello! I am your Physics Assistant. Ask me any physics-related question!"
    continue_Phrase = "How may I help you for further assistance."
    thinking_phrase = "hmmm.. Let me think about it..."
    audio_error_phrase = "Sorry, I could not understand the audio."+continue_Phrase
    session_id = str(datetime.now())
    def listen_and_respond():
        try:
            with microphone as source:
                image_label.config(image=listening_img)  # Show listening face
                window.update()  # Update the GUI to display the change
                recognizer.adjust_for_ambient_noise(source)
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=20)
                question = recognizer.recognize_google(audio)
                text_area.insert(tk.END, f"You said: {question}\n")
                text_area.see(tk.END)

                if question.lower() == "exit":
                    window.destroy()  # Close the GUI window
                    return

                image_label.config(image=thinking_img)  # Show speaking face
                window.update()

                text_area.insert(tk.END, thinking_phrase + "\n")
                text_area.see(tk.END)
                engine.say(thinking_phrase)
                engine.runAndWait()

                image_path = "images/img3.png"#input("Provide Image Path (image should be in the same folder): ")
                # image_path = capture_image()

                answer = ask_chatgpt(question, session_id, image_path)

                text_area.insert(tk.END, f"PhysicsAssistant: {answer}\n")
                image_label.config(image=speaking_img)  # Show speaking face
                window.update()
                engine.say(answer)
                engine.runAndWait()

                text_area.insert(tk.END, continue_Phrase + "\n")
                text_area.see(tk.END)
                engine.say(continue_Phrase)
                engine.runAndWait()

        except sr.UnknownValueError:
            print(audio_error_phrase)
            engine.say(audio_error_phrase)
            engine.runAndWait()
        except sr.RequestError as e:
            print(f"Could not request results; {e}")
            engine.say("Could not request results.")
            engine.runAndWait()
        finally:
            image_label.config(image=listening_img)  # Reset to listening face
            window.update()

    # Button
    # print(welcome_phrase)
    listen_button = tk.Button(window, text="Speak", command=listen_and_respond)
    listen_button.pack()

    image_label.config(image=speaking_img)  # Show listening face
    window.update()
    engine.say(welcome_phrase)
    engine.runAndWait()  
    window.mainloop()# Start the GUI event loop

# \begin{enumerate}
#     \item What is the horizontal distance traveled by the right ball?
#     \item What is the vertical distance traveled by the right ball?
#     \item Why do both balls have the same vertical distance but different horizontal distances?
#     \item What is the horizontal distance traveled by the right ball when it hits the ground?
#     \item If the left ball has less weight, will both balls hit the ground simultaneously?
# \end{enumerate}



## With Live Camera Feed

# def capture_image():
#     cap = cv2.VideoCapture(1)
#     if not cap.isOpened():
#         print("Error: Could not open video device.")
#         return None

#     ret, frame = cap.read()
#     if ret:
#         image_path = "captured_image.jpg"
#         cv2.imwrite(image_path, frame)
#         cap.release()
#         return image_path
#     cap.release()
#     return None

# def show_camera_feed(label):
#     cap = cv2.VideoCapture(0)
#     if not cap.isOpened():
#         print("Error: Could not open video device.")
#         return

#     def update_frame():
#         ret, frame = cap.read()
#         if ret:
#             # Resize the frame
#             frame = cv2.resize(frame, (720, 480))
#             cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#             img = Image.fromarray(cv2image)
#             imgtk = ImageTk.PhotoImage(image=img)
#             label.imgtk = imgtk
#             label.configure(image=imgtk)
#         label.after(50, update_frame)

#     update_frame()

# def main():
#     # GUI Setup
#     window = tk.Tk()
#     window.title("Physics Assistant")

#     camera_label = tk.Label(window)
#     camera_label.pack(pady=10)
#     # Image Labels
#     listening_img = ImageTk.PhotoImage(Image.open("images/listening_emoji.jpeg").resize((50, 50)))  # Resize image
#     speaking_img = ImageTk.PhotoImage(Image.open("images/speaking_emoji.jpeg").resize((50, 50)))
#     thinking_img = ImageTk.PhotoImage(Image.open("images/thinking_emoji.jpeg").resize((50, 50)))
#     image_label = tk.Label(window, image=listening_img)
#     image_label.pack(pady=10)

#     # Camera Feed


#     # Text Area
#     text_area = tk.Text(window, wrap=tk.WORD, width=50, height=10)
#     text_area.pack(pady=10)
#     text_area.insert(tk.END, "Hello! I am your Physics Assistant. Ask me any physics-related question!\n")

#     # Speech Recognition & Text-to-Speech
#     recognizer = sr.Recognizer()
#     microphone = sr.Microphone()
#     engine = pyttsx3.init("nsss")

#     welcome_phrase = "Hello! I am your Physics Assistant. Ask me any physics-related question!"
#     continue_Phrase = "How may I help you for further assistance."
#     thinking_phrase = "hmmm.. Let me think about it..."
#     audio_error_phrase = "Sorry, I could not understand the audio." + continue_Phrase
#     session_id = str(datetime.now())

#     def listen_and_respond():
#         try:
#             with microphone as source:
#                 image_label.config(image=listening_img)  # Show listening face
#                 window.update()  # Update the GUI to display the change
#                 recognizer.adjust_for_ambient_noise(source)
#                 audio = recognizer.listen(source, timeout=5, phrase_time_limit=20)
#                 question = recognizer.recognize_google(audio)
#                 text_area.insert(tk.END, f"You said: {question}\n")
#                 text_area.see(tk.END)

#                 if question.lower() == "exit":
#                     window.destroy()  # Close the GUI window
#                     return

#                 image_label.config(image=thinking_img)  # Show thinking face
#                 window.update()

#                 text_area.insert(tk.END, thinking_phrase + "\n")
#                 text_area.see(tk.END)
#                 engine.say(thinking_phrase)
#                 engine.runAndWait()

#                 # Capture image from live feed
#                 image_path = capture_image()
#                 if image_path:
#                     answer = ask_chatgpt(question, session_id, image_path)

#                     text_area.insert(tk.END, f"PhysicsAssistant: {answer}\n")
#                     image_label.config(image=speaking_img)  # Show speaking face
#                     window.update()
#                     engine.say(answer)
#                     engine.runAndWait()
#                 else:
#                     text_area.insert(tk.END, "Error: Unable to capture image.\n")
#                     engine.say("Error: Unable to capture image.")
#                     engine.runAndWait()

#                 text_area.insert(tk.END, continue_Phrase + "\n")
#                 text_area.see(tk.END)
#                 engine.say(continue_Phrase)
#                 engine.runAndWait()

#         except sr.UnknownValueError:
#             text_area.insert(tk.END, audio_error_phrase + "\n")
#             engine.say(audio_error_phrase)
#             engine.runAndWait()
#         except sr.RequestError as e:
#             error_message = f"Could not request results; {e}"
#             text_area.insert(tk.END, error_message + "\n")
#             engine.say("Could not request results.")
#             engine.runAndWait()
#         finally:
#             image_label.config(image=listening_img)  # Reset to listening face
#             window.update()


#     # Button
#     listen_button = tk.Button(window, text="Speak", command=listen_and_respond)
#     listen_button.pack()

#     image_label.config(image=speaking_img)  # Show speaking face
#     window.update()
#     engine.say(welcome_phrase)
#     engine.runAndWait()

#     threading.Thread(target=show_camera_feed, args=(camera_label,)).start()

#     # Start camera feed

#     window.mainloop()  # Start the GUI event loop

#### With live video feed
# class VideoRecorder:
#     def __init__(self, max_seconds=5, fps=10):
#         self.max_seconds = max_seconds
#         self.fps = fps
#         self.frames = []
#         self.recording = False

#     def start_recording(self):
#         self.recording = True
#         self.frames = []
#         threading.Thread(target=self.record).start()

#     def stop_recording(self):
#         self.recording = False

#     def record(self):
#         cap = cv2.VideoCapture(1)
#         while self.recording:
#             ret, frame = cap.read()
#             if ret:
#                 self.frames.append(frame)
#                 if len(self.frames) > self.max_seconds * self.fps:
#                     self.frames.pop(0)
#             time.sleep(1 / self.fps)
#         cap.release()

#     def save_video(self, path):
#         if not self.frames:
#             print("No frames to save.")
#             return None

#         fourcc = cv2.VideoWriter_fourcc(*'XVID')
#         height, width, _ = self.frames[0].shape
#         out = cv2.VideoWriter(path, fourcc, self.fps, (width, height))

#         for frame in self.frames:
#             out.write(frame)

#         out.release()
#         return path

# def show_camera_feed(label):
#     cap = cv2.VideoCapture(1)
#     if not cap.isOpened():
#         print("Error: Could not open video device.")
#         return

#     def update_frame():
#         ret, frame = cap.read()
#         if ret:
#             frame = cv2.resize(frame, (320, 240))
#             cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#             img = Image.fromarray(cv2image)
#             imgtk = ImageTk.PhotoImage(image=img)
#             label.imgtk = imgtk
#             label.configure(image=imgtk)
#         label.after(10, update_frame)

#     update_frame()

# def main():
#     # GUI Setup
#     window = tk.Tk()
#     window.title("Physics Assistant")

#     # Image Labels
#     listening_img = ImageTk.PhotoImage(Image.open("images/listening_emoji.jpeg").resize((50, 50)))  # Resize image
#     speaking_img = ImageTk.PhotoImage(Image.open("images/speaking_emoji.jpeg").resize((50, 50)))
#     thinking_img = ImageTk.PhotoImage(Image.open("images/thinking_emoji.jpeg").resize((50, 50)))
#     image_label = tk.Label(window, image=listening_img)
#     image_label.pack(pady=10)

#     # Camera Feed
#     camera_label = tk.Label(window)
#     camera_label.pack(pady=10)

#     # Text Area
#     text_area = tk.Text(window, wrap=tk.WORD, width=50, height=10)
#     text_area.pack(pady=10)
#     text_area.insert(tk.END, "Hello! I am your Physics Assistant. Ask me any physics-related question!\n")

#     # Speech Recognition & Text-to-Speech
#     recognizer = sr.Recognizer()
#     microphone = sr.Microphone()
#     engine = pyttsx3.init("nsss")

#     welcome_phrase = "Hello! I am your Physics Assistant. Ask me any physics-related question!"
#     continue_Phrase = "How may I help you for further assistance."
#     thinking_phrase = "hmmm.. Let me think about it..."
#     audio_error_phrase = "Sorry, I could not understand the audio." + continue_Phrase
#     session_id = str(datetime.now())

#     recorder = VideoRecorder(max_seconds=5, fps=30)

#     def listen_and_respond():
#         try:
#             recorder.start_recording()
#             with microphone as source:
#                 image_label.config(image=listening_img)  # Show listening face
#                 window.update()  # Update the GUI to display the change
#                 recognizer.adjust_for_ambient_noise(source)
#                 audio = recognizer.listen(source, timeout=5, phrase_time_limit=20)
#                 question = recognizer.recognize_google(audio)
#                 text_area.insert(tk.END, f"You said: {question}\n")
#                 text_area.see(tk.END)

#                 if question.lower() == "exit":
#                     recorder.stop_recording()
#                     window.destroy()  # Close the GUI window
#                     return

#                 image_label.config(image=thinking_img)  # Show thinking face
#                 window.update()

#                 text_area.insert(tk.END, thinking_phrase + "\n")
#                 text_area.see(tk.END)
#                 engine.say(thinking_phrase)
#                 engine.runAndWait()

#                 recorder.stop_recording()

#                 # Save the recorded video
#                 video_path = "latest_video.avi"
#                 saved_video_path = recorder.save_video(video_path)

#                 if saved_video_path:
#                     answer = ask_chatgpt(question, session_id, video_path=saved_video_path)

#                     text_area.insert(tk.END, f"PhysicsAssistant: {answer}\n")
#                     image_label.config(image=speaking_img)  # Show speaking face
#                     window.update()
#                     engine.say(answer)
#                     engine.runAndWait()
#                 else:
#                     text_area.insert(tk.END, "Error: Unable to capture video.\n")
#                     engine.say("Error: Unable to capture video.")
#                     engine.runAndWait()

#                 text_area.insert(tk.END, continue_Phrase + "\n")
#                 text_area.see(tk.END)
#                 engine.say(continue_Phrase)
#                 engine.runAndWait()

#         except sr.UnknownValueError:
#             recorder.stop_recording()
#             text_area.insert(tk.END, audio_error_phrase + "\n")
#             engine.say(audio_error_phrase)
#             engine.runAndWait()
#         except sr.RequestError as e:
#             recorder.stop_recording()
#             error_message = f"Could not request results; {e}"
#             text_area.insert(tk.END, error_message + "\n")
#             engine.say("Could not request results.")
#             engine.runAndWait()
#         finally:
#             image_label.config(image=listening_img)  # Reset to listening face
#             window.update()

#     # Button
#     listen_button = tk.Button(window, text="Speak", command=listen_and_respond)
#     listen_button.pack()

#     image_label.config(image=speaking_img)  # Show speaking face
#     window.update()
#     engine.say(welcome_phrase)
#     engine.runAndWait()

#     # Start camera feed
#     threading.Thread(target=show_camera_feed, args=(camera_label,)).start()

#     window.mainloop() 

if __name__ == "__main__":
    main()