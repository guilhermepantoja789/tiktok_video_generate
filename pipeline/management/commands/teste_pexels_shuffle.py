# pipeline/management/commands/test_pexels_shuffle.py
from django.core.management.base import BaseCommand
from dotenv import load_dotenv

from pipeline.services.pexels_videos import buscar_video_pexels

class Command(BaseCommand):
    help = 'Testa a lógica de busca aleatória de vídeos no Pexels.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("--- INICIANDO TESTE DO SHUFFLE DE VÍDEOS PEXELS ---"))

        load_dotenv()

        termo_teste = "CGI animation"
        pasta_saida = "videos_teste_shuffle" # O vídeo será salvo numa pasta separada

        self.stdout.write(f"-> Buscando por um vídeo aleatório com o termo: '{termo_teste}'")

        # Chama o nosso serviço já atualizado com a lógica de shuffle
        caminho_video = buscar_video_pexels(termo_teste, pasta_saida)

        if caminho_video:
            self.stdout.write(self.style.SUCCESS(f"\n✅ TESTE BEM-SUCEDIDO!"))
            self.stdout.write(f"O vídeo aleatório foi baixado e salvo em: '{caminho_video}'")
            self.stdout.write(self.style.NOTICE("-> Execute o comando novamente para verificar se um vídeo DIFERENTE é baixado."))
        else:
            self.stderr.write(self.style.ERROR("\n❌ TESTE FALHOU. Veja as mensagens de erro no serviço Pexels."))

        self.stdout.write(self.style.SUCCESS("\n--- TESTE DO SHUFFLE FINALIZADO ---"))