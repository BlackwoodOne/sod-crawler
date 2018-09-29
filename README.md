#sod-crawler

This project is crawling, downloading and transcribing Youtube playlists and videos of daily published news channels. The projects main aim is to provide the transcribed videos to the Network of the Day [NoD](https://github.com/uhh-lt/NoDCore) project. 

The project can either be setup as a local installation or as a docker container stack.

The project is dependent on the [kaldi-gstreamer](https://github.com/jcsilva/docker-kaldi-gstreamer-server) project, the [CoreNLP](https://stanfordnlp.github.io/CoreNLP/) project and [youtube-DL](https://github.com/rg3/youtube-dl). 

In the processing pipeline the YoutubeDL downloader is used to collect and download the videos and playlists. As a postprocessing step the downloads are converted to _mp3_ with _ffmpg_. The _mp3_ files are then send to _kladi-gstreamer_ server, to transcribe the audio files to text. For this step a [Kaldi ASR](https://github.com/kaldi-asr/kaldi) model is necessary (e.g. German Model from [UHH-LT](https://github.com/uhh-lt/kaldi-tuda-de)). As a third step "Words To Sentence" and "True Case" annotation is done via _CoreNLP_. The last step is to transform, compress and export the data fitting the requirements of the NoD-Core. 

## Docker Image
To build the crawler docker image:

1. `git clone github.com/BlackwoodOne/sod-crawler`
2. `cd sod-crawler`
3. `docker-compose up --build`

## Docker Compose NoD Setup
To build the complete stack with all dependencies execute:

1. `git clone github.com/BlackwoodOne/sod-crawler`
2. `cd sod-crawler`
3. `docker-compose -f docker-compose.nod.yml up --build`

This wil setup and start five docker containers connected by a docker network. To use the system you need to provide a Kaldi ASR model to the kaldi-gstreamer server in `gstreamer/model/` . A german model can be found [here](https://github.com/uhh-lt/kaldi-tuda-de). To start a worker execute `/opt/start.sh -y /opt/models/KALDI_YAML_FILE.yaml`  within the _gstreamer_ docker container.

## Local Setup
### Dependencies

* linux based system (Ubuntu 16.04)
* ffmpg
* openjdk-8-jre

Enviroment for Python with:

* Python 3.6
* ws4py
* stanfordcorenlp
* urllib3
* youtube-dl

### Setup
1. `git clone github.com/BlackwoodOne/sod-crawler`
2. `cd sod-crawler`
3. `wget http://nlp.stanford.edu/software/stanford-corenlp-full-2018-02-27.zip`
4. `unzip stanford-corenlp-full-2018-02-27.zip`
5. `rm stanford-corenlp-full-2018-02-27.zip`
6. `mv stanford-corenlp-full-2018-02-27 /PATH_TO_SOD-CRAWLER/coreNLP` 

In your environment (e.g. virtualenv or conda) run:
1. `pip install --no-cache-dir -r requirements.txt`

To use the system you need to provide a Kaldi ASR model to the kaldi-gstreamer server in `gstreamer/model/` . A german model can be found [here](https://github.com/uhh-lt/kaldi-tuda-de). To start a worker execute `/opt/start.sh -y /opt/models/KALDI_YAML_FILE.yaml`  within the _gstreamer_ docker container.


## RUN

    python speechcrawler.py

This will run the crawler based on the given _config.ini_. In case of the docker setup, you need to execute this command inside the _speech-crawler_ docker container.

In the docker-compose Nod stack there is a Cronjob configured which will execute every night. You can change this in the crontab file within the docker conatiner.

You can find the Network of the Day website under: `http://127.0.0.1:10008/nod/`

## Data Structure
####Downloads
The videos are downloaded to `data/downloads/<upload_date>/<upload_date>_<uploader_id>_<video_id>` .

During the process, transcribe-files (.stt) and sentence-split-files (.wts) are generated. The final export is by default written to `data/nod/german` . The docker filepaths are provided via docker volume to the host `PATH_TO_Crawler/out/` . 

###Configs
All config file live in the `config/` folder. The applications _config.ini_, as well as the crawler sources. During the process, files for the next pipeline steps are created.

## Options and Setings
Settings can be made in the `configs.ini` . By default the configuration is made to work with the docker-compose NoD stack. You may want to change this for a local setup.

###[DEFAULT]
* **skipCrawling**(False): Skipping the youtubeDL crawler in the pipeline
* **skipTranscribe**(False): Skipping the kaldi-gstreamer transcription
* **skipWordToSentence**(False): Skipping th CoreNLP sentence splitting and true casing
* **skipNodExport**(False): Skipping the export for the Nod-Core
* **operationDate**(e.g. 20180924): Setting the date for the youtube uploads(YearMonthDay / yesterday / today)
* **operationLanguage**(de): Choosing the coreNLP operation language
* **useWebSockets**(False): Using Websockets or the HttpApi(when false) for connection to the kaldi-gestreamer
* **httpApiTimeout**(600): HttpApi request timeout in seconds
* **basepath**(/app/): the applications basepath
* **outputPath**(data/nod/german/): the output path for the NoD export
* **gstreamerHttpApiUrl**(http://gstreamer/client/dynamic/recognize): the url for the gstreamer HttpApi requests. http://gestreamer/ is in this case the docker network link to the gstreamer container
* **gstreamerWsStatusUrl**(ws://gstreamer/client/ws/status): url to the gstreamer status socket
* **gstreamerWsSpeechUrl**(ws://gstreamer/client/ws/speech): url for the web socket based gstreamer connection
* **stanfordNlpPath**(/app/coreNLP): path to the coreNLP files

### Crawler Sources
The youtube source paths can be edited in the `config/sources` file. The links can be either to a playlist or a video and need to be line-separated. Comments can be made with the `#` symbol. 






