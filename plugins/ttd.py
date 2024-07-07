import os
import asyncio
import concurrent.futures
import ffmpeg
from time import time
from TikTokApi import TikTokApi
from yt_dlp import YoutubeDL
from asyncstdlib.itertools import islice
from ffmpeg import Error
from pipeline.settings import *
from plugins.pdfm import generate_report


class TikTokDownloader:
    """
    Класс для загрузки и обработки видео с TikTok.
    """

    def init(self, output_folder, speed_ratio_int, resize_ratio_int, audio):
        self.output_folder = output_folder
        self.speed_ratio_int = speed_ratio_int
        self.resize_ratio_int = resize_ratio_int
        self.audio = audio

    async def get_trending_videos(self, count=10):
        """
        Получает список URL трендовых видео с TikTok.

        Args:
            count: Количество видео для получения.

        Returns:
            Список URL видео.
        """
        video_urls = []
        async with TikTokApi() as api:
            await api.create_sessions(
                ms_tokens=[ms_token], num_sessions=1, sleep_after=3
            )
            async for video in islice(api.trending.videos(count=count), 0, count):
                video_url = f"https://www.tiktok.com/@{video.author.username}/video/{video.id} "
                video_urls.append(video_url)
                print(
                    f"Video: {video_url}"
                    f"Username: {video.author.username}"
                    f"Video ID: {video.id}"
                )
        return video_urls

    def _download_video(self, video_url):
        """
        Загружает видео с заданного URL.

        Args:
            video_url: URL видео.

        Returns:
            Путь к загруженному видео.
        """
        ydl_opts = {
            "quiet": True,
            "outtmpl": f"{self.output_folder}/%(uploader)s_%(id)s_%(timestamp)s.%(ext)s",
        }
        ydl = YoutubeDL(ydl_opts)
        info_dict = ydl.extract_info(video_url, download=True)
        filename = ydl.prepare_filename(info_dict)
        return filename

    def _modify_video(self, video_path):
        """
        Изменяет скорость и размер видео.

        Args:
            video_path: Путь к видео.
        """
        output_path = os.path.join(
            self.output_folder, f"temp_{os.path.basename(video_path)}"
        )
        (
            ffmpeg
            .input(video_path)
            .filter("setpts", f"PTS/{self.speed_ratio_int}")
            .filter(
                "scale",
                f"trunc(iw*{self.resize_ratio_int}/2)*2",
                f"trunc(ih*{self.resize_ratio_int}/2)*2",
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

    def process_videos(self, video_urls):
        """
        Обрабатывает список видео, загружает, изменяет и возвращает результаты.

        Args:
            video_urls: Список URL видео.

        Returns:
            Кортеж, содержащий количество обработанных видео и список ошибок.
        """
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
                        print(f"FFmpeg error occurred: {e.stderr.decode('utf8')}")
                    except Exception as e:
                        exceptions.append(e)
                        print(f"An unexpected error occurred: {e}")
                    else:
                        num_videos_processed += 1
        return num_videos_processed, exceptions

        async def run(self, count):
            """
            Запускает загрузку, обработку и генерирует отчет.

            Args:
                count: Количество видео для обработки.
            """
            try:
                t1 = time()
                urls = await self.get_trending_videos(count)
                num_of_vid, exceptions = self.process_videos(urls)
                t2 = time()
                generate_report(
                    num_of_vid, t2 - t1, exceptions, report
                )  # Вызов метода generate_report из модуля pdfm
                print("All videos have been downloaded and modified.")
                print(f"Executed in {(t2 - t1):.4f}s")
            except asyncio.CancelledError:
                print("Asyncio task was cancelled.")
            except Exception as e:
                print(f"An error occurred: {e}")

if __name__ == "__main__":
        downloader = TikTokDownloader(
            output_folder, speed_ratio_int, resize_ratio_int, audio
        )
        asyncio.run(downloader.run(10))  # Запуск с 10 видео