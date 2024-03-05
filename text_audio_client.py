import base64
import os
import pyaudio
import socket

class Client:
    def __init__(self):
        self.host = '127.0.0.1'
        self.port = 65432
        self.rate = 16000
        self.recording = False
        self.slient = None

    def _send(self, in_data, frame_count, time_info, status_flags):
        if self.recording:
            self.s.send(in_data)
            self.slient = in_data
        else:
            self.s.send(self.slient)
        return None, pyaudio.paContinue


    def start(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.host, self.port))
            print('======> Connected to server!')
            self.s = s

            audio_interface = pyaudio.PyAudio()
            audio_stream = audio_interface.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=self.rate,
                input=True,
                frames_per_buffer=1600,
                stream_callback=self._send
            )

            self.recording = True

            buffer = ''
            current_mode = ''

            while True:
                data = s.recv(1024)
                if not data:
                    break

                buffer += data.decode('utf-8')
                while True:
                    tag_start = buffer.find('[[')
                    tag_end = buffer.find(']]')

                    if tag_start < 0 and current_mode == 'T':
                        print(buffer, end="", flush=True)
                        buffer = ''
                        break

                    if tag_start < 0 or tag_end < 0:
                        break
                    assert tag_end == tag_start + 3
                    prev = buffer[0:tag_start]
                    new_mode = buffer[tag_start+2]
                    buffer = buffer[tag_end+2:]

                    if current_mode == 'T':
                        print(prev, end="", flush=True)
                    elif current_mode == 'Q':
                        # self.recording = False
                        pass
                    elif current_mode == 'S':
                        audio = base64.b64decode(prev)
                        with open('/tmp/output.mp3', 'wb') as out:
                            out.write(audio)
                        os.system('afplay /tmp/output.mp3')
                        os.remove('/tmp/output.mp3')
                    elif current_mode == 'E':
                        # self.recording = True
                        pass
                    current_mode = new_mode

            audio_stream.stop_stream()
            audio_stream.close()
            audio_interface.terminate()

# with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
#     s.connect((HOST, PORT))
#     s.sendall(b"Hello, world")
#     data = s.recv(1024)

# print(f"Received {data!r}")

if __name__ == '__main__':
    Client().start()
