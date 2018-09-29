import urllib.request, urllib.parse, urllib.error
import time
import datetime
import os
import io
import youtubeDL
import utils
import json
import requests
import bz2
import configparser
from youtube_dl.utils import DateRange
from stanfordcorenlp import StanfordCoreNLP
import sttConverter as Transcribe

def main():
    #Load crawler config file
    config = configparser.ConfigParser()
    config.read('config/config.ini')
    defConfig = config['DEFAULT']

    skipCrawling = defConfig.getboolean('skipCrawling')
    skipTranscribe = defConfig.getboolean('skipTranscribe')
    skipWordToSentence = defConfig.getboolean('skipWordToSentence')
    skipNodExport = defConfig.getboolean('skipNodExport')
    useWebSockets = defConfig.getboolean('useWebSockets')
    httpApiTimeout = int(defConfig['httpApiTimeout'])
    operationDate = str(defConfig['operationDate'])
    operationLanguage = defConfig['operationLanguage']
    basepath = defConfig['basepath']
    outputPath = defConfig['outputPath']
    gstreamerHttpApiUrl = defConfig['gstreamerHttpApiUrl']
    gstreamerWsStatusUrl = defConfig['gstreamerWsStatusUrl']
    gstreamerWsSpeechUrl = defConfig['gstreamerWsSpeechUrl']
    stanfordNlpPath = defConfig['stanfordNlpPath']
    #stanfordNlpPort = int(defConfig['stanfordNlpPort'])

    if(operationDate == 'today'):
        operationDate = datetime.datetime.today().strftime('%Y%m%d')
    elif(operationDate == 'yesterday'):
        yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
        operationDate = yesterday.strftime('%Y%m%d')

    print('Operation Date:' + operationDate)

    #Step 1: check sources, download videos and convert to mp3
    if(not skipCrawling):
        utils.clearFile("config/downloaded")
        d = youtubeDL.Downloader()
        d.setDateRange(DateRange(operationDate))
        d.downloadAndConvert("config/sources")


    #Step 2: convert the downloaded files to text
    if(not skipTranscribe):
        utils.clearFile("config/transcribed")
        sleepCounter = 0
        transcribes = []
        downloadedVideos = utils.load_list(basepath + "config/downloaded")

        if (len(downloadedVideos) > 0):
            #Create Status Socket. Enables us to check for available workers
            statusSocket = Transcribe.StatusSocket(gstreamerWsStatusUrl)
            statusSocket.connect()
            errMsg = False

            for audiofile_path in downloadedVideos:
                # Routine to check if workers are available
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


                if(not os.path.isfile(os.path.splitext(audiofile_path)[0] + '.sst')):
                    with open(basepath + audiofile_path, 'rb') as audiofile:
                        utterance = ""

                        if(not useWebSockets):
                            files = {'request_file': audiofile}
                            try:
                                print(("Start to transcribe " + audiofile_path))
                                result = requests.post(gstreamerHttpApiUrl, files=files, timeout=httpApiTimeout)
                                resultJSON = json.loads(result.text)
                                utterance = str(resultJSON["hypotheses"][0]["utterance"])

                            except requests.exceptions.Timeout:
                                print('It timed out!')

                        elif(useWebSockets):
                            rate = 32000  # Normallay the converted mp3 is 24000(192kbps)
                            save_adaptation_state = None
                            send_adaptation_state = None
                            content_type = ""

                            if(content_type == '' and audiofile.name.endswith(".raw")):
                               content_type = "audio/x-raw, layout=(string)interleaved, rate=(int)%d, format=(string)S16LE, channels=(int)1" %(rate//2)

                            ws = Transcribe.SpeechSocket(audiofile, gstreamerWsSpeechUrl + '?%s' % (urllib.parse.urlencode([("content-type", content_type)])), byterate=rate, save_adaptation_state_filename=save_adaptation_state, send_adaptation_state_filename=send_adaptation_state)
                            ws.connect()
                            utterance = ws.get_full_hyp()
                            print(utterance)
                            ws.close()

                        if(len(utterance) > 0):
                            utils.write_line(os.path.splitext(audiofile_path)[0] + '.sst', utterance)
                            transcribes.append(os.path.splitext(audiofile_path)[0] + '.sst')

                    sleepCounter = 0
                    audiofile.close()
                else:
                    print("Skipping. File already exists: " + os.path.splitext(audiofile_path)[0] + '.sst')
                    transcribes.append(os.path.splitext(audiofile_path)[0] + '.sst')

            statusSocket.close()

            #Write all transcribed file paths
            if (len(transcribes) > 0):
                utils.write_list("config/transcribed", transcribes)


    #Step 3: use OpenNLP to tokenize and create sentences and ture caseing
    if (not skipWordToSentence):
        utils.clearFile("config/trueCased")
        trueCased = []
        transcribe_paths = utils.load_list(basepath + "config/transcribed")

        if (len(transcribe_paths) > 0):
            print('Doing StnadfordNLP sentence splitting and true caseing')
            nlp = StanfordCoreNLP(stanfordNlpPath)
            for transcribe_path in transcribe_paths:
                transcribe = utils.load_line(transcribe_path)

                if(operationLanguage == 'en'):
                    props = {'annotators': 'tokenize,ssplit,truecase', 'pipelineLanguage': 'en', 'outputFormat': 'json', 'truecase.overwriteText': 'true'}
                elif(operationLanguage == 'de'):
                    props = {'annotators': 'tokenize,ssplit', 'pipelineLanguage': 'de', 'outputFormat': 'json', 'truecase.overwriteText': 'true'}

                annotationResult = nlp.annotate(transcribe, properties=props)
                annotationJSON = json.loads(annotationResult)
                print(annotationResult)

                utils.write_json(os.path.splitext(transcribe_path)[0] +'.json',annotationJSON)

                trueSentences = []
                charOffsetIndex = 0
                sentenceStart = True

                for sentence in annotationJSON["sentences"]:
                    trueWords = ""
                    for tokens in sentence["tokens"]:
                        if(int(tokens["characterOffsetBegin"]) > charOffsetIndex and not sentenceStart):
                            trueWords = trueWords + " "
                        trueWords= trueWords + tokens["word"]
                        charOffsetIndex= int(tokens["characterOffsetEnd"])
                        sentenceStart = False
                    trueSentences.append(trueWords)
                    sentenceStart = True
                print(trueSentences)

                utils.write_list(os.path.splitext(transcribe_path)[0] +'.wts',trueSentences)
                trueCased.append(os.path.splitext(transcribe_path)[0] +'.wts')

            nlp.close()

            #Write all transcribed file paths
            if (len(trueCased) > 0):
                utils.write_list("config/trueCased", trueCased)


    #Step 4: export for nod in bz2 compressed format
    if (not skipNodExport):
        lines = []

        if(not skipWordToSentence):
            paths = utils.load_list(basepath + "config/trueCased")
        else:
            paths = utils.load_list(basepath + "config/transcribed")
        if (len(paths) > 0):
            print('Exporting transcribes to bz2')

            for path in paths:
                text = utils.load_list(path)
                infoJson = utils.load_line(os.path.splitext(path)[0] + '.info.json')
                videoInfo = json.loads(infoJson)
                link = videoInfo['webpage_url']

                for line in text:
                    outputLine = line + "\t" + link
                    lines.append(outputLine)

            with bz2.BZ2File(outputPath + operationDate, 'wb') as output:
                with io.TextIOWrapper(output, encoding='utf-8') as enc:
                    enc.write("\n".join(lines))
            os.rename(outputPath + operationDate, outputPath + operationDate + ".bz2")

    print("Finished pipeline")


if __name__ == "__main__":
    main()