import requests
import pickle
import os
from datetime import datetime as dt


RASPBERRY = 0


class Text2Speech:
    def __init__(self):
        with open('key', 'rb') as fd:
            self.key = str(fd.read().decode('utf-8'))
        self.path = 'speech_cache/'
        self.speech_pickle_file = ''.join([self.path, 'speech_pickle'])

        if os.path.exists(self.path):
            if os.path.exists(self.speech_pickle_file):
                with open(self.speech_pickle_file, 'rb') as fd:
                    self.speech_dict = pickle.load(fd)
            else:
                self.speech_dict = {}
        else:
            os.mkdir(self.path)
            self.speech_dict = {}

    def talk(self, speech_text, method='yandex', speaker='omazh', emotion='evil', speed=1):
        self.speech_text = speech_text.lower()

        if method == 'yandex':
            get_mp3_function = self.get_mp3_from_yandex
            speech_info = 'O'.join([self.speech_text, method, speaker, emotion, str(speed)])
        else:
            get_mp3_function = self.get_mp3_from_google
            speech_info = self.speech_text

        print(speech_info)
        if speech_info not in self.speech_dict.keys():
            mp3file = get_mp3_function(self.speech_text, speaker, emotion, speed)
            self.Play(mp3file)
        else:
            self.Play(self.speech_dict[speech_info])

    def get_mp3_from_google(self, *a):
        params = {'ie': 'UTF-8',
                  'q': self.speech_text,
                  'tl': 'ru',
                  'total': '1',
                  'idx': '0',
                  'textlen': '32',
                  'ttsspeed':'0.34',
                  'client': 'tw-ob',
                  }
        headers = {'user-agent': 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
        r = requests.get('https://translate.google.ru/translate_tts', headers=headers, params=params)

        mp3filename = ''.join([self.path, str(abs(hash(r.content))), '.mp3'])

        with open(mp3filename, 'wb', 0) as fd:
            fd.write(r.content)
            fd.flush()

        self.speech_dict.update({self.speech_text: mp3filename})

        with open(self.speech_pickle_file, 'wb') as fd:
            pickle.dump(self.speech_dict, fd)

        return mp3filename

    def get_mp3_from_yandex(self, text, speaker='omazh', emotion='evil', speed=1):
        """
        https://tech.yandex.ru/speechkit/cloud/doc/dg/concepts/speechkit-dg-tts-docpage/

        https://tts.voicetech.yandex.net/generate?
          text=<текст для озвучивания>
        & format=<формат аудио файла>
        & lang=<язык>
        & speaker=<голос>
        & key=<API‑ключ>

        & [emotion=<эмоциональная окраска голоса>]
        & [speed=<скорость речи>]


        Эмоциональная окраска голоса. Возможные значения:
        good (доброжелательный),
        evil (злой),
        neutral (нейтральный),

        женские голоса jane, oksana, alyss и omazh,
        мужские голоса zahar и ermil.
        """
        params = {
            'text': text,
            'format': 'mp3',
            'lang': 'ru_RU',
            'speaker': speaker,
            'key': self.key,
            'emotion': emotion,
            'speed': speed
        }
        r = requests.get('https://tts.voicetech.yandex.net/generate', params=params)

        mp3filename = ''.join([self.path, str(dt.now().timestamp()), '.mp3'])

        with open(mp3filename, 'wb', 0) as fd:
            fd.write(r.content)
            fd.flush()

        speech_info = 'O'.join([self.speech_text, 'yandex', speaker, emotion, str(speed)])
        self.speech_dict.update({speech_info: mp3filename})

        with open(self.speech_pickle_file, 'wb') as fd:
            pickle.dump(self.speech_dict, fd)

        return mp3filename

    def Play(self, mp3file):
        if RASPBERRY:
        # mplayer -ao alsa:device=hw=0.0
            os.system(' '.join(['mplayer', '-ao', 'alsa:device=hw=0.1', mp3file]))
        else:
            os.system(' '.join(['mplayer', mp3file]))
            #sound = pyglet.media.load(mp3file)
            #sound.play()

            #def exiter(dt):
            #    pyglet.app.exit()

            #print(sound.duration)
            #pyglet.clock.schedule_once(exiter, sound.duration)
            #pyglet.app.run()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('text', type=str, help='Текст, который будет произнесён')
    args = parser.parse_args()

    a = Text2Speech()
    a.talk(args.text)

