# ong_app/views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password
from django.db import connection
from django.contrib import messages
from .models import Alumno
from .forms import UsuarioForm
from .forms import ActividadForm
from django.db.models import Count
from .models import Alumno, Usuario, Actividad, Nota
from django.utils.timezone import now
from django.shortcuts import get_object_or_404



def login_view(request):
    if request.method == 'POST':
        correo = request.POST.get('correo')
        contrasena = request.POST.get('contrasena')

        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT id_usuario, nombre, correo, contrasena, rol
                FROM Usuarios
                WHERE correo = %s
            """, [correo])
            row = cursor.fetchone()

        if row:
            id_usuario, nombre, correo_db, contrasena_hash, rol_db = row

            if check_password(contrasena, contrasena_hash):
                # Guardar datos en sesión
                request.session['usuario_id'] = id_usuario
                request.session['usuario_nombre'] = nombre
                request.session['usuario_rol'] = rol_db

                # Redirigir según rol
                if rol_db == 'Administrador':
                    return redirect('dashboard')
                elif rol_db == 'Maestro':
                    return redirect('inicio_maestro')
                elif rol_db == 'Psicologo':
                    return redirect('inicio_psicologo')
                else:
                    messages.error(request, 'Rol no válido.')
                    return redirect('login')
            else:
                messages.error(request, 'Contraseña incorrecta.')
        else:
            messages.error(request, 'Correo no registrado.')

    return render(request, 'ong_app/login.html')


def dashboard(request):
    if request.session.get('usuario_rol') != 'Administrador':
        return redirect('login')

    # Total de alumnos
    total_alumnos = Alumno.objects.count()

    # Maestros activos
    maestros_activos = Usuario.objects.filter(rol='Maestro').count()

    # Psicólogos
    psicologos = Usuario.objects.filter(rol='Psicologo').count()

    # Actividades asignadas este mes
    from django.utils.timezone import now
    mes_actual = now().month
    actividades_mes = Actividad.objects.filter(fecha_asignacion__month=mes_actual).count()

    # Distribución de alumnos por nivel (si tuvieras un campo 'nivel')
    # Aquí asumimos que 'diagnostico' indica el nivel como ejemplo
    distribucion_nivel = Alumno.objects.values('diagnostico').annotate(total=Count('id_alumno'))

    # Actividad más reciente
    actividad_reciente = Actividad.objects.order_by('-fecha_asignacion')[:5].values_list('descripcion', 'fecha_asignacion')

    context = {
        'usuario_nombre': request.session.get('usuario_nombre'),
        'total_alumnos': total_alumnos,
        'maestros_activos': maestros_activos,
        'psicologos': psicologos,
        'actividades_mes': actividades_mes,
        'distribucion_nivel': [(a['diagnostico'], a['total']) for a in distribucion_nivel],
        'actividad_reciente': actividad_reciente
    }
    
    return render(request, 'ong_app/dashboard.html', context)

# Logout
def logout_view(request):
    request.session.flush()  # Limpia toda la sesión
    return redirect('login')


def registrar_alumno(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        apellido = request.POST.get('apellido')
        fecha_nacimiento = request.POST.get('fecha_nacimiento')
        diagnostico = request.POST.get('diagnostico')
        id_responsable = request.POST.get('id_responsable')

        Alumno.objects.create(
            nombre=nombre,
            apellido=apellido,
            fecha_nacimiento=fecha_nacimiento,
            diagnostico=diagnostico,
            id_responsable=id_responsable or None
        )

        messages.success(request, 'Alumno registrado correctamente.')
        return redirect('registrar_alumno')

    return render(request, 'ong_app/registrar_alumno.html')

def registrar_usuarios(request):
    if request.method == 'POST':
        form = UsuarioForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Usuario registrado exitosamente.")
            return redirect('registrar_usuarios')
        else:
            messages.error(request, "⚠️ Corrige los errores antes de continuar.")
    else:
        form = UsuarioForm()

    return render(request, 'ong_app/registrar_usuarios.html', {'form': form})

def actividades(request):
    # Solo administradores pueden acceder
    if request.session.get('usuario_rol') != 'Administrador':
        messages.error(request, "⚠️ No tienes permisos para ver esta sección.")
        return redirect('login')

    # Obtener todas las actividades
    actividades_lista = Actividad.objects.select_related('id_alumno', 'id_usuario').order_by('-fecha_asignacion')

    # Opcional: filtrar por mes actual
    mes_actual = now().month
    actividades_mes = actividades_lista.filter(fecha_asignacion__month=mes_actual)

    context = {
        'usuario_nombre': request.session.get('usuario_nombre'),
        'actividades': actividades_lista,         # Todas las actividades
        'actividades_mes': actividades_mes.count() # Cantidad de actividades este mes
    }

    return render(request, 'ong_app/actividades.html', context)


def inicio_maestro(request):
    # 🔐 Verificación de rol
    if request.session.get('usuario_rol') != 'Maestro':
        messages.error(request, "⚠️ No tienes permisos para esta sección.")
        return redirect('login')

    # 🔹 Obtener el ID del maestro actual
    id_maestro = request.session.get('usuario_id')
    mes_actual = now().month

    # 🧍 Alumnos asignados al maestro (si no hay relación, lista todos)
    alumnos = Alumno.objects.all()
    total_alumnos = alumnos.count()

    # 📋 Actividades asignadas por el maestro
    actividades_todas = Actividad.objects.filter(id_usuario=id_maestro)
    actividades_recientes = actividades_todas.order_by('-fecha_asignacion')[:5]
    total_actividades = actividades_todas.count()

    # 🧾 Notas ingresadas por el maestro (este mes)
    try:
        notas_mes = Nota.objects.filter(
            id_maestro=id_maestro,
            fecha_registro__month=mes_actual
        ).count()
    except:
        notas_mes = 0  # Si aún no está el modelo Nota conectado

    # 🧠 Enviar todo al template
    context = {
        'usuario_nombre': request.session.get('usuario_nombre'),
        'alumnos': alumnos,
        'actividades_recientes': actividades_recientes,
        'total_alumnos': total_alumnos,
        'total_actividades': total_actividades,
        'notas_mes': notas_mes
    }

    return render(request, 'ong_app/inicio_maestro.html', context)


def inicio_psicologo(request):
    if request.session.get('usuario_rol') != 'Psicologo':
        messages.error(request, "⚠️ No tienes permisos para esta sección.")
        return redirect('login')

    # Datos relevantes para psicólogos
    actividades = Actividad.objects.filter(id_usuario=request.session['usuario_id']).order_by('-fecha_asignacion')

    context = {
        'usuario_nombre': request.session.get('usuario_nombre'),
        'actividades': actividades,
    }

    return render(request, 'ong_app/inicio_psicologo.html', context)



def registrar_alumno_maestro(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        apellido = request.POST.get('apellido')
        fecha_nacimiento = request.POST.get('fecha_nacimiento')
        diagnostico = request.POST.get('diagnostico')
        id_responsable = request.POST.get('id_responsable')

        Alumno.objects.create(
            nombre=nombre,
            apellido=apellido,
            fecha_nacimiento=fecha_nacimiento,
            diagnostico=diagnostico,
            id_responsable=id_responsable or None
        )

        messages.success(request, 'Alumno registrado correctamente.')
        return redirect('registrar_alumno_maestro')

    return render(request, 'ong_app/registrar_alumno_maestro.html')

def ver_alumno(request, id_alumno):
    if request.session.get('usuario_rol') not in ['Maestro', 'Administrador']:
        messages.error(request, "⚠️ No tienes permisos para acceder a esta sección.")
        return redirect('login')

    alumno = get_object_or_404(Alumno, id_alumno=id_alumno)

    if request.method == 'POST':
        # Actualización de datos del alumno
        alumno.nombre = request.POST.get('nombre')
        alumno.apellido = request.POST.get('apellido')
        alumno.fecha_nacimiento = request.POST.get('fecha_nacimiento')
        alumno.diagnostico = request.POST.get('diagnostico')
        alumno.save()
        messages.success(request, "✅ Información del alumno actualizada correctamente.")
        return redirect('ver_alumno', id_alumno=alumno.id_alumno)

    context = {
        'usuario_nombre': request.session.get('usuario_nombre'),
        'usuario_rol': request.session.get('usuario_rol'),
        'alumno': alumno
    }

    return render(request, 'ong_app/ver_alumno.html', context)

def eliminar_alumno(request, id_alumno):
    alumno = get_object_or_404(Alumno, id_alumno=id_alumno)
    
    if request.method == "POST":
        alumno.delete()
        messages.success(request, "Alumno eliminado correctamente.")
        return redirect('inicio_maestro')  # Redirige al dashboard del maestro
    
    return render(request, 'ong_app/eliminar_alumno.html', {'alumno': alumno})

def agregar_nota(request, id_alumno):
    alumno = get_object_or_404(Alumno, id_alumno=id_alumno)
    maestro_id = request.session.get('usuario_id')  # El maestro que está logueado

    if request.method == "POST":
        nota_valor = request.POST.get('nota')
        observaciones = request.POST.get('observaciones')

        if not nota_valor:
            messages.error(request, "Por favor ingresa una nota.")
        else:
            try:
                nota_float = float(nota_valor)
                if nota_float < 0 or nota_float > 100:
                    messages.warning(request, "La nota debe estar entre 0 y 100.")
                else:
                    Nota.objects.create(
                        id_alumno=alumno,
                        id_maestro_id=maestro_id,
                        nota=nota_float,
                        observaciones=observaciones
                    )
                    messages.success(request, "Nota agregada correctamente.")
                    return redirect('inicio_maestro')
            except ValueError:
                messages.error(request, "El valor ingresado no es válido.")

    return render(request, 'ong_app/agregar_nota.html', {'alumno': alumno})

def agregar_actividad(request, alumno_id):
    alumno = get_object_or_404(Alumno, id_alumno=alumno_id)
    maestro_id = request.session.get('usuario_id')  # ID del maestro logueado

    if request.method == 'POST':
        descripcion = request.POST.get('descripcion')
        tipo_actividad = request.POST.get('tipo_actividad')
        fecha_entrega = request.POST.get('fecha_entrega')

        if descripcion:
            actividad = Actividad(
                id_alumno=alumno,
                id_usuario_id=maestro_id,
                descripcion=descripcion,
                tipo_actividad=tipo_actividad,
                fecha_entrega=fecha_entrega,
                estado='Pendiente'
            )
            actividad.save(using='default')  # Guardar en la BD principal (SQL Server)
            messages.success(request, f'Actividad asignada correctamente a {alumno.nombre}.')
            return redirect('inicio_maestro')
        else:
            messages.error(request, 'Debes ingresar una descripción.')

    return render(request, 'ong_app/agregar_actividad.html', {'alumno': alumno})


def lista_actividades(request):
    # Solo maestros
    if request.session.get('usuario_rol') != 'Maestro':
        messages.error(request, "⚠️ No tienes permisos para esta sección.")
        return redirect('login')

    # Obtener todas las actividades creadas por este maestro
    actividades = Actividad.objects.filter(id_usuario=request.session['usuario_id']).order_by('-fecha_asignacion')

    context = {
        'usuario_nombre': request.session.get('usuario_nombre'),
        'actividades': actividades
    }
    return render(request, 'ong_app/listar_actividad.html', context)

def editar_actividad(request, id_actividad):
    actividad = get_object_or_404(Actividad, id_actividad=id_actividad)

    if request.method == 'POST':
        form = ActividadForm(request.POST, instance=actividad)
        if form.is_valid():
            form.save()
            messages.success(request, "Actividad actualizada correctamente.")
            return redirect('lista_actividades')
    else:
        form = ActividadForm(instance=actividad)

    context = {
        'form': form,
        'actividad': actividad
    }
    return render(request, 'ong_app/editar_actividad.html', context)

def eliminar_actividad(request, id_actividad):
    # Solo maestros pueden eliminar sus propias actividades
    if request.session.get('usuario_rol') != 'Maestro':
        messages.error(request, "⚠️ No tienes permisos para eliminar actividades.")
        return redirect('login')
    
    actividad = get_object_or_404(Actividad, id_actividad=id_actividad)

    # Opcional: verificar que la actividad pertenezca al maestro logueado
    if actividad.id_usuario.id_usuario != request.session.get('usuario_id'):
        messages.error(request, "⚠️ No puedes eliminar actividades de otro maestro.")
        return redirect('inicio_maestro')

    actividad.delete()
    messages.success(request, "✅ Actividad eliminada correctamente.")
    return redirect('inicio_maestro')