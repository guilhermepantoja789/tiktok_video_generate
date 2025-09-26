# pipeline/services/pexels_videos.py
import os
import requests
import random

# --- PASSO 1: LISTA DE TERMOS VIRAIS E CHAMATIVOS ---
# Adicionamos uma lista de termos de busca com alta chance de encontrar vídeos virais.
TERMOS_DE_BUSCA_VIRAL = [
    "abstract background",
    "satisfying loops",
    "particle animation",
    "nature footage",
    "ocean waves",
    "minecraft parkour",  # Exemplo de conteúdo de jogo
    "subway surfers gameplay",  # Exemplo de conteúdo de jogo
    "time lapse city",
    "galaxy animation",
    "tunnel background",
    "technology abstract",
    "forest aerial",
    "calm rain",
    "geometric patterns"
]


def _baixar_e_salvar_video(url, caminho_completo):
    """Função auxiliar para baixar um ficheiro de uma URL."""
    print(f"-> A baixar vídeo de {url} para: {caminho_completo}")
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


def _buscar_um_termo_na_pexels(termo_de_busca, headers):
    """
    Função interna que realiza a busca para UM ÚNICO termo.
    Retorna o link do vídeo se encontrar, ou None se falhar.
    """
    print(f"-> Tentando buscar por: '{termo_de_busca}'...")

    # Lógica de shuffle (busca em página aleatória) foi mantida
    pagina_aleatoria = random.randint(1, 10)
    resultados_por_pagina = 50

    params = {
        "query": termo_de_busca,
        "per_page": resultados_por_pagina,
        "orientation": "portrait",
        "page": pagina_aleatoria
    }

    try:
        response = requests.get("https://api.pexels.com/videos/search", headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        videos = data.get("videos", [])

        if not videos:
            print(f"🟡 Nenhum vídeo vertical encontrado para '{termo_de_busca}' na página {pagina_aleatoria}.")
            return None, None

        # Escolhe um vídeo aleatório da lista de resultados
        video_escolhido = random.choice(videos)
        video_id = video_escolhido.get("id")

        # Procura por um link de boa qualidade (Full HD ou HD)
        video_link = next(
            (f['link'] for f in video_escolhido.get('video_files', []) if f.get('quality') in ['fhd', 'hd']),
            None
        )

        if not video_link:
            print(f"🟡 Vídeo encontrado para '{termo_de_busca}', mas sem link de qualidade FHD/HD.")
            return None, None

        return video_link, video_id

    except requests.exceptions.RequestException as e:
        print(f"❌ Erro na comunicação com a API da Pexels para o termo '{termo_de_busca}': {e}")
        return None, None


# --- PASSO 2: FUNÇÃO PRINCIPAL COM LÓGICA DE FALLBACK ---
# Esta é a nova função que você deve chamar no seu pipeline.
def buscar_video_com_fallback(pasta_downloads):
    """
    Busca um vídeo na Pexels tentando vários termos de busca em ordem aleatória.
    Para no primeiro sucesso.
    """
    print("-> Acessando o serviço da Pexels com lógica de fallback...")
    api_key = os.getenv("PEXELS_API_KEY")
    if not api_key or "SUA_CHAVE" in api_key:
        print("❌ ERRO: Chave da API da Pexels não configurada no ficheiro .env")
        return None

    headers = {"Authorization": api_key}

    # Embaralha a lista de termos para que cada execução tente uma ordem diferente
    termos_embaralhados = random.sample(TERMOS_DE_BUSCA_VIRAL, len(TERMOS_DE_BUSCA_VIRAL))

    for termo in termos_embaralhados:
        video_link, video_id = _buscar_um_termo_na_pexels(termo, headers)

        if video_link and video_id:
            print(f"✅ Vídeo encontrado para o termo '{termo}'!")
            caminho_final = os.path.join(pasta_downloads, f"{termo.replace(' ', '_')}_{video_id}.mp4")

            if _baixar_e_salvar_video(video_link, caminho_final):
                print("✅ Vídeo de fundo baixado com sucesso.")
                return caminho_final
            else:
                # Se o download falhar, continua para o próximo termo
                print(f"🟡 Falha no download do vídeo para '{termo}'. Tentando próximo termo...")

    # Se o loop terminar sem encontrar nenhum vídeo
    print("❌ Nenhum vídeo encontrado para nenhum dos termos de busca. Verifique a API da Pexels ou os termos.")
    return None