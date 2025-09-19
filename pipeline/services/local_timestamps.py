# pipeline/services/local_timestamps.py
import subprocess
import os


def gerar_timestamps_localmente(caminho_audio, arquivo_srt_saida):
    """Usa o whisper.cpp local para gerar um ficheiro de legenda .srt a partir de um áudio."""
    print("-> Acessando o serviço local whisper.cpp para gerar legendas...")

    # --- CONFIGURAÇÃO ---
    # !! IMPORTANTE: Verifique se estes caminhos estão corretos para o seu computador !!
    caminho_whisper_cpp = "/home/guilherme-martins/Desktop/whisper.cpp/build/bin/whisper-cli"
    caminho_modelo_whisper = "/home/ti/projetos/var/whisper/models/ggml-medium.bin"
    # --------------------

    if not all(os.path.exists(p) for p in [caminho_whisper_cpp, caminho_modelo_whisper]):
        print("❌ ERRO: Caminho para o executável ou modelo do whisper.cpp não está correto.")
        print(f"   Verifique os caminhos dentro de 'pipeline/services/local_timestamps.py'")
        return None

    caminho_srt_gerado_pelo_whisper = f"{caminho_audio}.srt"

    try:
        comando = [
            caminho_whisper_cpp,
            '-m', caminho_modelo_whisper,
            '-f', caminho_audio,
            '-osrt',
            '-l', 'pt',
            '--max-len', '45',  # <-- REINTRODUZIDO: Limite máximo de 45 caracteres por linha
            '--split-on-word'
        ]

        print(f"-> Executando o whisper.cpp (isso pode demorar um pouco)...")

        # --- INÍCIO DA MODIFICAÇÃO ---
        # Obter as variáveis de ambiente atuais
        env = os.environ.copy()

        # Caminho para a primeira biblioteca (libwhisper.so.1) que já tínhamos
        caminho_biblioteca_whisper = "/home/guilherme-martins/Desktop/whisper.cpp/build/src"

        # !! Adicione aqui a PASTA que encontrar para a libggml.so !!
        caminho_biblioteca_ggml = "/home/guilherme-martins/Desktop/whisper.cpp/build/ggml/src/"  # <-- SUBSTITUA ESTA LINHA

        # Adiciona AMBAS as pastas ao path de busca, separadas por ':'
        # Isto garante que o Linux procura nos dois locais
        env[
            "LD_LIBRARY_PATH"] = f"{caminho_biblioteca_whisper}:{caminho_biblioteca_ggml}:{env.get('LD_LIBRARY_PATH', '')}"

        # Executa o subprocesso com o ambiente modificado
        subprocess.run(comando, check=True, capture_output=True, text=True, env=env)
        # --- FIM DA MODIFICAÇÃO ---

        if os.path.exists(caminho_srt_gerado_pelo_whisper):
            os.rename(caminho_srt_gerado_pelo_whisper, arquivo_srt_saida)
            print(f"✅ Legenda gerada com sucesso: '{arquivo_srt_saida}'")
            return arquivo_srt_saida
        else:
            print("❌ ERRO: O whisper.cpp não gerou o ficheiro .srt esperado.")
            return None

    except subprocess.CalledProcessError as e:
        print("❌ ERRO ao executar o whisper.cpp.");
        print(e.stderr)
        return None
    except FileNotFoundError:
        print(f"❌ ERRO: O executável do whisper.cpp não foi encontrado em '{caminho_whisper_cpp}'.")
        return None