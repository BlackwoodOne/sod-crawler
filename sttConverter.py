#import argparse
from ws4py.client.threadedclient import WebSocketClient
import threading
import sys
import urllib.request, urllib.parse, urllib.error
import queue
import json
import time
import os
import utils
import requests

if sys.version_info[0] < 3:
    raise Exception("Python 3 is required to execute.")

def rate_limited(maxPerSecond):
    minInterval = 1.0 / float(maxPerSecond)
    def decorate(func):
        lastTimeCalled = [0.0]
        def rate_limited_function(*args,**kargs):
            elapsed = time.clock() - lastTimeCalled[0]
            leftToWait = minInterval - elapsed
            if leftToWait>0:
                time.sleep(leftToWait)
            ret = func(*args,**kargs)
            lastTimeCalled[0] = time.clock()
            return ret
        return rate_limited_function
    return decorate

class StatusSocket(WebSocketClient):
    def __init__(self, url, protocols=None, extensions=None, heartbeat_freq=None):
        super(StatusSocket, self).__init__(url, protocols, extensions, heartbeat_freq)
        self.workersAvailable = False

    def opened(self):
        print ("Status Socket opened.")


    def closed(self, code, reason=None):
        print(("Status Socket opened.", code, reason))

    def received_message(self, m):
        #print (m)
        response = json.loads(str(m))
        if response['num_workers_available'] > 0:
            self.workersAvailable = True
        else:
            self.workersAvailable = False



class SpeechSocket(WebSocketClient):

    def __init__(self, audiofile, url, protocols=None, extensions=None, heartbeat_freq=None, byterate=32000,
                 save_adaptation_state_filename=None, send_adaptation_state_filename=None):
        super(SpeechSocket, self).__init__(url, protocols, extensions, heartbeat_freq)
        self.final_hyps = []
        self.audiofile = audiofile
        self.byterate = byterate
        self.final_hyp_queue = queue.Queue()
        self.save_adaptation_state_filename = save_adaptation_state_filename
        self.send_adaptation_state_filename = send_adaptation_state_filename

    @rate_limited(4)
    def send_data(self, data):
        self.send(data, binary=True)

    def opened(self):
        #print "Socket opened!"
        def send_data_to_ws():
            if self.send_adaptation_state_filename is not None:
                print("Sending adaptation state from %s" % self.send_adaptation_state_filename, file=sys.stderr)
                try:
                    adaptation_state_props = json.load(open(self.send_adaptation_state_filename, "r"))
                    self.send(json.dumps(dict(adaptation_state=adaptation_state_props)))
                except:
                    e = sys.exc_info()[0]
                    print("Failed to send adaptation state: ",  e, file=sys.stderr)
            with self.audiofile as audiostream:
                for block in iter(lambda: audiostream.read(int(self.byterate//4)), ""):
                    self.send_data(block)
            print("Audio sent, now sending EOS", file=sys.stderr)
            self.send("EOS")

        t = threading.Thread(target=send_data_to_ws)
        t.start()


    def received_message(self, m):
        response = json.loads(str(m))
        #print >> sys.stderr, "RESPONSE:", response
        #print >> sys.stderr, "JSON was:", m
        if response['status'] == 0:
            if 'result' in response:
                trans = response['result']['hypotheses'][0]['transcript']
                if response['result']['final']:
                    #print >> sys.stderr, trans,
                    self.final_hyps.append(trans)
                    print('\r%s' % trans.replace("\n", "\\n"), file=sys.stderr)
                else:
                    print_trans = trans.replace("\n", "\\n")
                    if len(print_trans) > 80:
                        print_trans = "... %s" % print_trans[-76:]
                    print('\r%s' % print_trans, end=' ', file=sys.stderr)
            if 'adaptation_state' in response:
                if self.save_adaptation_state_filename:
                    print("Saving adaptation state to %s" % self.save_adaptation_state_filename, file=sys.stderr)
                    with open(self.save_adaptation_state_filename, "w") as f:
                        f.write(json.dumps(response['adaptation_state']))
        else:
            print("Received error from server (status %d)" % response['status'], file=sys.stderr)
            if 'message' in response:
                print("Error message:",  response['message'], file=sys.stderr)


    def get_full_hyp(self, timeout=60):
        return self.final_hyp_queue.get(timeout)

    def closed(self, code, reason=None):
        #print "Websocket closed() called"
        #print >> sys.stderr
        self.final_hyp_queue.put(" ".join(self.final_hyps))


def main():
    sleepCounter = 0
    basepath = "/home/steffen/Dev/Repos/"
    sources = utils.load_list(basepath+"sod-crawler/config/stt_processing")
    uri = "ws://localhost:8080/client/ws/speech"
    rate = 192000 #24000
    save_adaptation_state = None
    send_adaptation_state = None
    content_type = ""

    statusSocket = StatusSocket("ws://localhost:8080/client/ws/status")
    statusSocket.connect()
    errMsg = False

    for audiofile_path in sources:
        while(statusSocket.workersAvailable == False):
            if (sleepCounter < 60):
                print("No workers available, sleeping for 1 second")
                sleepCounter += 1
                time.sleep(1)
            else:
                errMsg = True
                print("Slept " + str(sleepCounter) + " times. Maybe there is a Problem with the workers?")
                break

        if (errMsg == True):
            break

        print(("Start to translate " + audiofile_path))
        with open(basepath+"sod-crawler/"+audiofile_path, 'rb') as audiofile:
            #if content_type == '' and audiofile.name.endswith(".raw"):
            #    content_type = "audio/x-raw, layout=(string)interleaved, rate=(int)%d, format=(string)S16LE, channels=(int)1" %(rate//2)

            # ws = SpeechSocket(audiofile, uri + '?%s' % (urllib.parse.urlencode([("content-type", content_type)])), byterate=rate, save_adaptation_state_filename=save_adaptation_state, send_adaptation_state_filename=send_adaptation_state)
            # ws.connect()
            # result = ws.get_full_hyp()
            # print(result)

            url = 'http://localhost:8888/client/dynamic/recognize'
            files = {'request_file': audiofile}
            result = requests.post(url, files=files)
            print (result.text)
            print (result.json)


            if(len(result) > 0):
                utils.write_line(os.path.splitext(audiofile.name)[0] +'.sst',result)
            #ws.close()

        sleepCounter = 0
        audiofile.close()

    statusSocket.close()

if __name__ == "__main__":
    main()