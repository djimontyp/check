import logging
import random

from django.core.validators import FileExtensionValidator
from django.db import models
from core.tasks import generate_pdf

CHECK_TYPES = (
    ("kitchen", "Kitchen"),
    ("client", "Client"),
)

logger = logging.getLogger(__name__)


class Printer(models.Model):
    name = models.CharField(max_length=255, verbose_name="Назва принтеру")
    point_id = models.IntegerField(verbose_name="ID точки")
    api_key = models.CharField(
        max_length=255, unique=True, verbose_name="Ключ доступу до API"
    )
    check_type = models.CharField(
        max_length=7, choices=CHECK_TYPES, verbose_name="Тип чеку"
    )

    @staticmethod
    def print(check: "Check"):
        logger.info(f"Printing check {check.id}...")
        is_printed = random.randint(0, 1)
        if is_printed:
            print(f"""
            Check Information:
            --------------------
            ID:       {check.id}
            Type:     {check.type}
            Order:    {check.order}
            Status:   {check.status}
            PDF File: {check.pdf_file}
            --------------------
            """)
            return True
        else:
            print(f"Check {check.id} was not printed.")
            return False


class Check(models.Model):
    STATUS_TYPES = (
        ("new", "New"),
        ("rendered", "Rendered"),
        ("printed", "Printed"),
    )
    printer = models.ForeignKey(Printer, on_delete=models.CASCADE)
    type = models.CharField(max_length=7, choices=CHECK_TYPES, verbose_name="Тип чеку")
    order = models.JSONField(verbose_name="Замовлення")
    status = models.CharField(max_length=8, choices=STATUS_TYPES, verbose_name="Статус", default="new")
    pdf_generate_in_progress = models.BooleanField(default=False, verbose_name="В процесі")
    pdf_file = models.FileField(
        upload_to="pdf/",
        verbose_name="Файл чеку",
        validators=[
            FileExtensionValidator(["pdf"], message="Приймаються лише PDF-файли.")
        ],
        blank=True,
        null=True,
    )

    @property
    def ready_to_print(self):
        return self.status == "rendered" and self.pdf_file

    def start_generate_pdf(self):
        logger.info(f"Generating PDF for check {self.id}...")
        if self.pdf_generate_in_progress:
            logger.info(f"PDF generation for check {self.id} is already in progress.")
            return

        self.pdf_generate_in_progress = True
        self.save()
        generate_pdf.delay(self.id)

    def start_print(self):
        if self.ready_to_print:
            if self.printer.print(self):
                logger.info(f"Check {self.id} was printed.")
                self.status = "printed"
                self.save()
                return True
            else:
                logger.info(f"Check {self.id} was not printed.")
                return False
        else:
            logger.info(f"Check {self.id} is not ready to print.")
            return False
