from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.contrib.auth.hashers import make_password


class PerfilUsuario(models.Model):
    ROLES = [
        ('Administrador', 'Administrador'),
        ('Maestro', 'Maestro'),
        ('Psicologo', 'Psicologo'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    rol = models.CharField(max_length=20, choices=ROLES)

    def __str__(self):
        return f"{self.user.username} ({self.rol})"
    
    
class Alumno(models.Model):
    id_alumno = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    diagnostico = models.TextField(max_length=500, null=True, blank=True)
    id_responsable = models.IntegerField(null=True, blank=True)  # solo número, sin relación
    fecha_registro = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'Alumnos'

    def __str__(self):
        return f"{self.nombre} {self.apellido}"
    
class Usuario(models.Model):
    ROLES = [
        ('Administrador', 'Administrador'),
        ('Maestro', 'Maestro'),
        ('Psicologo', 'Psicólogo'),
    ]

    id_usuario = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    correo = models.EmailField(unique=True)
    contrasena = models.CharField(max_length=256)
    rol = models.CharField(max_length=20, choices=ROLES)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Hashea la contraseña si aún no está hasheada
        if not self.contrasena.startswith('pbkdf2_'):
            self.contrasena = make_password(self.contrasena)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nombre} ({self.rol})"
    
    class Meta:
        db_table = 'Usuarios'
        
        
class Actividad(models.Model):
    id_actividad = models.AutoField(primary_key=True, db_column='id_actividad')
    id_alumno = models.ForeignKey(
        Alumno, 
        on_delete=models.CASCADE, 
        db_column='id_alumno', 
        to_field='id_alumno'
    )
    id_usuario = models.ForeignKey(
        Usuario, 
        on_delete=models.CASCADE, 
        db_column='id_usuario', 
        to_field='id_usuario'
    )
    descripcion = models.TextField()
    tipo_actividad = models.CharField(max_length=50, null=True, blank=True)
    fecha_asignacion = models.DateTimeField(auto_now_add=True)
    fecha_entrega = models.DateTimeField(null=True, blank=True)
    estado = models.CharField(
        max_length=20, 
        default='Pendiente', 
        choices=[('Pendiente','Pendiente'),('Completada','Completada'),('Cancelada','Cancelada')]
    )

    class Meta:
        db_table = 'Actividades'
        managed = False

class Nota(models.Model):
    id_nota = models.AutoField(primary_key=True)
    id_alumno = models.ForeignKey('Alumno', on_delete=models.DO_NOTHING, db_column='id_alumno')
    id_maestro = models.ForeignKey('Usuario', on_delete=models.DO_NOTHING, db_column='id_maestro')
    nota = models.DecimalField(max_digits=5, decimal_places=2)
    observaciones = models.TextField(null=True, blank=True)
    fecha_registro = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'Notas'