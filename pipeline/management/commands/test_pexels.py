# pipeline/management/commands/test_pexels.py
from django.core.management.base import BaseCommand
from dotenv import load_dotenv

from pipeline.services.pexels_videos import buscar_video_pexels

class Command(BaseCommand):
    help = 'Testa o serviço de busca e download de vídeos da Pexels.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("--- INICIANDO TESTE DO SERVIÇO PEXELS ---"))

        load_dotenv()

        termo_teste = "natureza relaxante"
        pasta_saida = "videos_baixados" # O vídeo será salvo nesta pasta

        self.stdout.write(f"-> Buscando por um vídeo com o termo: '{termo_teste}'")
        caminho_video = buscar_video_pexels(termo_teste, pasta_saida)

        if caminho_video:
            self.stdout.write(self.style.SUCCESS(f"\n✅ TESTE BEM-SUCEDIDO!"))
            self.stdout.write(f"O vídeo foi baixado e salvo em: '{caminho_video}'")
        else:
            self.stderr.write(self.style.ERROR("\n❌ TESTE FALHOU. Veja as mensagens de erro acima."))

        self.stdout.write(self.style.SUCCESS("\n--- TESTE DO SERVIÇO PEXELS FINALIZADO ---"))