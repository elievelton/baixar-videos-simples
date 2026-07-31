import os
import shutil
from yt_dlp import YoutubeDL


class UniversalDownloader:

    def __init__(self):

        self.output = os.path.expanduser("~/Movies")

        os.makedirs(self.output, exist_ok=True)

        if shutil.which("ffmpeg") is None:
            raise Exception(
                "FFmpeg não encontrado.\n\nInstale com:\n\nbrew install ffmpeg"
            )

    def progress_hook(self, d):

        if d["status"] == "downloading":

            total = d.get("total_bytes") or d.get("total_bytes_estimate", 0)

            downloaded = d.get("downloaded_bytes", 0)

            if total:

                percent = downloaded / total * 100

                speed = d.get("speed")

                eta = d.get("eta")

                if speed:
                    speed = f"{speed/1024/1024:.2f} MB/s"
                else:
                    speed = "?"

                print(
                    f"\r{percent:6.2f}% | {speed} | ETA {eta}s",
                    end=""
                )

        elif d["status"] == "finished":

            print("\nDownload concluído.")

    def download(self, url, nome=None, apenas_audio=False):

        info_opts = {
            "quiet": True
        }

        with YoutubeDL(info_opts) as ydl:

            info = ydl.extract_info(url, download=False)

        titulo = info.get("title", "video")

        if not nome.strip():

            nome = titulo

        print(f"\nTítulo : {titulo}")

        print(f"Duração: {info.get('duration')} segundos")

        print(f"Uploader: {info.get('uploader')}")

        print()

        ydl_opts = {

            "outtmpl": os.path.join(
                self.output,
                f"{nome}.%(ext)s"
            ),

            "noplaylist": True,

            "merge_output_format": "mp4",

            "progress_hooks": [self.progress_hook],

            "concurrent_fragment_downloads": 5,

            "retries": 10,

            "fragment_retries": 10,

            "continuedl": True,

            "ignoreerrors": False,

            "quiet": False,

            "no_warnings": False,

            "http_chunk_size": 10485760,

            "format_sort": [
                "res",
                "fps",
                "codec:h264"
            ]
        }

        if apenas_audio:

            ydl_opts["format"] = "bestaudio"

            ydl_opts["postprocessors"] = [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192"
                }
            ]

        else:

            ydl_opts["format"] = (
                "bv*+ba/b"
            )

        with YoutubeDL(ydl_opts) as ydl:

            ydl.download([url])

        print("\nArquivo salvo em:")

        print(self.output)


def menu():

    print("=" * 50)

    print("Universal Video Downloader")

    print("=" * 50)

    url = input("\nURL: ")

    nome = input("Nome do arquivo (Enter = automático): ")

    audio = input("Somente áudio? (s/n): ").lower() == "s"

    downloader = UniversalDownloader()

    downloader.download(url, nome, audio)


if __name__ == "__main__":

    try:

        menu()

    except Exception as e:

        print("\nERRO:")

        print(e)