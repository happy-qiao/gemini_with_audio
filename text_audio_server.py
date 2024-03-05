import queue
import socket
import threading
import base64

import vertexai
from vertexai.generative_models import GenerativeModel, ChatSession

from google.cloud import speech, texttospeech

class Server:
    def __init__(self):
        self._buff = queue.Queue()
        self.host = '127.0.0.1'
        self.port = 65432
        self.rate = 16000

    def listen(self):
        with self.conn:
            while True:
                data = self.conn.recv(1024)
                if not data:
                    self._buff.put(None)
                    break
                self._buff.put(data)

    def generator(self):
        while True:
            chunk = self._buff.get()
            if chunk is None:
                return
            data = [chunk]

            while True:
                try:
                    chunk = self._buff.get(block=False)
                    if chunk is None:
                        return
                    data.append(chunk)
                except queue.Empty:
                    break
            
            yield b"".join(data)
        
    def send_text(self, text: str):
        self.conn.sendall(b'[[T]]')
        self.conn.sendall(text.encode('utf-8'))

    def send_audio(self, tts_client, text):
        response = tts_client.synthesize_speech(
            request = {
                'input': texttospeech.SynthesisInput(text=text),
                'voice': texttospeech.VoiceSelectionParams(
                    language_code="en-US",
                    name="en-US-Standard-C",
                    ssml_gender=texttospeech.SsmlVoiceGender.FEMALE,
                ),
                'audio_config': texttospeech.AudioConfig(
                    audio_encoding=texttospeech.AudioEncoding.MP3
                )
            }
        )
        self.conn.send(b'[[S]]')
        self.conn.send(base64.b64encode(response.audio_content))
        self.conn.send(b'[[E]]')


    def listen_loop(self, responses, chat):
        tts_client = texttospeech.TextToSpeechClient()

        for response in responses:
            if not response.results:
                continue
            result = response.results[0]
            if not result.alternatives:
                continue
            transcript = result.alternatives[0].transcript.strip()
            if len(transcript) == 0:
                continue
            print(transcript, result.is_final)

            if result.is_final:
                self.send_text(f'{transcript}\n< ')
                self.conn.send(b'[[Q]]')
                try:
                    chat_response = "".join([chunk.text for chunk in chat.send_message(transcript, stream=True)])
                    self.send_text(chat_response)
                    self.send_audio(tts_client, chat_response)
                except:
                    pass
                self.send_text('\n\n> ')

    def run(self):
        client = speech.SpeechClient()
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=self.rate,
            language_code='en-US',
        )

        streaming_config = speech.StreamingRecognitionConfig(
            config=config, interim_results=True
        )

        vertexai.init(project='vertexsdk', location='us-west1')
        model = GenerativeModel("gemini-1.0-pro")
        chat = model.start_chat()

        self.send_text('Start chat with Gemini....\n\n> ')

        audio_generator = self.generator()
        requests = (
            speech.StreamingRecognizeRequest(audio_content=content)
            for content in audio_generator
        )
        responses = client.streaming_recognize(streaming_config, requests)
        self.listen_loop(responses, chat)

    def start(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            print(f'Listening on {self.host}:{self.port}...')
            s.bind((self.host, self.port))
            s.listen()
            conn, addr = s.accept()
            self.conn = conn
            print(f"Connected by {addr}")

            threading.Thread(target=self.listen).start()

            self.run()

if __name__ == '__main__':
    Server().start()
