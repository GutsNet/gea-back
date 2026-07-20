from django.db import migrations, models

def migrar_roles_viejos_a_nuevos(apps, schema_editor):
    Usuario = apps.get_model('usuarios', 'Usuario')
    
    Usuario.objects.filter(rol="Root").update(rol="root")
    
    Usuario.objects.filter(rol="Administrativo").update(rol="admin")
    
    Usuario.objects.filter(rol="Estudiante").update(rol="user")

def revertir_roles_nuevos_a_viejos(apps, schema_editor):
    Usuario = apps.get_model('usuarios', 'Usuario')
    Usuario.objects.filter(rol="root").update(rol="Root")
    Usuario.objects.filter(rol="admin").update(rol="Administrativo")
    Usuario.objects.filter(rol="user").update(rol="Estudiante")


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0002_alter_usuario_cuatrimestre_alter_usuario_grupo'),
    ]

    operations = [
        migrations.RunPython(migrar_roles_viejos_a_nuevos, revertir_roles_nuevos_a_viejos),
        
        migrations.AlterField(
            model_name='usuario',
            name='rol',
            field=models.CharField(choices=[('root', 'Root'), ('admin', 'Admin'), ('user', 'User')], default='user', max_length=15, verbose_name='Rol'),
        ),
    ]
