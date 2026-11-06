
**General Notes**

An `onlinecourse` app has already been provided in this repo upon which you will be adding a new assesement feature.

- If you want to develop the final project on Theia hosted by [IBM Developer Skills Network](https://labs.cognitiveclass.ai/), you will need to create the same project structure on Theia workspace and save it everytime you close the browser
- Or you could develop the final project locally by setting up your own Python runtime and IDE
- Hints for the final project are left on source code files
- You may choose any cloud platform for deployment (default is IBM Cloud Foundry)
- Depends on your deployment, you may choose any SQL database Django supported such as SQLite3, PostgreSQL, and MySQL (default is SQLite3)

**ER Diagram**
For your reference, we have prepared the ER diagram design for the new assesement feature.

![Onlinecourse ER Diagram](https://github.com/ibm-developer-skills-network/final-cloud-app-with-database/blob/master/static/media/course_images/onlinecourse_app_er.png)

---

## Final Project: Assessment Feature (Completed)

This repository implements the IBM Skills Network final project assessment feature.

### Features

- `Question`, `Choice`, and `Submission` models with exact-answer scoring
- Admin registration and inline editing for all seven models
- Collapsible, CSRF-protected exam form on the course detail page
- `submit` and `show_exam_result` views with authentication, enrollment and
  submission-ownership checks
- Bootstrap exam result page with pass/fail messages and per-choice feedback
- 24 automated tests and a deterministic demo-data command

### Local setup

Use Python 3.8–3.12 (the pinned Django 4.2.3 / Pillow 10.0.0 releases do not
build on Python 3.13+).

```bash
python3.11 -m venv djangoenv
source djangoenv/bin/activate
pip install -U -r requirements.txt
python manage.py migrate
python manage.py seed_data
python manage.py runserver
```

### Demo credentials

| Account | Username | Password |
| --- | --- | --- |
| Django admin | `admin` | `p@ssword123` |
| Learner | `learner` | `p@ssword123` |

The learner is enrolled in **Learning Django**, whose single exam question is
*“Is Django a Python framework?”* (100 points, correct answer **Yes**).

### Verification

```bash
python manage.py makemigrations --check --dry-run
python manage.py migrate
python manage.py check
python manage.py test
```

Screenshots and verification output are in `submission_evidence/`.
