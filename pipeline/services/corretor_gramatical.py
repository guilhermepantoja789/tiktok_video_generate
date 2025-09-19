# pipeline/services/corretor_gramatical.py
import os
import google.generativeai as genai

# Variável para guardar o modelo (será inicializado na primeira chamada)
model = None

def _initialize_model():
    """Função interna para inicializar o modelo na primeira utilização."""
    global model
    if model is None:
        try:
            # A biblioteca agora procura automaticamente por GOOGLE_API_KEY
            genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
            model = genai.GenerativeModel('gemini-1.5-flash')
            print("-> Modelo Gemini (gemini-1.5-flash) carregado com sucesso.")
        except Exception as e:
            print(f"❌ ERRO ao carregar o modelo Gemini. Verifique a sua chave de API. Erro: {e}")
            model = "failed" # Marca como falha para não tentar novamente

def corrigir_texto(texto):
    """Usa a API do Gemini para corrigir e refinar um texto para narração."""
    _initialize_model() # Garante que o modelo está inicializado

    if model is None or model == "failed":
        print("-> Modelo Gemini não está disponível. A saltar a etapa de correção.")
        return texto

    print("-> Enviando texto para o Gemini para correção e refinamento...")
    prompt = (
        "Você é um editor de roteiros para um canal de narração de histórias. "
        "Sua tarefa é pegar o texto a seguir, que foi extraído de um fórum da internet, e prepará-lo para ser lido em voz alta. "
        "Você deve fazer o seguinte:\n"
        "1. Corrija todos os erros de gramática, ortografia e pontuação.\n"
        "2. Reescreva frases que soem estranhas ou que sejam muito longas, para melhorar a clareza e a fluidez da narração.\n"
        "3. Adicione pontuação (vírgulas, pontos) para criar pausas naturais na fala.\n"
        "4. Mantenha o tom e a intenção original do autor (se for um desabafo, deve continuar a soar como um desabafo).\n"
        "5. NÃO adicione nenhum comentário, introdução ou conclusão sua. Apenas devolva o texto corrigido e refinado.\n\n"
        "Texto original:\n---\n"
        f"{texto}"
    )
    try:
        response = model.generate_content(prompt)
        texto_corrigido = response.text
        print("✅ Texto refinado pelo Gemini com sucesso.")
        return texto_corrigido
    except Exception as e:
        print(f"❌ Erro ao comunicar com a API do Gemini: {e}")
        return texto