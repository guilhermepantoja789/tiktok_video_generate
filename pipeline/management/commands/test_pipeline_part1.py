# pipeline/management/commands/test_pipeline_part1.py
from django.core.management.base import BaseCommand
from dotenv import load_dotenv

# Importa as DUAS funções de serviço que vamos testar em conjunto
from pipeline.services.buscador_praw import buscar_post_no_reddit
from pipeline.services.edge_tts import gerar_audio_sync

class Command(BaseCommand):
    help = 'Testa a primeira parte da pipeline: busca um texto no Reddit e gera o áudio correspondente.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("--- INICIANDO TESTE INTEGRADO (REDDIT -> ÁUDIO) ---"))

        # Carrega as credenciais do .env (necessário para o PRAW/Reddit)
        load_dotenv()

        # --- PASSO 1: BUSCAR O TEXTO ---
        self.stdout.write(self.style.HTTP_INFO("\n[ETAPA 1/2] Executando o serviço de busca no Reddit..."))
        texto_historia = buscar_post_no_reddit()

        # Validação: Se o serviço do Reddit falhar, não podemos continuar.
        if not texto_historia:
            self.stderr.write(self.style.ERROR("Falha ao obter o texto do Reddit. Pipeline interrompida."))
            return

        self.stdout.write(self.style.SUCCESS("Texto obtido com sucesso!"))

        # --- PASSO 2: GERAR O ÁUDIO ---
        self.stdout.write(self.style.HTTP_INFO("\n[ETAPA 2/2] Executando o serviço de geração de áudio (Edge TTS)..."))
        arquivo_saida = "audio_da_historia_real.mp3"

        # A "magia" acontece aqui: passamos a variável 'texto_historia' da etapa 1
        # para o nosso serviço de geração de áudio.
        resultado_audio = gerar_audio_sync(texto_historia, arquivo_saida)

        # Validação: Se o serviço de áudio falhar.
        if not resultado_audio:
            self.stderr.write(self.style.ERROR("Falha ao gerar o ficheiro de áudio. Pipeline interrompida."))
            return

        self.stdout.write(self.style.SUCCESS(f"\n✅ TESTE INTEGRADO BEM-SUCEDIDO!"))
        self.stdout.write(f"O ficheiro '{arquivo_saida}' foi criado com a narração da história real do Reddit.")
        self.stdout.write(f"--- TESTE FINALIZADO ---")