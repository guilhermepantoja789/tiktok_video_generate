# pipeline/services/edge_tts.py
import asyncio
import edge_tts

# Vozes em Português do Brasil: Francisca (feminina), Antonio (masculino)
VOICE = "pt-BR-AntonioNeural"


async def sintetizar_fala_edge(texto, nome_arquivo_saida):
    """
    Usa a biblioteca edge-tts para converter texto em áudio de alta qualidade.
    """
    print("-> Acessando o serviço Edge-TTS para gerar áudio...")
    try:
        comunicador = edge_tts.Communicate(texto, VOICE, rate="+10%")
        await comunicador.save(nome_arquivo_saida)
        print(f"✅ Áudio gerado com sucesso: '{nome_arquivo_saida}'")
        return nome_arquivo_saida
    except Exception as e:
        print(f"❌ Ocorreu um erro ao gerar o áudio com Edge-TTS: {e}")
        return None


def gerar_audio_sync(texto, nome_arquivo_saida):
    """
    Um 'wrapper' para chamar a função assíncrona a partir de código síncrono,
    como os nossos comandos Django.
    """
    # O asyncio.run executa a nossa função assíncrona e espera que ela termine
    return asyncio.run(sintetizar_fala_edge(texto, nome_arquivo_saida))