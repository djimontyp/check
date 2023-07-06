import codecs
import json

import requests
from celery import shared_task
from django.core.files.base import ContentFile
from django.template.loader import render_to_string


@shared_task
def check_new_checks():
    from core.models import Check

    new_checks = Check.objects.filter(status="new")
    [check.start_generate_pdf() for check in new_checks]
    return f"NewChecks scheduled: {new_checks}"


@shared_task
def print_ready_checks():
    from core.models import Check

    ready_checks = Check.objects.filter(status="rendered", pdf_file__isnull=False)

    check: Check
    [check.start_print() for check in ready_checks]
    return f"PrintChecks scheduled: {ready_checks}"


@shared_task
def generate_pdf(check_id):
    from core.models import Check

    check = Check.objects.get(id=check_id)
    try:
        html_template: str = render_to_string('check_template.html', {'check': check})

        url = 'http://pdf:80/'  # sorry, hardcode
        content = codecs.encode(html_template.encode("utf-8"), "base64").decode("utf-8")
        data = {'contents': content}
        headers = {'Content-Type': 'application/json'}
        response = requests.post(url, data=json.dumps(data), headers=headers)
        if response.status_code == 200:
            response: requests.Response
            pdf_file = ContentFile(response.content, name=f"{check.order['id']}_{check.type}.pdf")
            check.pdf_file.save(pdf_file.name, pdf_file)
            check.pdf_generate_in_progress = False
            check.status = "rendered"
            check.save()
            return f"PDF file generated for Check ID: {check.id}"
        else:
            return f"PDF generation failed for Check ID: {check.id}"
    except Exception as e:
        check.status = "new"
        check.pdf_generate_in_progress = False
        check.save()
        return f"PDF generation failed for Check ID: {check.id} with error: {e}"
