from http.server import BaseHTTPRequestHandler, HTTPServer
import subprocess
from urllib.parse import urlparse, parse_qs
import t2s

def bash(*args):
  #  "выполняет команду на баше"
  cmd_string = ' '.join(str(e) for e in args)
  cmd = bytes(cmd_string, encoding='utf-8')
  proc = subprocess.Popen([cmd], shell=True, stdin=None, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  try:
    outs, errs = proc.communicate(input=None, timeout=17)
    if errs:
      return errs.decode('utf-8')
    else:
      return outs.decode('utf-8')
  except Exception as e:
      proc.kill()

# Port on which server will run.
PORT = 28999

class HTTPRequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        """ Handle GET Request"""
        query_components = parse_qs(urlparse(self.path).query)
        print(query_components)
        with open('index.html', 'rb') as fd:
            html = fd.read()
        if 'text' in query_components:
            print('text')
#            print(query_components)
#            a.talk(query_components['text'])
            self.send_response(200)
            self.send_header('Last-Modified', "")
            self.send_header('Access-Control-Allow-Origin:', "*")
            self.end_headers()
        else:
            self.send_header('Content-type', 'text/html')
            self.send_response(200)
            self.wfile.write(html)
            self.send_header('Last-Modified', "")
            self.end_headers()

#        print(bash(command))

    def do_POST(self):
        """ Handle POST Request"""
        length = self.headers['content-length']
        data = self.rfile.read(int(length))
        data = data.decode('utf-8')
        data = parse_qs(data, encoding='utf-8')
        print(data)

        text = data['text'][0]
        if not 'method' in data.keys():
            method = 'yandex'
            speaker = 'omazh'
            emotion = 'neutral'
        else:
            method = data['method'][0]
            if method == 'yandex':
                if 'speaker' in data.keys():
                    speaker = data['speaker'][0]
                else:
                    speaker = 'omazh'
                if 'emotion' in data.keys():
                    emotion = data['emotion'][0]
                else:
                    emotion = 'neutral'
            else:
                method = 'google'
                speaker = None
                emotion = None

        print(text)
        print(data)
        a.talk(text, method, speaker, emotion)

        self.send_header('Content-type', 'text/html')
        self.send_response(404, 'nothing to do here')
        self.send_header('Last-Modified', "")
        self.end_headers()


if __name__ == '__main__':
    HTTPDeamon = HTTPServer(('', PORT), HTTPRequestHandler)
    print("Listening at port", PORT)
    a = t2s.Text2Speech()

    try:
        HTTPDeamon.serve_forever()
    except KeyboardInterrupt:
        pass

    HTTPDeamon.server_close()
    print("Server stopped")