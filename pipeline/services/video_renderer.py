# pipeline/services/video_renderer.py
import subprocess
import os


def renderizar_video(video_base, audio_narracao, legenda_srt, video_final):
    """
    Usa o FFmpeg com o filtro -vf simples e fiável. A posição da legenda é
    controlada por 'Alignment' e 'MarginV' para garantir consistência.
    """
    print("🎬 Iniciando a renderização final do vídeo (método simples e fiável)...")
    try:
        diretorio_de_trabalho = os.path.dirname(video_base)

        # Estilo focado na fiabilidade. Posição no terço inferior da tela.
        estilo_legenda = (
            f"FontName=Montserrat,"  # <-- FONTE ALTERADA PARA 'TIKTOK'
            f"FontSize=16,"  # Ajustei o tamanho para a nova fonte
            f"Alignment=2,"
            f"PrimaryColour=&H00FFFFFF,"
            f"OutlineColour=&H00000000,"  # Borda preta sólida
            f"BorderStyle=1,"
            f"Shadow=0,"
            f"Outline=2,"
            f"MarginV=110"
        )

        comando = [
            'ffmpeg',
            '-stream_loop', '-1',
            '-i', os.path.basename(video_base),
            '-i', os.path.basename(audio_narracao),
            '-vf', (
                f"scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
                f"subtitles={os.path.basename(legenda_srt)}:force_style='{estilo_legenda}'"
            ),
            '-map', '0:v',
            '-map', '1:a',
            '-c:v', 'libx264',
            '-preset', 'ultrafast',
            '-crf', '23',
            '-c:a', 'aac',
            '-shortest',
            '-y',
            os.path.basename(video_final)
        ]

        subprocess.run(comando, check=True, capture_output=True, text=True, cwd=diretorio_de_trabalho)

        print(f"✅ Vídeo final renderizado com sucesso: {video_final}")
        return video_final

    except subprocess.CalledProcessError as e:
        print("❌ Erro durante a renderização com FFmpeg.")
        print("Saída do FFmpeg (stderr):")
        print(e.stderr)
        return None
    except FileNotFoundError:
        print("❌ Erro: O comando 'ffmpeg' não foi encontrado.")
        return None