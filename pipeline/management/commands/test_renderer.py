# pipeline/management/commands/test_renderer.py
import os
import subprocess
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Executa um teste de diagnóstico isolado no renderizador de vídeo FFmpeg.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("--- INICIANDO TESTE DE DIAGNÓSTICO DO RENDERIZADOR ---"))

        # --- Encontrar a pasta de trabalho mais recente ---
        base_dir = "videos_gerados"
        try:
            # Ordena as pastas por nome (que é a data/hora) e pega a última
            latest_folder = sorted([d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d))])[-1]
            pasta_de_trabalho = os.path.join(base_dir, latest_folder)
            self.stdout.write(f"Usando os ficheiros da pasta de trabalho: {pasta_de_trabalho}")
        except (FileNotFoundError, IndexError):
            self.stderr.write(self.style.ERROR(f"Nenhuma pasta de trabalho encontrada em '{base_dir}'."))
            self.stderr.write(self.style.ERROR("Por favor, execute 'python manage.py create_video' primeiro para gerar os ficheiros necessários."))
            return

        # --- Definir os caminhos dos ficheiros de teste ---
        legenda_srt = "legendas_finais.srt"
        caminho_legenda_completo = os.path.join(pasta_de_trabalho, legenda_srt)

        # Tenta encontrar o ficheiro de vídeo base que foi baixado
        video_base = next((f for f in os.listdir(pasta_de_trabalho) if f.endswith('.mp4') and f.startswith('dark_forest')), None)
        if not video_base:
            self.stderr.write(self.style.ERROR(f"Vídeo base (ex: 'dark_forest_...') não encontrado em '{pasta_de_trabalho}'."))
            return
        caminho_video_completo = os.path.join(pasta_de_trabalho, video_base)

        video_teste_saida = os.path.join(pasta_de_trabalho, "video_TESTE_RENDER.mp4")

        if not os.path.exists(caminho_legenda_completo):
            self.stderr.write(self.style.ERROR(f"Ficheiro de legenda '{caminho_legenda_completo}' não encontrado."))
            return

        # --- COMANDO FFmpeg SIMPLIFICADO ---
        self.stdout.write(self.style.HTTP_INFO("\nTentando renderizar com o comando mais simples possível..."))

        estilo_legenda = (
            f"FontName=Luckiest Guy,FontSize=28,Alignment=5,"
            f"PrimaryColour=&H00FFFFFF,OutlineColour=&H80000000,BorderStyle=1,Shadow=0,Outline=2"
        )

        # Este é o comando mais básico para queimar legendas, sem filtros complexos
        comando = [
            'ffmpeg',
            '-i', caminho_video_completo,
            '-vf', f"subtitles='{caminho_legenda_completo}':force_style='{estilo_legenda}'",
            '-y',
            video_teste_saida
        ]

        try:
            subprocess.run(comando, check=True, capture_output=True, text=True)
            self.stdout.write(self.style.SUCCESS(f"✅ VÍDEO DE TESTE GERADO COM SUCESSO em '{video_teste_saida}'"))
            self.stdout.write(self.style.SUCCESS("Por favor, verifique este ficheiro. Ele tem legendas? Estão centralizadas?"))
        except subprocess.CalledProcessError as e:
            self.stderr.write(self.style.ERROR("❌ O COMANDO DE RENDERIZAÇÃO SIMPLIFICADO FALHOU."))
            self.stderr.write("Isto indica um problema fundamental com a instalação do FFmpeg/libass ou com a fonte 'Luckiest Guy'.")
            self.stderr.write("Saída do FFmpeg:")
            self.stderr.write(e.stderr)