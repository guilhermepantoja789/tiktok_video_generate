# pipeline/management/commands/test_edge_tts.py
from django.core.management.base import BaseCommand

# Importa a função do nosso novo serviço de áudio
from pipeline.services.edge_tts import gerar_audio_sync


class Command(BaseCommand):
    help = 'Testa o serviço de síntese de fala do Edge-TTS'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("--- INICIANDO TESTE DO SERVIÇO EDGE-TTS ---"))

        texto_teste = "Olá Alexsa e Clerdomy! O teste de conversão Texto-Áudio com o Edge TTS foi um sucesso!"
        arquivo_saida = "teste_audio_edge.mp3"

        # Chama a função do nosso serviço
        resultado = gerar_audio_sync(texto_teste, arquivo_saida)

        if resultado:
            self.stdout.write(self.style.SUCCESS(f"\n✅ TESTE BEM-SUCEDIDO!"))
            self.stdout.write(f"Ficheiro de áudio '{arquivo_saida}' foi criado na raiz do seu projeto.")
            self.stdout.write("Abra o ficheiro para verificar a narração.")
        else:
            self.stderr.write(self.style.ERROR("\n❌ TESTE FALHOU. Veja as mensagens de erro acima."))

        self.stdout.write(self.style.SUCCESS("\n--- TESTE DO SERVIÇO EDGE-TTS FINALIZADO ---"))