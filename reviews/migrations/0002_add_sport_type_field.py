from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='reviews',
            name='sport_type',
            field=models.CharField(
                max_length=20,
                choices=[
                    ('soccer', 'Soccer'),
                    ('tennis', 'Tennis'),
                    ('badminton', 'Badminton'),
                    ('futsal', 'Futsal'),
                    ('basket', 'Basket'),
                ],
                default='soccer',
            ),
        ),
    ]
