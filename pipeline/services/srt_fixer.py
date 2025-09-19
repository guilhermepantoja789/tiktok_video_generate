# pipeline/services/srt_fixer.py
import re
from datetime import datetime, timedelta

def _parse_srt_time(time_str):
    """Converte o tempo de uma legenda SRT para um objeto timedelta."""
    return datetime.strptime(time_str.replace(',', '.'), '%H:%M:%S.%f') - datetime(1900, 1, 1)

def _format_srt_time(td):
    """Formata um timedelta de volta para o formato de tempo SRT."""
    total_seconds = int(td.total_seconds())
    milliseconds = int(td.microseconds / 1000)
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"

def merge_and_offset_srt(file1_path, file2_path, offset_seconds, output_path):
    """
    Junta dois ficheiros SRT. Adiciona um offset de tempo a todos os
    tempos do segundo ficheiro.
    """
    print(f"-> Juntando legendas com um offset de {offset_seconds:.2f} segundos...")
    offset = timedelta(seconds=offset_seconds)

    with open(file1_path, 'r', encoding='utf-8') as f1, \
         open(file2_path, 'r', encoding='utf-8') as f2, \
         open(output_path, 'w', encoding='utf-8') as out_f:

        # Escreve o conteúdo do primeiro ficheiro diretamente
        out_f.write(f1.read())
        out_f.write("\n")

        last_index = int(re.findall(r'^(\d+)\s*$', f1.read().strip(), re.MULTILINE)[-1])

        # Processa o segundo ficheiro
        content2 = f2.read()
        blocks = content2.strip().split('\n\n')

        for i, block in enumerate(blocks):
            lines = block.split('\n')
            if len(lines) < 2: continue

            new_index = last_index + i + 1
            time_line = lines[1]
            text_lines = lines[2:]

            match = re.match(r'(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})', time_line)
            if match:
                start_str, end_str = match.groups()
                start_td = _parse_srt_time(start_str) + offset
                end_td = _parse_srt_time(end_str) + offset

                out_f.write(f"{new_index}\n")
                out_f.write(f"{_format_srt_time(start_td)} --> {_format_srt_time(end_td)}\n")
                out_f.write("\n".join(text_lines) + "\n\n")

    print(f"✅ Legendas unidas e sincronizadas com sucesso em '{output_path}'")
    return output_path