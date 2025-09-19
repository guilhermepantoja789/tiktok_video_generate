# pipeline/management/commands/test_reddit.py
from django.core.management.base import BaseCommand
from dotenv import load_dotenv

# Importa a função do nosso serviço que queremos testar
from pipeline.services.buscador_praw import buscar_post_no_reddit

class Command(BaseCommand):
    help = 'Testa o serviço de busca de histórias no Reddit (buscador_praw.py)'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("--- INICIANDO TESTE DO SERVIÇO DO REDDIT ---"))

        # Carrega as variáveis do arquivo .env para o ambiente de execução
        load_dotenv()

        # Chama a função do nosso serviço
        texto_da_historia = buscar_post_no_reddit()

        # Exibe o resultado no console
        if texto_da_historia:
            self.stdout.write(self.style.SUCCESS("\n✅ TESTE BEM-SUCEDIDO! Texto obtido:\n"))
            self.stdout.write("-------------------------------------------")
            self.stdout.write(texto_da_historia)
            self.stdout.write("-------------------------------------------")
        else:
            self.stderr.write(self.style.ERROR("\n❌ TESTE FALHOU. Veja as mensagens de erro acima."))

        self.stdout.write(self.style.SUCCESS("\n--- TESTE DO SERVIÇO DO REDDIT FINALIZADO ---"))