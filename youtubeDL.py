from __future__ import unicode_literals
import youtube_dl
from youtube_dl.utils import DateRange
import utils
import os
converted_videos = []

class MyLogger(object):
    def debug(self, msg):
        print(msg)

    def warning(self, msg):
        pass

    def error(self, msg):
        print(msg)

class Downloader():
    sources = "config/sources"
    dateRange = DateRange('20180921')

    def my_hook(d):
        print(d)
        if d['status'] == 'finished':
            print('Done downloading, now converting ...')
            print(d['filename'])
            converted_videos.append(os.path.splitext(d['filename'])[0] + '.mp3')

    ydl_opts = {
        'ignoreerrors': True,
        'writesubtitles': True,
        'writeautomaticsub': True,
        # 'allsubtitles': True,
        # 'subtitleslangs': 'en',
        'writethumbnail': True,
        'writeinfojson': True,
        'daterange': dateRange,
        'playlist_items': '1-50',
        'format': 'bestaudio/best',
        'outtmpl': 'data/downloads/%(upload_date)s/%(upload_date)s_%(uploader_id)s_%(id)s.%(ext)s',
        'keepvideo': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'logger': MyLogger(),
        'progress_hooks': [my_hook],
    }

    def downloadAndConvert(self,_sources):
        if(_sources != ''):
            self.sources = _sources
        self.ydl_opts.update(daterange = self.dateRange)
        sources = utils.load_list(self.sources)
        print(sources)

        with youtube_dl.YoutubeDL(self.ydl_opts) as ydl:
            ydl.download(sources)
            print('Converting and Download finished')
            if(len(converted_videos) > 0):
                utils.write_list("config/downloaded", converted_videos)

    def setDateRange(self,_dateRange):
        self.dateRange = _dateRange

def main():
    d = Downloader()
    d.downloadAndConvert("config/sources")

if __name__ == '__main__':
    main()

