from os import path
from pydub import AudioSegment
from os import path
AUDIO_FILE = path.join(path.dirname(path.realpath(__file__)), "test.mp3")

# files                                                                         
src = path.join(path.dirname(path.realpath(__file__)), "test.mp3")
dst = path.join(path.dirname(path.realpath(__file__)), "done.wav")

print(src)
print(dst)

# convert wav to mp3                                                            
sound = AudioSegment.from_mp3(src)
sound.export(dst, format="wav")