# pipeline/services/buscador_praw.py
import os
import praw
import hashlib
import random  # <-- NOVO: Importa a biblioteca para sorteio
from django.db.models import Q
from pipeline.models import ProcessedPost


def buscar_post_no_reddit():
    """
    Busca posts no Reddit de um subreddit aleatório, limpa a formatação
    Markdown e retorna o primeiro que ainda não foi processado.
    """
    print("-> Acessando o serviço de busca no Reddit...")

    client_id = os.getenv("REDDIT_CLIENT_ID")
    client_secret = os.getenv("REDDIT_CLIENT_SECRET")
    user_agent = os.getenv("REDDIT_USER_AGENT")

    # --- INÍCIO DA MODIFICAÇÃO ---
    # Lista de subreddits para buscar histórias. Adicione ou remova conforme quiser!
    subreddits_para_buscar = [
        "EuSouOBabaca",
        "relatosdoreddit",
        "desabafos",
        "HistoriasdoReddit",
        "antitrampo",
        "conversas"
    ]
    # Sorteia um subreddit da lista para usar nesta execução
    subreddit_alvo = random.choice(subreddits_para_buscar)
    print(f"-> Subreddit escolhido para esta execução: r/{subreddit_alvo}")
    # --- FIM DA MODIFICAÇÃO ---

    if not all([client_id, client_secret, user_agent]):
        print("❌ ERRO: Credenciais do Reddit não configuradas.")
        return None

    try:
        reddit = praw.Reddit(client_id=client_id, client_secret=client_secret, user_agent=user_agent)
        subreddit = reddit.subreddit(subreddit_alvo)

        print(f"-> Buscando os 25 posts mais populares em r/{subreddit_alvo}...")
        for post in subreddit.hot(limit=25):
            if post.selftext and not post.stickied and len(post.selftext) > 2000:
                # Pega o texto cru
                titulo_cru = post.title.strip('"')
                corpo_cru = post.selftext

                # Lista de caracteres de formatação a remover
                caracteres_a_remover = ['*', '_', '#', '~~', '`']

                titulo_limpo = titulo_cru
                corpo_limpo = corpo_cru

                for char in caracteres_a_remover:
                    titulo_limpo = titulo_limpo.replace(char, '')
                    corpo_limpo = corpo_limpo.replace(char, '')

                texto_completo_limpo = f"{titulo_limpo}\n\n{corpo_limpo}"

                # Calcula o hash do conteúdo JÁ LIMPO
                computed_hash = hashlib.sha256(texto_completo_limpo.encode('utf-8')).hexdigest()

                if not ProcessedPost.objects.filter(Q(post_id=post.id) | Q(text_hash=computed_hash)).exists():
                    print(f"✅ Post novo encontrado: '{titulo_limpo}' (ID: {post.id})")
                    # Retorna os textos JÁ LIMPOS
                    return (post.id, titulo_limpo, corpo_limpo, computed_hash)
                else:
                    print(f"-> Ignorando post já processado (ID ou conteúdo duplicado): '{titulo_cru}'")

        print("❌ Nenhum post novo e adequado foi encontrado nos últimos 25.")
        return None

    except Exception as e:
        print(f"❌ Ocorreu um erro na comunicação com a API do Reddit: {e}")
        return None