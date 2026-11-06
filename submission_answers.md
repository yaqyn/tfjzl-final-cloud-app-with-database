# IBM Skills Network — Final Project Submission Answers

**Project:** Add a New Assessment Feature to an Online Course Application
**Repository:** https://github.com/yaqyn/tfjzl-final-cloud-app-with-database
**Starter repository:** https://github.com/ibm-developer-skills-network/tfjzl-final-cloud-app-with-database

## Q1 — `onlinecourse/models.py` (3 points)

https://github.com/yaqyn/tfjzl-final-cloud-app-with-database/blob/main/onlinecourse/models.py

Implements `Question` (course FK, content, grade, `is_get_score`), `Choice`
(question FK, content, `is_correct`), and `Submission` (enrollment FK, choices
M2M). Exact-answer scoring awards a question's grade only when the selected
choices match the full correct set, so extra incorrect choices score zero.

## Q2 — `onlinecourse/admin.py` (3 points)

https://github.com/yaqyn/tfjzl-final-cloud-app-with-database/blob/main/onlinecourse/admin.py

Imports and registers all seven models and defines `QuestionInline`,
`ChoiceInline`, `QuestionAdmin`, `CourseAdmin`, `LessonInline`, and
`LessonAdmin`.

## Q3 — Django admin site screenshot (1 point)

`submission_evidence/03-admin-site.png`

Genuine Chromium screenshot of the authenticated `/admin/` page after logging
in as `admin`. It shows both the **Authentication and Authorization** and
**OnlineCourse** sections. See `submission_evidence/verification.txt`.

## Q4 — Course detail template (2 points)

https://github.com/yaqyn/tfjzl-final-cloud-app-with-database/blob/main/onlinecourse/templates/onlinecourse/course_detail_bootstrap.html

The starter project actually renders `course_detail_bootstrap.html`
(singular), as configured by `CourseDetailView` in `views.py`. The template
shows the course name and lessons, then an authenticated-only **Start Exam**
button that expands a collapsible, CSRF-protected form containing every course
question and its choices as checkboxes. It submits to
`{% url 'onlinecourse:submit' course.id %}`.

## Q5 — `onlinecourse/views.py` (2 points)

https://github.com/yaqyn/tfjzl-final-cloud-app-with-database/blob/main/onlinecourse/views.py

Implements `submit(request, course_id)` and
`show_exam_result(request, course_id, submission_id)`. Submission requires an
authenticated, enrolled learner, validates that every submitted choice belongs
to the course, saves the submission, and redirects to the result route. Results
are restricted to the submission owner and score each question only when the
complete correct answer set is selected.

## Q6 — `onlinecourse/urls.py` (2 points)

https://github.com/yaqyn/tfjzl-final-cloud-app-with-database/blob/main/onlinecourse/urls.py

Adds the `submit` and `exam_result` routes under the `onlinecourse` namespace:
`<int:course_id>/submit/` and
`course/<int:course_id>/submission/<int:submission_id>/result/`.

## Q7 — Exam result screenshot (2 points)

`submission_evidence/07-final.png`

Genuine Chromium screenshot captured after an actual exam submission through
the running Django application. It shows **Congratulations, Alex!**, the score
**100/100**, the course **Learning Django**, the question, and the correct
answer **Yes** in green.

## Evidence and validation

| Item | Path |
| --- | --- |
| Admin screenshot | `submission_evidence/03-admin-site.png` |
| Course detail exam screenshot (extra) | `submission_evidence/04-course-detail-exam.png` |
| Final result screenshot | `submission_evidence/07-final.png` |
| Browser check log | `submission_evidence/verification.txt` |
| Rendered result HTML | `submission_evidence/exam_result_page.html` |

Validation performed on the real project:

```text
python3 manage.py makemigrations   -> onlinecourse/migrations/0001_initial.py
python3 manage.py migrate          -> applied successfully
python3 manage.py check            -> System check identified no issues
python3 manage.py test             -> Ran 24 tests ... OK
```

Demo accounts: `admin` / `p@ssword123` and `learner` / `p@ssword123`.
