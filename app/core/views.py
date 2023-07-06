from rest_framework import permissions
from rest_framework import viewsets

from core.models import Printer, Check
from core.serializers import (
    PrinterSerializer,
    ChecksSerializer
)


class PrinterViewSet(viewsets.ModelViewSet):
    queryset = Printer.objects.all()
    serializer_class = PrinterSerializer
    permission_classes = [permissions.IsAuthenticated]


class CheckViewSet(viewsets.ModelViewSet):
    queryset = Check.objects.all()
    serializer_class = ChecksSerializer
    permission_classes = [permissions.IsAuthenticated]
