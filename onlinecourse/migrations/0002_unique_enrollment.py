from django.db import migrations, models


def deduplicate_enrollments(apps, schema_editor):
    Enrollment = apps.get_model('onlinecourse', 'Enrollment')
    Course = apps.get_model('onlinecourse', 'Course')
    seen = set()
    for enrollment in Enrollment.objects.order_by('id'):
        key = (enrollment.user_id, enrollment.course_id)
        if key in seen:
            enrollment.delete()
        else:
            seen.add(key)
    for course in Course.objects.all():
        course.total_enrollment = Enrollment.objects.filter(
            course_id=course.id
        ).count()
        course.save(update_fields=['total_enrollment'])


class Migration(migrations.Migration):
    dependencies = [
        ('onlinecourse', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(
            deduplicate_enrollments,
            migrations.RunPython.noop,
        ),
        migrations.AddConstraint(
            model_name='enrollment',
            constraint=models.UniqueConstraint(
                fields=('user', 'course'),
                name='unique_enrollment_user_course',
            ),
        ),
    ]
