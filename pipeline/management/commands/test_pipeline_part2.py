# pipeline/management/commands/test_pipeline_part2.py
from django.core.management.base import BaseCommand
from dotenv import load_dotenv
import os

# Importa os TRÊS serviços que vamos usar em sequência
from pipeline.services.buscador_praw import buscar_post_no_reddit
from pipeline.services.edge_tts import gerar_audio_sync
from pipeline.services.local_timestamps import gerar_timestamps_localmente

class Command(BaseCommand):
    help = 'Testa a pipeline de Reddit -> Áudio -> Legenda.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("--- INICIANDO TESTE INTEGRADO (REDDIT -> ÁUDIO -> LEGENDA) ---"))

        load_dotenv()

        # --- PASSO 1: BUSCAR O TEXTO ---
        self.stdout.write(self.style.HTTP_INFO("\n[ETAPA 1/3] Executando o serviço de busca no Reddit..."))
        texto_historia = buscar_post_no_reddit()
        if not texto_historia:
            self.stderr.write(self.style.ERROR("Falha ao obter o texto do Reddit. Pipeline interrompida."))
            return

        self.stdout.write(self.style.SUCCESS("Texto obtido com sucesso!"))

        # --- PASSO 2: GERAR O ÁUDIO ---
        self.stdout.write(self.style.HTTP_INFO("\n[ETAPA 2/3] Executando o serviço de geração de áudio (Edge TTS)..."))
        arquivo_audio = "audio_da_historia_completa.mp3"
        caminho_audio = gerar_audio_sync(texto_historia, arquivo_audio)
        if not caminho_audio:
            self.stderr.write(self.style.ERROR("Falha ao gerar o ficheiro de áudio. Pipeline interrompida."))
            return

        self.stdout.write(self.style.SUCCESS(f"Áudio gerado em: {caminho_audio}"))

        # --- PASSO 3: GERAR A LEGENDA ---
        self.stdout.write(self.style.HTTP_INFO("\n[ETAPA 3/3] Executando o serviço de legendagem local (Whisper.cpp)..."))
        arquivo_legenda = "legenda_da_historia.srt"
        caminho_legenda = gerar_timestamps_localmente(caminho_audio, arquivo_legenda)
        if not caminho_legenda:
            self.stderr.write(self.style.ERROR("Falha ao gerar o ficheiro de legenda. Pipeline interrompida."))
            return

        self.stdout.write(self.style.SUCCESS(f"Legenda gerada em: {caminho_legenda}"))

        # Limpa o ficheiro de áudio intermediário para não acumular lixo
        # if os.path.exists(caminho_audio):
        #     os.remove(caminho_audio)
        #     self.stdout.write(self.style.NOTICE(f"Ficheiro de áudio intermediário '{caminho_audio}' apagado."))

        self.stdout.write(self.style.SUCCESS(f"\n✅ TESTE INTEGRADO BEM-SUCEDIDO!"))
        self.stdout.write(f"O ficheiro final de legendas '{arquivo_legenda}' foi criado.")
        self.stdout.write(f"--- TESTE FINALIZADO ---")