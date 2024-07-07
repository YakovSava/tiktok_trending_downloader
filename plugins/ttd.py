import os
import asyncio
import concurrent.futures
import ffmpeg

from time import time
from TikTokApi import TikTokApi
from yt_dlp import YoutubeDL
from ffmpeg import Error
from plugins.pdfm import generate_report

class TikTokError(Exception):
    pass

class TikTokDownloader:

    def __init__(self,
             tt_token:str=None,
             output_folder:str="output",
             speed_ratio:float=1.0,
             resize_ratio:float=1.0,
             audio_filename:str="audio.mp3",
             report:str="report.pdf"
        ):
        if tt_token is None:
            raise TikTokError('TikTok token not found!')
        self._output = output_folder
        self._video_speed = speed_ratio
        self._video_resize = resize_ratio
        self.audio = audio_filename
        self._tt_token = tt_token
        self._report_filename = report

    async def get_trending_videos(self, count:int=25):
        video_urls = []
        async with TikTokApi() as api:
            await api.create_sessions(
                ms_tokens=[self._tt_token], num_sessions=1, sleep_after=3
            )
            cnt = 0
            async for video in api.trending.videos(count=count):
                video_url = f"https://www.tiktok.com/@{video.author.username}/video/{video.id} "
                video_urls.append(video_url)
                if cnt == count:
                    break
                cnt += 1
        return video_urls

    def _download_video(self, video_url:str):
        ydl_opts = {
            "quiet": True,
            "outtmpl": f"{self._output}/%(uploader)s_%(id)s_%(timestamp)s.%(ext)s",
        }
        ydl = YoutubeDL(ydl_opts)
        info_dict = ydl.extract_info(video_url, download=True)
        filename = ydl.prepare_filename(info_dict)
        return filename

    def _modify_video(self, video_path:str):
        output_path = os.path.join(
            self._output, f"temp_{os.path.basename(video_path)}"
        )
        (
            ffmpeg
            .input(video_path)
            .filter("setpts", f"PTS/{self._video_speed}")
            .filter(
                "scale",
                f"trunc(iw*{self._video_resize}/2)*2",
                f"trunc(ih*{self._video_resize}/2)*2",
            )
            .output(
                output_path, vcodec="libx264", acodec="aac", preset="ultrafast"
            )
            .global_args("-y")
            .run(overwrite_output=True, capture_stdout=True, capture_stderr=True)
        )

        video_part = ffmpeg.input(output_path)
        audio_part = ffmpeg.input(self.audio)
        (
            ffmpeg
            .output(
                audio_part.audio,
                video_part.video,
                video_path,
                shortest=None,
                vcodec="copy",
            )
            .global_args("-y")
            .run(overwrite_output=True, capture_stdout=True, capture_stderr=True)
        )

        os.remove(output_path)

    def process_videos(self, video_urls:list[str]):
        num_videos_processed = 0
        exceptions = []
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = []
            for video_url in video_urls:
                future = executor.submit(self._download_video, video_url)
                futures.append(future)
                for future in concurrent.futures.as_completed(futures):
                    try:
                        file_name = future.result()
                        self._modify_video(file_name)
                    except ffmpeg.Error as e:
                        exceptions.append(e)
                        print(f"FFmpeg error!\n{e.stderr.decode('utf-8')}\n")
                    except Exception as e:
                        raise
                        exceptions.append(e)
                        print(f"Error!\n{e}\n")
                    else:
                        num_videos_processed += 1
        return num_videos_processed, exceptions

    async def run(self, count):
        try:
            t1 = time()
            urls = await self.get_trending_videos(count)
            num_of_vid, exceptions = self.process_videos(urls)
            t2 = time()
            generate_report(
                num_of_vid, t2 - t1, exceptions, self._report_filename
            )
        except asyncio.CancelledError:
            return
        except Exception as e:
            raise
            print(f"Error!\n{e}\n")