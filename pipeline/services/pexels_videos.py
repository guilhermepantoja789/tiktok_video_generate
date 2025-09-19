# pipeline/services/pexels_videos.py
import os
import requests
import random  # <-- Adicionamos a biblioteca random


def _baixar_e_salvar_video(url, caminho_completo):
    """Função auxiliar para baixar um ficheiro de uma URL."""
    print(f"-> A baixar vídeo para: {caminho_completo}")
    try:
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            os.makedirs(os.path.dirname(caminho_completo), exist_ok=True)
            with open(caminho_completo, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        return True
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro ao baixar o vídeo: {e}")
        return False


def buscar_video_pexels(termo_de_busca, pasta_downloads):
    """
    Busca e baixa um vídeo vertical aleatório de uma página aleatória da Pexels API.
    """
    print("-> Acessando o serviço da Pexels API com shuffle melhorado...")
    api_key = os.getenv("PEXELS_API_KEY")
    if not api_key or "SUA_CHAVE" in api_key:
        print("❌ ERRO: Chave da API da Pexels não configurada no ficheiro .env")
        return None

    headers = {"Authorization": api_key}

    # --- INÍCIO DA LÓGICA DE SHUFFLE ---
    pagina_aleatoria = random.randint(1, 10)  # Escolhe um número de página entre 1 e 10
    resultados_por_pagina = 50  # Pede 50 vídeos para ter uma boa seleção

    params = {
        "query": termo_de_busca,
        "per_page": resultados_por_pagina,
        "orientation": "portrait",
        "page": pagina_aleatoria
    }
    # --- FIM DA LÓGICA DE SHUFFLE ---

    try:
        response = requests.get("https://api.pexels.com/videos/search", headers=headers, params=params)
        response.raise_for_status()

        videos = response.json().get("videos", [])

        if videos:
            # --- SEGUNDA PARTE DO SHUFFLE ---
            # Em vez de pegar o primeiro (videos[0]), escolhemos um aleatoriamente da lista de 50
            video_escolhido = random.choice(videos)

            video_link = next((f['link'] for f in video_escolhido['video_files'] if f['quality'] in ['hd', 'fhd']),
                              None)

            if video_link:
                caminho_final = os.path.join(pasta_downloads,
                                             f"{termo_de_busca.replace(' ', '_')}_{video_escolhido['id']}.mp4")
                if _baixar_e_salvar_video(video_link, caminho_final):
                    print("✅ Vídeo de fundo aleatório baixado com sucesso.")
                    return caminho_final

        print(f"❌ Nenhum vídeo vertical encontrado para '{termo_de_busca}' na página {pagina_aleatoria}.")
        return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro na comunicação com a API da Pexels: {e}")
        return None