from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('app_registros', '0010_alter_marcasenal_numero_orden'),
    ]

    operations = [
        migrations.AddField(
            model_name='marcasenal',
            name='image_hash',
            field=models.CharField(
                max_length=128, blank=True, null=True,
                verbose_name='Hash perceptual de imagen_marca', db_index=True,
            ),
        ),
        migrations.AddField(
            model_name='imagenmarcapredefinida',
            name='image_hash',
            field=models.CharField(
                max_length=128, blank=True, null=True,
                verbose_name='Hash perceptual', db_index=True,
            ),
        ),
    ]