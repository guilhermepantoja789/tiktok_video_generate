# pipeline/management/commands/create_video.py
import os
import re
import datetime
import subprocess
from django.core.management.base import BaseCommand
from dotenv import load_dotenv
from datetime import datetime, timedelta
import random

from pipeline.models import ProcessedPost
from pipeline.services.buscador_praw import buscar_post_no_reddit
from pipeline.services.corretor_gramatical import corrigir_texto
from pipeline.services.edge_tts import gerar_audio_sync
from pipeline.services.local_timestamps import gerar_timestamps_localmente
from pipeline.services.pexels_videos import buscar_video_pexels
from pipeline.services.video_renderer import renderizar_video


# --- FUNÇÕES AUXILIARES (sem alterações) ---
def get_audio_duration(file_path):
    if not os.path.exists(file_path):
        print(f"❌ Erro de duração: Ficheiro não encontrado em '{file_path}'");
        return 0.0
    command = ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of',
               'default=noprint_wrappers=1:nokey=1', file_path]
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        return float(result.stdout.strip())
    except Exception as e:
        print(f"❌ Erro ao obter a duração de '{file_path}': {e}");
        return 0.0


def _parse_srt_time(time_str):
    time_str = time_str.replace(',', '.');
    parts = time_str.split('.');
    time_str = parts[0] + '.' + parts[1][:3]
    return datetime.strptime(time_str, '%H:%M:%S.%f') - datetime(1900, 1, 1)


def _format_srt_time(td):
    total_seconds = int(td.total_seconds());
    milliseconds = int(td.microseconds / 1000)
    hours, remainder = divmod(total_seconds, 3600);
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"


def merge_and_offset_srt(srt_files_with_offsets, output_path):
    print("-> Juntando e sincronizando legendas...");
    final_content = "";
    total_index = 0
    for file_path, offset_seconds in srt_files_with_offsets:
        if not os.path.exists(file_path): continue
        offset = timedelta(seconds=offset_seconds)
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
        blocks = content.split('\n\n')
        for block in blocks:
            if not block: continue
            lines = block.split('\n');
            if len(lines) < 2: continue
            total_index += 1;
            time_line = lines[1];
            text_lines = "\n".join(lines[2:])
            match = re.match(r'(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})', time_line)
            if match:
                start_str, end_str = match.groups()
                start_td = _parse_srt_time(start_str) + offset;
                end_td = _parse_srt_time(end_str) + offset
                final_content += f"{total_index}\n{_format_srt_time(start_td)} --> {_format_srt_time(end_td)}\n{text_lines}\n\n"
    with open(output_path, 'w', encoding='utf-8') as out_f:
        out_f.write(final_content)
    print(f"✅ Legendas finais criadas: '{output_path}'");
    return output_path


class Command(BaseCommand):
    help = 'Executa a pipeline completa para criar um vídeo.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("🚀 INICIANDO A PIPELINE 🚀"))
        load_dotenv()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        pasta_de_trabalho = os.path.join("videos_gerados", timestamp)
        os.makedirs(pasta_de_trabalho, exist_ok=True)
        self.stdout.write(self.style.NOTICE(f"Pasta de trabalho: {pasta_de_trabalho}"))

        # PASSO 1: BUSCAR E CORRIGIR HISTÓRIA
        self.stdout.write(self.style.HTTP_INFO("\n[PASSO 1/7] Buscando e corrigindo história..."))
        resultado_reddit = buscar_post_no_reddit()
        if not resultado_reddit: self.stderr.write(self.style.ERROR("Pipeline encerrada.")); return
        post_id, titulo_historia, corpo_historia, text_hash = resultado_reddit
        corpo_historia_corrigido = corrigir_texto(corpo_historia)

        # DEFINIÇÃO DE CONTEÚDO
        texto_final_interativo = "E aí? Qual a opinião de vocês? Deixem nos comentários!"
        segmentos = [{'nome': 'titulo', 'texto': titulo_historia},
                     {'nome': 'historia', 'texto': corpo_historia_corrigido}]

        # PASSO 2: GERAR ÁUDIOS E LEGENDAS
        self.stdout.write(self.style.HTTP_INFO("\n[PASSO 2/7] Gerando áudios e legendas..."))
        for seg in segmentos:
            caminho_audio = os.path.join(pasta_de_trabalho, f"audio_{seg['nome']}.mp3")
            caminho_legenda = os.path.join(pasta_de_trabalho, f"legenda_{seg['nome']}.srt")
            seg['caminho_audio'] = gerar_audio_sync(seg['texto'], caminho_audio)
            seg['caminho_legenda'] = gerar_timestamps_localmente(caminho_audio, caminho_legenda)
            if not seg['caminho_audio'] or not seg['caminho_legenda']:
                self.stderr.write(self.style.ERROR(f"Pipeline encerrada na geração do segmento '{seg['nome']}'"));
                return

        caminho_audio_final_interativo = os.path.join(pasta_de_trabalho, "audio_final_interativo.mp3")
        gerar_audio_sync(texto_final_interativo, caminho_audio_final_interativo)

        # PASSO 3: UNIR ÁUDIOS
        self.stdout.write(self.style.HTTP_INFO("\n[PASSO 3/7] Combinando áudios..."))
        caminho_audio_final = os.path.join(pasta_de_trabalho, "narracao_final.mp3")
        caminho_efeito_sonoro = "efeito_sonoro.mp3"
        caminho_pausa = os.path.join(pasta_de_trabalho, "pausa.mp3")
        subprocess.run(
            ['ffmpeg', '-f', 'lavfi', '-i', 'anullsrc=r=48000', '-t', '1.5', '-q:a', '9', '-y', caminho_pausa],
            capture_output=True, check=True)
        caminho_pausa_curta = os.path.join(pasta_de_trabalho, "pausa_curta.mp3")
        subprocess.run(
            ['ffmpeg', '-f', 'lavfi', '-i', 'anullsrc=r=48000', '-t', '1.0', '-q:a', '9', '-y', caminho_pausa_curta],
            capture_output=True, check=True)
        concat_list_path = os.path.join(pasta_de_trabalho, "concat_list.txt")
        arquivos_para_unir = [caminho_efeito_sonoro, segmentos[0]['caminho_audio'], caminho_pausa,
                              segmentos[1]['caminho_audio'], caminho_pausa_curta, caminho_audio_final_interativo]
        with open(concat_list_path, 'w') as f:
            for arq in arquivos_para_unir: f.write(f"file '{os.path.abspath(arq)}'\n")
        comando_audio = ['ffmpeg', '-f', 'concat', '-safe', '0', '-i', concat_list_path, '-c', 'copy', '-y',
                         caminho_audio_final]
        try:
            subprocess.run(comando_audio, check=True, capture_output=True, text=True);
            self.stdout.write(self.style.SUCCESS("Áudio final criado."))
        except subprocess.CalledProcessError as e:
            self.stderr.write(self.style.ERROR(f"Erro ao combinar áudios: {e.stderr}"));
            return

        # PASSO 4: SINCORNIZAR LEGENDAS (REMOVIDO O TEXTO FINAL)
        self.stdout.write(self.style.HTTP_INFO("\n[PASSO 4/7] Sincronizando legendas..."))
        caminho_legenda_final = os.path.join(pasta_de_trabalho, "legendas_finais.srt")
        d_efeito = get_audio_duration(caminho_efeito_sonoro);
        d_titulo = get_audio_duration(segmentos[0]['caminho_audio']);
        d_pausa = 1.5
        srt_a_juntar = [(segmentos[0]['caminho_legenda'], d_efeito),
                        (segmentos[1]['caminho_legenda'], d_efeito + d_titulo + d_pausa)]
        merge_and_offset_srt(srt_a_juntar, caminho_legenda_final)

        # PASSO 5: BUSCAR VÍDEO DE FUNDO
        self.stdout.write(self.style.HTTP_INFO("\n[PASSO 5/7] Buscando vídeo de fundo (Pexels)..."))
        termos_de_busca_gameplay = ["abstract tunnel", "CGI animation", "fractal zoom", "endless road animation",
                                    "flying through clouds"]
        termo_escolhido = random.choice(termos_de_busca_gameplay)
        self.stdout.write(self.style.NOTICE(f"-> Termo de busca de vídeo escolhido: '{termo_escolhido}'"))
        caminho_video_base = buscar_video_pexels(termo_escolhido, pasta_de_trabalho)
        if not caminho_video_base: self.stderr.write(self.style.ERROR("Pipeline encerrada.")); return

        # PASSO 6: RENDERIZAR VÍDEO DA HISTÓRIA
        self.stdout.write(self.style.HTTP_INFO("\n[PASSO 6/8] Renderizando o vídeo da história..."))
        caminho_video_historia = os.path.join(pasta_de_trabalho, "video_historia.mp4")
        resultado_render = renderizar_video(caminho_video_base, caminho_audio_final, caminho_legenda_final,
                                            caminho_video_historia)
        if not resultado_render: self.stderr.write(self.style.ERROR("Pipeline encerrada.")); return

        # --- PASSO 7: ADICIONAR ANIMAÇÃO FINAL (COM MÉTODO SIMPLIFICADO) ---
        self.stdout.write(self.style.HTTP_INFO("\n[PASSO 7/8] Adicionando animação final..."))
        caminho_video_final_output = os.path.join(pasta_de_trabalho, "video_final.mp4")
        caminho_animacao = os.path.abspath("animacao.mov")

        if not os.path.exists(caminho_animacao):
            os.rename(caminho_video_historia, caminho_video_final_output)
            self.stdout.write(self.style.NOTICE("Animação não encontrada, usando vídeo da história como final."))
        else:
            try:
                # --- CORREÇÃO FINAL: REMOVEMOS A TEMPORIZAÇÃO PARA O TESTE ---
                # Este filtro irá sobrepor a animação desde o início do vídeo.
                filtro_overlay = f"[1:v][0:v]overlay=x=(W-w)/2:y=H-h-50"

                comando_overlay_string = (
                    f"ffmpeg -i \"{caminho_animacao}\" "
                    f"-i \"{caminho_video_historia}\" "
                    f"-filter_complex \"{filtro_overlay}\" "
                    f"-map 1:a -c:a copy "
                    f"-shortest "  # Usamos shortest para que o vídeo final tenha a duração da animação
                    f"-y \"{caminho_video_final_output}\""
                )

                self.stdout.write(self.style.NOTICE(f"-> EXECUTANDO COMANDO DE DIAGNÓSTICO: {comando_overlay_string}"))
                subprocess.run(comando_overlay_string, check=True, capture_output=True, text=True, shell=True)
                self.stdout.write(self.style.SUCCESS("Animação final adicionada com sucesso."))

            except Exception as e:
                self.stderr.write(self.style.ERROR(f"Erro ao adicionar animação: {e}"))
                if 'stderr' in dir(e): self.stderr.write(self.style.ERROR(f"Detalhes: {e.stderr}"))
                self.stderr.write(self.style.ERROR("Usando vídeo da história como final devido ao erro."));
                os.rename(caminho_video_historia, caminho_video_final_output)

        # PASSO 8: SALVAR REGISTO NO BANCO DE DADOS
        self.stdout.write(self.style.HTTP_INFO("\n[PASSO 8/8] Salvando registo do post no banco de dados..."))
        try:
            ProcessedPost.objects.create(post_id=post_id, text_hash=text_hash, title=titulo_historia,
                                         video_path=caminho_video_final_output)
            self.stdout.write(self.style.SUCCESS("Registo salvo! Este post não será usado novamente."))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Erro ao registar o post: {e}"))

        self.stdout.write(self.style.SUCCESS(f"\n🎉🎉🎉 PIPELINE CONCLUÍDA! 🎉🎉🎉"))
        self.stdout.write(self.style.SUCCESS(f"O seu vídeo está pronto em: {caminho_video_final_output}"))