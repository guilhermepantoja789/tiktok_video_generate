# pipeline/services/srt_to_ass_converter.py
import re

def converter_srt_para_ass(srt_path, ass_path):
    """
    Converte um ficheiro SRT para o formato ASS, injetando um estilo
    personalizado para garantir a centralização.
    """
    print(f"-> Convertendo '{srt_path}' para o formato ASS com estilo centralizado...")

    # --- DEFINIÇÃO DO ESTILO DA LEGENDA ---
    # Fontname, Fontsize, PrimaryColour, OutlineColour, ...
    # Alignment=5 é o centro exato (vertical e horizontal) no formato ASS.
    style_header = "[V4+ Styles]\n" \
                   "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n" \
                   "Style: Default,Arial,28,&H00FFFFFF,&H000000FF,&H80000000,&H80000000,0,0,0,0,100,100,0,0,1,2,1,5,10,10,10,1\n\n"

    events_header = "[Events]\n" \
                    "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"

    try:
        with open(srt_path, 'r', encoding='utf-8') as srt_file:
            srt_content = srt_file.read()

        ass_content = style_header + events_header

        # Converte cada bloco de legenda SRT para o formato de evento ASS
        blocks = srt_content.strip().split('\n\n')
        for block in blocks:
            if not block: continue
            lines = block.split('\n')
            if len(lines) < 3: continue

            # Converte o tempo de SRT (00:00:01,234) para ASS (0:00:01.23)
            time_line = lines[1].replace(',', '.')
            start_time, end_time = [t.strip() for t in time_line.split('-->')]
            start_time = f"0:{start_time}"
            end_time = f"0:{end_time}"

            # Junta o texto da legenda
            text = " ".join(lines[2:]).replace('\n', '\\N') # \N é quebra de linha em ASS

            ass_content += f"Dialogue: 0,{start_time},{end_time},Default,,0,0,0,,{text}\n"

        with open(ass_path, 'w', encoding='utf-8') as ass_file:
            ass_file.write(ass_content)

        print(f"✅ Ficheiro de legenda estilizado criado com sucesso: '{ass_path}'")
        return ass_path
    except Exception as e:
        print(f"❌ Erro ao converter SRT para ASS: {e}")
        return None