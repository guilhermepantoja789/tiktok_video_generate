# pipeline/models.py
from django.db import models

class ProcessedPost(models.Model):
    post_id = models.CharField(max_length=10, unique=True, help_text="O ID único do post do Reddit (ex: '1ab2cd')")
    # NOVO CAMPO ABAIXO
    text_hash = models.CharField(max_length=64, unique=True, db_index=True, help_text="Hash SHA-256 do conteúdo do texto para evitar duplicados")
    title = models.CharField(max_length=300, help_text="O título do post processado")
    video_path = models.CharField(max_length=500, blank=True, help_text="O caminho para o ficheiro de vídeo final gerado")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.post_id})"