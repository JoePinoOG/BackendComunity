from django.db import models

class Reunion(models.Model):
    MOTIVOS = [
        ('ORDINARIA', 'Ordinaria'),
        ('EXTRAORDINARIA', 'Extraordinaria'),
        ('INFORMATIVA', 'Informativa')
    ]
    
    titulo = models.CharField(max_length=200, default='Reunión sin título')
    fecha = models.DateTimeField()
    lugar = models.CharField(max_length=200)
    motivo = models.CharField(max_length=50, choices=MOTIVOS, default='ORDINARIA')

    class Meta:
        verbose_name_plural = "Reuniones"
        ordering = ['-fecha']

    def __str__(self):
        return f"{self.titulo} - {self.fecha.strftime('%d/%m/%Y')}"