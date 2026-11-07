from datetime import date

from django.contrib.admin.sites import site as admin_site
from django.contrib.auth.models import User
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.urls import reverse

from .models import (
    Course,
    Lesson,
    Instructor,
    Learner,
    Question,
    Choice,
    Submission,
    Enrollment,
)


class OnlineCourseTestBase(TestCase):
    def setUp(self):
        self.learner_user = User.objects.create_user(
            username='learner', password='p@ssword123',
            first_name='Alex', last_name='Learner',
        )
        self.other_user = User.objects.create_user(
            username='other', password='p@ssword123',
            first_name='Other', last_name='Learner',
        )
        self.instructor_user = User.objects.create_user(
            username='instructor', password='p@ssword123',
        )
        self.instructor = Instructor.objects.create(
            user=self.instructor_user, total_learners=1,
        )
        self.course = Course.objects.create(
            name='Learning Django',
            image='course_images/django.png',
            description=(
                'Django is an extremely popular and fully featured '
                'server-side web framework, written in Python'
            ),
            pub_date=date.today(),
        )
        self.course.instructors.add(self.instructor)
        self.lesson = Lesson.objects.create(
            title='What is Django',
            order=0,
            course=self.course,
            content='Django is a high-level Python web framework.',
        )
        self.enrollment = Enrollment.objects.create(
            user=self.learner_user, course=self.course, mode='honor',
        )
        self.question = Question.objects.create(
            course=self.course,
            content='Is Django a Python framework?',
            grade=100,
        )
        self.correct_choice = Choice.objects.create(
            question=self.question, content='Yes', is_correct=True,
        )
        self.incorrect_choice = Choice.objects.create(
            question=self.question, content='No', is_correct=False,
        )


class ModelTests(OnlineCourseTestBase):
    def test_course_and_lesson_relationships(self):
        self.assertEqual(self.course.lesson_set.count(), 1)
        self.assertEqual(self.course.question_set.count(), 1)
        self.assertEqual(self.question.choice_set.count(), 2)

    def test_is_get_score_accepts_exact_correct_answer(self):
        self.assertTrue(
            self.question.is_get_score({self.correct_choice.id})
        )

    def test_is_get_score_rejects_missing_correct_answer(self):
        self.assertFalse(self.question.is_get_score(set()))
        self.assertFalse(
            self.question.is_get_score({self.incorrect_choice.id})
        )

    def test_is_get_score_rejects_extra_incorrect_choice(self):
        self.assertFalse(self.question.is_get_score({
            self.correct_choice.id, self.incorrect_choice.id,
        }))

    def test_is_get_score_requires_all_correct_choices(self):
        second_correct = Choice.objects.create(
            question=self.question, content='Absolutely', is_correct=True,
        )
        self.assertFalse(
            self.question.is_get_score({self.correct_choice.id})
        )
        self.assertTrue(self.question.is_get_score({
            self.correct_choice.id, second_correct.id,
        }))
        self.assertFalse(self.question.is_get_score({
            self.correct_choice.id,
            second_correct.id,
            self.incorrect_choice.id,
        }))

    def test_submission_links_enrollment_and_choices(self):
        submission = Submission.objects.create(enrollment=self.enrollment)
        submission.choices.add(self.correct_choice)
        self.assertEqual(submission.enrollment, self.enrollment)
        self.assertIn(self.correct_choice, submission.choices.all())

    def test_user_cannot_enroll_in_the_same_course_twice(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            Enrollment.objects.create(
                user=self.learner_user,
                course=self.course,
                mode='audit',
            )


class AdminTests(TestCase):
    def test_all_seven_models_are_registered(self):
        for model in (
            Course, Lesson, Instructor, Learner,
            Question, Choice, Submission,
        ):
            self.assertIn(model, admin_site._registry)

    def test_question_admin_uses_choice_inline(self):
        from .admin import QuestionAdmin, ChoiceInline
        self.assertIn(ChoiceInline, admin_site._registry[Question].inlines)


class CourseDetailTemplateTests(OnlineCourseTestBase):
    def test_authenticated_user_sees_exam_and_choices(self):
        self.client.login(username='learner', password='p@ssword123')
        response = self.client.get(
            reverse('onlinecourse:course_details', args=(self.course.id,))
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Learning Django')
        self.assertContains(response, 'Start Exam')
        self.assertContains(response, 'Is Django a Python framework?')
        self.assertContains(response, 'choice_%s' % self.correct_choice.id)
        self.assertContains(response, "Yes")
        self.assertContains(response, "No")
        self.assertContains(response, 'csrfmiddlewaretoken')
        self.assertContains(
            response,
            reverse('onlinecourse:submit', args=(self.course.id,)),
        )
        self.assertContains(response, 'Submit')

    def test_anonymous_user_does_not_see_exam(self):
        response = self.client.get(
            reverse('onlinecourse:course_details', args=(self.course.id,))
        )
        self.assertNotContains(response, 'Start Exam')

    def test_course_name_and_lessons_are_displayed(self):
        response = self.client.get(
            reverse('onlinecourse:course_details', args=(self.course.id,))
        )
        self.assertContains(response, 'Learning Django')
        self.assertContains(response, 'What is Django')


class EnrollmentViewTests(OnlineCourseTestBase):
    def test_repeated_enrollment_is_idempotent_and_counted_once(self):
        self.client.login(username='other', password='p@ssword123')
        url = reverse('onlinecourse:enroll', args=(self.course.id,))

        first = self.client.get(url)
        second = self.client.get(url)

        self.assertEqual(first.status_code, 302)
        self.assertEqual(second.status_code, 302)
        self.assertEqual(
            Enrollment.objects.filter(
                user=self.other_user, course=self.course
            ).count(),
            1,
        )
        self.course.refresh_from_db()
        self.assertEqual(self.course.total_enrollment, 1)


class SubmitViewTests(OnlineCourseTestBase):
    def setUp(self):
        super().setUp()
        self.submit_url = reverse(
            'onlinecourse:submit', args=(self.course.id,)
        )

    def test_submit_requires_authentication(self):
        response = self.client.post(
            self.submit_url,
            {'choice_%s' % self.correct_choice.id: self.correct_choice.id},
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('onlinecourse:login'), response.url)

    def test_submit_requires_post(self):
        self.client.login(username='learner', password='p@ssword123')
        response = self.client.get(self.submit_url)
        self.assertEqual(response.status_code, 405)

    def test_submit_creates_submission_and_redirects(self):
        self.client.login(username='learner', password='p@ssword123')
        response = self.client.post(
            self.submit_url,
            {'choice_%s' % self.correct_choice.id: self.correct_choice.id},
        )
        submission = Submission.objects.get(enrollment=self.enrollment)
        self.assertRedirects(
            response,
            reverse(
                'onlinecourse:exam_result',
                args=(self.course.id, submission.id),
            ),
        )
        self.assertEqual(
            list(submission.choices.all()), [self.correct_choice]
        )

    def test_submit_requires_enrollment(self):
        self.client.login(username='other', password='p@ssword123')
        response = self.client.post(
            self.submit_url,
            {'choice_%s' % self.correct_choice.id: self.correct_choice.id},
        )
        self.assertEqual(response.status_code, 404)
        self.assertFalse(Submission.objects.exists())

    def test_submit_rejects_choice_from_another_course(self):
        other_course = Course.objects.create(
            name='Other Course',
            image='course_images/django.png',
            description='Another course',
            pub_date=date.today(),
        )
        other_question = Question.objects.create(
            course=other_course, content='Other question', grade=10,
        )
        foreign_choice = Choice.objects.create(
            question=other_question, content='Foreign', is_correct=True,
        )
        self.client.login(username='learner', password='p@ssword123')
        response = self.client.post(
            self.submit_url,
            {'choice_%s' % foreign_choice.id: foreign_choice.id},
        )
        self.assertEqual(response.status_code, 400)
        self.assertFalse(Submission.objects.exists())

    def test_submit_rejects_malformed_choice_value(self):
        self.client.login(username='learner', password='p@ssword123')
        response = self.client.post(
            self.submit_url, {'choice_bad': 'not-a-number'},
        )
        self.assertEqual(response.status_code, 400)
        self.assertFalse(Submission.objects.exists())


class ExamResultViewTests(OnlineCourseTestBase):
    def _submit(self, *choices):
        submission = Submission.objects.create(enrollment=self.enrollment)
        submission.choices.set(choices)
        return submission

    def test_exam_result_shows_congratulations_and_score(self):
        submission = self._submit(self.correct_choice)
        self.client.login(username='learner', password='p@ssword123')
        response = self.client.get(reverse(
            'onlinecourse:exam_result',
            args=(self.course.id, submission.id),
        ))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['grade'], 100)
        self.assertEqual(response.context['max_score'], 100)
        self.assertEqual(response.context['percentage'], 100)
        self.assertContains(response, 'Congratulations')
        self.assertContains(response, '100/100')
        self.assertContains(response, 'Learning Django')
        self.assertContains(response, 'Is Django a Python framework?')
        self.assertContains(response, 'Correct answer:')
        self.assertContains(response, 'Yes')

    def test_exam_result_scores_zero_with_extra_incorrect_choice(self):
        submission = self._submit(
            self.correct_choice, self.incorrect_choice,
        )
        self.client.login(username='learner', password='p@ssword123')
        response = self.client.get(reverse(
            'onlinecourse:exam_result',
            args=(self.course.id, submission.id),
        ))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['grade'], 0)
        self.assertContains(response, 'Failed')
        self.assertContains(response, '0/100')
        self.assertContains(response, 'Wrong answer:')
        self.assertContains(response, 'Re-test')

    def test_exam_result_shows_not_selected_warning(self):
        submission = self._submit(self.incorrect_choice)
        self.client.login(username='learner', password='p@ssword123')
        response = self.client.get(reverse(
            'onlinecourse:exam_result',
            args=(self.course.id, submission.id),
        ))
        self.assertContains(response, 'Not selected:')
        self.assertContains(response, 'Failed')

    def test_exam_result_requires_authentication(self):
        submission = self._submit(self.correct_choice)
        response = self.client.get(reverse(
            'onlinecourse:exam_result',
            args=(self.course.id, submission.id),
        ))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('onlinecourse:login'), response.url)

    def test_exam_result_blocks_other_learners_submission(self):
        submission = self._submit(self.correct_choice)
        self.client.login(username='other', password='p@ssword123')
        response = self.client.get(reverse(
            'onlinecourse:exam_result',
            args=(self.course.id, submission.id),
        ))
        self.assertEqual(response.status_code, 404)

    def test_exam_result_blocks_submission_from_another_course(self):
        submission = self._submit(self.correct_choice)
        other_course = Course.objects.create(
            name='Other Course',
            image='course_images/django.png',
            description='Another course',
            pub_date=date.today(),
        )
        self.client.login(username='learner', password='p@ssword123')
        response = self.client.get(reverse(
            'onlinecourse:exam_result',
            args=(other_course.id, submission.id),
        ))
        self.assertEqual(response.status_code, 404)


class UrlTests(TestCase):
    def test_named_routes_exist(self):
        self.assertEqual(
            reverse('onlinecourse:submit', args=(1,)),
            '/onlinecourse/1/submit/',
        )
        self.assertEqual(
            reverse('onlinecourse:exam_result', args=(1, 2)),
            '/onlinecourse/course/1/submission/2/result/',
        )
