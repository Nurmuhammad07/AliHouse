from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import gettext_lazy as _

from .models import ContactRequest, Customer, Feedback, Order, OrderComment, Service, User


class PhoneAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        label=_("Телефон"),
        widget=forms.TextInput(
            attrs={
                "placeholder": "+998",
                "class": "input",
                "autocomplete": "tel",
            }
        ),
    )
    password = forms.CharField(
        label=_("Пароль"),
        widget=forms.PasswordInput(
            attrs={
                "class": "input",
                "autocomplete": "current-password",
            }
        ),
    )


class SignUpForm(forms.ModelForm):
    password1 = forms.CharField(
        label=_("Пароль"),
        widget=forms.PasswordInput(attrs={"class": "input", "autocomplete": "new-password"}),
    )
    password2 = forms.CharField(
        label=_("Повторите пароль"),
        widget=forms.PasswordInput(attrs={"class": "input", "autocomplete": "new-password"}),
    )

    class Meta:
        model = User
        fields = ("name", "phone")
        widgets = {
            "name": forms.TextInput(attrs={"class": "input", "placeholder": _("Имя")}),
            "phone": forms.TextInput(attrs={"class": "input", "placeholder": "+998"}),
        }

    def clean_phone(self):
        raw_phone = self.cleaned_data["phone"]
        phone = "".join(ch for ch in raw_phone if ch.isdigit() or ch == "+")
        if User.objects.filter(phone=phone).exists():
            raise forms.ValidationError(_("Пользователь с таким телефоном уже есть."))
        return phone

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get("password1") != cleaned_data.get("password2"):
            self.add_error("password2", _("Пароли не совпадают."))
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ("service", "details")
        labels = {
            "service": _("Услуга"),
            "details": _("Комментарий"),
        }
        widgets = {
            "service": forms.Select(attrs={"class": "input"}),
            "details": forms.Textarea(attrs={"class": "input", "rows": 4, "placeholder": _("Пожелания")}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["service"].queryset = Service.objects.filter(is_active=True)


class ServicePriceCalculatorForm(forms.Form):
    """Форма для расчета цены услуги."""
    sqm = forms.DecimalField(
        label=_("Площадь (м²)"),
        required=False,
        min_value=0,
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={"class": "input", "placeholder": _("Введите площадь"), "step": "0.01"}),
    )
    hours = forms.DecimalField(
        label=_("Количество часов"),
        required=False,
        min_value=0,
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={"class": "input", "placeholder": _("Введите количество часов"), "step": "0.5"}),
    )
    items = forms.IntegerField(
        label=_("Количество единиц"),
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={"class": "input", "placeholder": _("Введите количество")}),
    )

    def __init__(self, *args, price_type=None, **kwargs):
        super().__init__(*args, **kwargs)
        # Скрываем поля, которые не нужны для данного типа цены
        if price_type:
            if price_type != "per_sqm":
                self.fields["sqm"].widget = forms.HiddenInput()
            if price_type != "per_hour":
                self.fields["hours"].widget = forms.HiddenInput()
            if price_type != "per_item":
                self.fields["items"].widget = forms.HiddenInput()

    def clean(self):
        cleaned_data = super().clean()
        # Проверяем, что заполнено хотя бы одно поле
        if not any([cleaned_data.get("sqm"), cleaned_data.get("hours"), cleaned_data.get("items")]):
            raise forms.ValidationError(_("Заполните поле для расчета."))
        return cleaned_data


class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ("rating", "text")
        labels = {
            "rating": _("Оценка (1-5)"),
            "text": _("Текст отзыва"),
        }
        widgets = {
            "rating": forms.NumberInput(attrs={"class": "input", "min": 1, "max": 5}),
            "text": forms.Textarea(attrs={"class": "input", "rows": 4, "placeholder": _("Расскажите о впечатлении")}),
        }


class OrderFilterForm(forms.Form):
    status = forms.ChoiceField(
        label=_("Статус"),
        required=False,
        choices=[("", _("Все статусы"))] + list(Order.Status.choices),
        widget=forms.Select(attrs={"class": "input"}),
    )
    priority = forms.ChoiceField(
        label=_("Приоритет"),
        required=False,
        choices=[("", _("Все приоритеты"))] + list(Order.Priority.choices),
        widget=forms.Select(attrs={"class": "input"}),
    )
    assigned_to = forms.ChoiceField(
        label=_("Оператор"),
        required=False,
        choices=[("", _("Все операторы"))],
        widget=forms.Select(attrs={"class": "input"}),
    )
    phone = forms.CharField(
        label=_("Телефон клиента"),
        required=False,
        widget=forms.TextInput(attrs={"class": "input", "placeholder": "+998"}),
    )

    def __init__(self, *args, operators=None, **kwargs):
        super().__init__(*args, **kwargs)
        if operators is not None:
            self.fields["assigned_to"].choices += [(op.id, op.name or op.phone) for op in operators]


class OrderUpdateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ("status", "priority", "assigned_to", "internal_notes")
        labels = {
            "status": _("Статус"),
            "priority": _("Приоритет"),
            "assigned_to": _("Ответственный оператор"),
            "internal_notes": _("Внутренние заметки"),
        }
        widgets = {
            "status": forms.Select(attrs={"class": "input"}),
            "priority": forms.Select(attrs={"class": "input"}),
            "assigned_to": forms.Select(attrs={"class": "input"}),
            "internal_notes": forms.Textarea(attrs={"class": "input", "rows": 4, "placeholder": _("Внутренние заметки для операторов...")}),
        }

    def __init__(self, *args, operator_queryset=None, **kwargs):
        super().__init__(*args, **kwargs)
        qs = operator_queryset or User.objects.filter(role__in=[User.Role.ADMIN, User.Role.OPERATOR])
        self.fields["assigned_to"].queryset = qs
        self.fields["assigned_to"].required = False
        self.fields["assigned_to"].empty_label = _("Не назначен")


class OrderCommentForm(forms.ModelForm):
    class Meta:
        model = OrderComment
        fields = ("text",)
        widgets = {
            "text": forms.Textarea(attrs={"class": "input", "rows": 3, "placeholder": _("Внутренний комментарий")}),
        }


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ("name", "phone", "notes")
        labels = {
            "name": _("Имя"),
            "phone": _("Телефон"),
            "notes": _("Заметки"),
        }
        widgets = {
            "name": forms.TextInput(attrs={"class": "input"}),
            "phone": forms.TextInput(attrs={"class": "input"}),
            "notes": forms.Textarea(attrs={"class": "input", "rows": 5}),
        }


class CustomerNotesForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ("notes",)
        labels = {"notes": _("Заметки")}
        widgets = {
            "notes": forms.Textarea(
                attrs={"class": "input", "rows": 4, "placeholder": _("Контекст общения, важные детали")}
            ),
        }


class ContactRequestForm(forms.ModelForm):
    class Meta:
        model = ContactRequest
        fields = ("phone", "email", "telegram", "instagram", "message")
        labels = {
            "phone": _("Телефон"),
            "email": _("Email"),
            "telegram": _("Telegram"),
            "instagram": _("Instagram"),
            "message": _("Сообщение"),
        }
        widgets = {
            "phone": forms.TextInput(attrs={"class": "input", "placeholder": "+998", "required": True}),
            "email": forms.EmailInput(attrs={"class": "input", "placeholder": "email@example.com"}),
            "telegram": forms.TextInput(attrs={"class": "input", "placeholder": "@username"}),
            "instagram": forms.TextInput(attrs={"class": "input", "placeholder": "@username"}),
            "message": forms.Textarea(attrs={"class": "input", "rows": 5, "placeholder": _("Ваше сообщение...")}),
        }

    def clean_phone(self):
        raw_phone = self.cleaned_data["phone"]
        phone = "".join(ch for ch in raw_phone if ch.isdigit() or ch == "+")
        if not phone:
            raise forms.ValidationError(_("Укажите номер телефона."))
        return phone


class ContactRequestUpdateForm(forms.ModelForm):
    class Meta:
        model = ContactRequest
        fields = ("status", "assigned_to", "internal_notes")
        labels = {
            "status": _("Статус"),
            "assigned_to": _("Ответственный оператор"),
            "internal_notes": _("Внутренние заметки"),
        }
        widgets = {
            "status": forms.Select(attrs={"class": "input"}),
            "assigned_to": forms.Select(attrs={"class": "input"}),
            "internal_notes": forms.Textarea(attrs={"class": "input", "rows": 4, "placeholder": _("Внутренние заметки...")}),
        }

    def __init__(self, *args, operator_queryset=None, **kwargs):
        super().__init__(*args, **kwargs)
        qs = operator_queryset or User.objects.filter(role__in=[User.Role.ADMIN, User.Role.OPERATOR])
        self.fields["assigned_to"].queryset = qs
        self.fields["assigned_to"].required = False
        self.fields["assigned_to"].empty_label = _("Не назначен")

