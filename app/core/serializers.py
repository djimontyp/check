from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from core.models import Printer, Check


class PrinterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Printer
        fields = ["name", "point_id", "api_key", "check_type"]


class CheckSerializer(serializers.ModelSerializer):
    class Meta:
        model = Check
        fields = ["order"]


class ChecksSerializer(serializers.Serializer):
    checks = CheckSerializer(many=True, read_only=True)
    order = serializers.JSONField(write_only=True)
    api_keys = serializers.ListField(child=serializers.CharField(), write_only=True)
    errors = serializers.ListField(read_only=True)

    class Meta:
        fields = ["checks", "order", "api_keys", "errors"]

    def create(self, validated_data):
        if not (api_keys := validated_data.pop("api_keys", [])):
            raise ValidationError("Не вказано жодного ключа API.")

        errors = []

        try:
            printers = Printer.objects.filter(api_key__in=api_keys)
            if not printers:
                errors.append("Немає жодного принтера для отриманих ключів API.")
                return {"errors": errors}

            order = validated_data.get("order")
            order_id = order.get("id")

            checks = []
            for printer in printers:
                check = Check.objects.filter(printer=printer, order__id=order_id).first()
                if check:
                    if check.status == "printed":
                        errors.append(f"Чек для замовлення {order_id} уже надруковано для принтера {printer.id}.")
                    else:
                        errors.append(f"Чек для замовлення {order_id} вже знаходиться у процесі створення для принтера {printer.check_type}.")
                else:
                    check = Check.objects.create(printer=printer, type=printer.check_type, order=order)
                    checks.append(check)

            if not any([checks, errors]):
                errors.append("Не вдалося створити жодного чеку.")
                return {"errors": errors}

            serialized_checks = CheckSerializer(checks, many=True).data

            return {"checks": serialized_checks, "errors": errors}

        except KeyError as e:
            errors.append("Не вказано номер замовлення.")
            return {"errors": errors}


