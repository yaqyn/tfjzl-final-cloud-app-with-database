from datetime import date

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from onlinecourse.models import (
    Choice,
    Course,
    Enrollment,
    Instructor,
    Lesson,
    Question,
)


class Command(BaseCommand):
    help = 'Create deterministic demo data used by the final project evidence.'

    def handle(self, *args, **options):
        admin, _ = User.objects.get_or_create(
            username='admin',
            defaults={'email': '', 'is_staff': True, 'is_superuser': True},
        )
        admin.is_staff = True
        admin.is_superuser = True
        admin.set_password('p@ssword123')
        admin.save()

        learner, _ = User.objects.get_or_create(
            username='learner',
            defaults={'first_name': 'Alex', 'last_name': 'Learner'},
        )
        learner.first_name = 'Alex'
        learner.last_name = 'Learner'
        learner.set_password('p@ssword123')
        learner.save()

        instructor, _ = Instructor.objects.get_or_create(
            user=admin, defaults={'total_learners': 1},
        )

        course, _ = Course.objects.get_or_create(
            name='Learning Django',
            defaults={
                'image': 'course_images/django.png',
                'description': (
                    'Django is an extremely popular and fully featured '
                    'server-side web framework, written in Python'
                ),
                'pub_date': date.today(),
            },
        )
        course.image = course.image or 'course_images/django.png'
        course.description = (
            'Django is an extremely popular and fully featured '
            'server-side web framework, written in Python'
        )
        course.pub_date = course.pub_date or date.today()
        course.save()
        course.instructors.add(instructor)

        Lesson.objects.get_or_create(
            course=course,
            title='What is Django',
            defaults={
                'order': 0,
                'content': (
                    'Django is a high-level Python web framework that '
                    'encourages rapid development and clean, pragmatic '
                    'design. Built by experienced developers, it takes care '
                    'of much of the hassle of web development, so you can '
                    'focus on writing your app without needing to reinvent '
                    'the wheel.'
                ),
            },
        )

        question, _ = Question.objects.get_or_create(
            course=course,
            content='Is Django a Python framework?',
            defaults={'grade': 100},
        )
        question.grade = 100
        question.save()

        yes, _ = Choice.objects.get_or_create(
            question=question, content='Yes',
            defaults={'is_correct': True},
        )
        yes.is_correct = True
        yes.save()

        no, _ = Choice.objects.get_or_create(
            question=question, content='No',
            defaults={'is_correct': False},
        )
        no.is_correct = False
        no.save()

        Enrollment.objects.get_or_create(
            user=learner, course=course, defaults={'mode': 'honor'},
        )
        course.total_enrollment = Enrollment.objects.filter(
            course=course
        ).count()
        course.save()

        self.stdout.write(self.style.SUCCESS(
            'Seed data ready: admin/p@ssword123, learner/p@ssword123, '
            'course "Learning Django" (id=%s), question id=%s, '
            'correct choice id=%s, incorrect choice id=%s.'
            % (course.id, question.id, yes.id, no.id)
        ))
