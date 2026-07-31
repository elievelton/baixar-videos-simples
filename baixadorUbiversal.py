import os
import re
import shutil
import time

from yt_dlp import YoutubeDL


OUTPUT_PADRAO = os.path.expanduser("~/Movies")


# ---------------------------------------------------------


def banner():

    print("=" * 60)
    print(" Universal Video Downloader v1.1")
    print("=" * 60)


# ---------------------------------------------------------


def verificar_ffmpeg():

    if shutil.which("ffmpeg") is None:

        raise Exception(
            "\nFFmpeg não encontrado.\n\n"
            "Instale com:\n\n"
            "brew install ffmpeg\n"
        )


# ---------------------------------------------------------


def limpar_nome(nome):

    nome = re.sub(r'[\\/:*?"<>|]', "", nome)

    return nome.strip()


# ---------------------------------------------------------

# ---------------------------------------------------------

def escolher_nome_arquivo(info):

    titulo = limpar_nome(
        info.get("title", "video")
    )

    print()

    print("Título do vídeo:")

    print(titulo)

    alterar = input(
        "\nAlterar nome do arquivo? (s/N): "
    ).lower()

    if alterar != "s":

        return titulo

    while True:

        novo = input(
            "\nNovo nome: "
        ).strip()

        if novo:

            return limpar_nome(novo)

        print("O nome não pode ficar vazio.")


def formatar_tempo(segundos):

    if not segundos:

        return "--"

    h = segundos // 3600

    m = (segundos % 3600) // 60

    s = segundos % 60

    if h:

        return f"{h:02}:{m:02}:{s:02}"

    return f"{m:02}:{s:02}"


# ---------------------------------------------------------


def obter_info(url):

    with YoutubeDL({"quiet": True}) as ydl:

        return ydl.extract_info(url, download=False)


# ---------------------------------------------------------


def mostrar_info(info):

    titulo = info.get("title", "-")

    canal = info.get("uploader", "-")

    duracao = formatar_tempo(info.get("duration"))

    formatos = info.get("formats", [])

    altura = 0

    for f in formatos:

        h = f.get("height")

        if h:

            altura = max(altura, h)

    print("\n" + "-" * 60)

    print(f"Título    : {titulo}")

    print(f"Canal     : {canal}")

    print(f"Duração   : {duracao}")

    if altura:

        print(f"Qualidade : {altura}p")

    print("-" * 60)


# ---------------------------------------------------------


def escolher_formato():

    print()

    print("1 - Melhor qualidade")

    print("2 - 1080p")

    print("3 - 720p")

    print("4 - Apenas áudio")

    print("0 - Cancelar")

    while True:

        opcao = input("\nEscolha: ").strip()

        if opcao in ("0", "1", "2", "3", "4"):

            return opcao

        print("Opção inválida.")


# ---------------------------------------------------------


def escolher_pasta():

    print()

    print("Salvar em:")

    print()

    print(OUTPUT_PADRAO)

    alterar = input("\nAlterar pasta? (s/N): ").lower()

    if alterar != "s":

        os.makedirs(OUTPUT_PADRAO, exist_ok=True)

        return OUTPUT_PADRAO

    pasta = input("\nNova pasta: ").strip()

    pasta = os.path.expanduser(pasta)

    os.makedirs(pasta, exist_ok=True)

    return pasta

# ---------------------------------------------------------


def progress_hook(d):

    if d["status"] == "downloading":

        total = d.get("total_bytes") or d.get("total_bytes_estimate", 0)
        downloaded = d.get("downloaded_bytes", 0)

        if total:

            percent = downloaded / total * 100

            speed = d.get("speed")
            eta = d.get("eta")

            speed_str = (
                f"{speed / 1024 / 1024:.2f} MB/s"
                if speed else "?"
            )

            eta_str = f"{eta}s" if eta else "--"

            print(
                f"\r{percent:6.2f}% | {speed_str} | ETA {eta_str}",
                end="",
                flush=True,
            )

    elif d["status"] == "finished":

        print("\n\nMesclando arquivos...")


# ---------------------------------------------------------


def obter_formato(opcao):

    formatos = {

        "1": (
            "bv*[vcodec^=avc1]+ba[acodec^=mp4a]/"
            "b[vcodec^=avc1]/"
            "bv*+ba/b"
        ),

        "2": (
            "bestvideo[height<=1080][vcodec^=avc1]+"
            "bestaudio[acodec^=mp4a]/"
            "best[height<=1080]"
        ),

        "3": (
            "bestvideo[height<=720][vcodec^=avc1]+"
            "bestaudio[acodec^=mp4a]/"
            "best[height<=720]"
        ),

        "4": "bestaudio"

    }

    return formatos[opcao]


# ---------------------------------------------------------


def baixar(
    url,
    info,
    opcao,
    pasta,
    nome_arquivo,
):

    titulo = nome_arquivo

    playlist = info.get("_type") == "playlist"

    noplaylist = True

    if playlist:

        print()

        print("Playlist detectada.")

        escolha = input(
            "Baixar playlist inteira? (s/N): "
        ).lower()

        noplaylist = escolha != "s"

    ydl_opts = {

        "outtmpl": os.path.join(
            pasta,
            f"{titulo}.%(ext)s"
        ),

        "format": obter_formato(opcao),

        "merge_output_format": "mp4",

        "prefer_ffmpeg": True,

        "postprocessor_args": [
            "-movflags",
            "+faststart",
        ],

        "progress_hooks": [
            progress_hook
        ],

        "concurrent_fragment_downloads": 5,

        "continuedl": True,

        "fragment_retries": 10,

        "retries": 10,

        "ignoreerrors": False,

        "noplaylist": noplaylist,

        "quiet": False,

        "no_warnings": False,

    }

    if opcao == "4":

        ydl_opts["postprocessors"] = [

            {

                "key": "FFmpegExtractAudio",

                "preferredcodec": "mp3",

                "preferredquality": "192",

            }

        ]

    print()

    print("Iniciando download...\n")

    inicio = time.time()

    with YoutubeDL(ydl_opts) as ydl:

        ydl.download([url])

    fim = time.time()

    print()

    print("=" * 60)

    print("Download concluído!")

    print()

    print("Arquivo salvo em:")

    print(pasta)

    print()

    print(
        "Tempo total:",
        formatar_tempo(
            int(fim - inicio)
        )
    )

    print("=" * 60)


# ---------------------------------------------------------


def main():

    banner()

    verificar_ffmpeg()

    url = input("\nCole a URL:\n\n> ").strip()

    if not url:

        print("\nNenhuma URL informada.")

        return

    print("\nObtendo informações...")

    try:

        info = obter_info(url)

    except Exception:

        print("\nNão foi possível obter informações do vídeo.")

        return

    mostrar_info(info)
    nome_arquivo = escolher_nome_arquivo(info)

    opcao = escolher_formato()

    if opcao == "0":

        print("\nOperação cancelada.")

        return

    pasta = escolher_pasta()

    confirmar = input(
        "\nIniciar download? (S/n): "
    ).lower()

    if confirmar == "n":

        print("\nOperação cancelada.")

        return

    baixar(

    url,

    info,

    opcao,

    pasta,

    nome_arquivo,

)


# ---------------------------------------------------------


if __name__ == "__main__":

    try:

        main()

    except KeyboardInterrupt:

        print("\n\nOperação cancelada pelo usuário.")

    except Exception as e:

        print("\nERRO:")

        print(e)