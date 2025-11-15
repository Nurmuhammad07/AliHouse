from django import forms
from django.contrib.auth.forms import AuthenticationForm

from .models import Customer, Feedback, Order, OrderComment, Service, User


class PhoneAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        label="Телефон",
        widget=forms.TextInput(
            attrs={
                "placeholder": "+7 999 000 00 00",
                "class": "input",
                "autocomplete": "tel",
            }
        ),
    )


class SignUpForm(forms.ModelForm):
    password1 = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(attrs={"class": "input", "autocomplete": "new-password"}),
    )
    password2 = forms.CharField(
        label="Повторите пароль",
        widget=forms.PasswordInput(attrs={"class": "input", "autocomplete": "new-password"}),
    )

    class Meta:
        model = User
        fields = ("name", "phone")
        widgets = {
            "name": forms.TextInput(attrs={"class": "input", "placeholder": "Имя"}),
            "phone": forms.TextInput(attrs={"class": "input", "placeholder": "+7 999 000 00 00"}),
        }

    def clean_phone(self):
        raw_phone = self.cleaned_data["phone"]
        phone = "".join(ch for ch in raw_phone if ch.isdigit() or ch == "+")
        if User.objects.filter(phone=phone).exists():
            raise forms.ValidationError("Пользователь с таким телефоном уже есть.")
        return phone

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get("password1") != cleaned_data.get("password2"):
            self.add_error("password2", "Пароли не совпадают.")
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
            "service": "Услуга",
            "details": "Комментарий",
        }
        widgets = {
            "service": forms.Select(attrs={"class": "input"}),
            "details": forms.Textarea(attrs={"class": "input", "rows": 4, "placeholder": "Пожелания"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["service"].queryset = Service.objects.filter(is_active=True)


class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ("rating", "text")
        labels = {
            "rating": "Оценка (1-5)",
            "text": "Текст отзыва",
        }
        widgets = {
            "rating": forms.NumberInput(attrs={"class": "input", "min": 1, "max": 5}),
            "text": forms.Textarea(attrs={"class": "input", "rows": 4, "placeholder": "Расскажите о впечатлении"}),
        }


class OrderFilterForm(forms.Form):
    status = forms.ChoiceField(
        label="Статус",
        required=False,
        choices=[("", "Все статусы")] + list(Order.Status.choices),
        widget=forms.Select(attrs={"class": "input"}),
    )
    priority = forms.ChoiceField(
        label="Приоритет",
        required=False,
        choices=[("", "Все приоритеты")] + list(Order.Priority.choices),
        widget=forms.Select(attrs={"class": "input"}),
    )
    assigned_to = forms.ChoiceField(
        label="Оператор",
        required=False,
        choices=[("", "Все операторы")],
        widget=forms.Select(attrs={"class": "input"}),
    )
    phone = forms.CharField(
        label="Телефон клиента",
        required=False,
        widget=forms.TextInput(attrs={"class": "input", "placeholder": "+7 ..."}),
    )

    def __init__(self, *args, operators=None, **kwargs):
        super().__init__(*args, **kwargs)
        if operators is not None:
            self.fields["assigned_to"].choices += [(op.id, op.name or op.phone) for op in operators]


class OrderUpdateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ("status", "priority", "assigned_to", "internal_notes")
        widgets = {
            "status": forms.Select(attrs={"class": "input"}),
            "priority": forms.Select(attrs={"class": "input"}),
            "assigned_to": forms.Select(attrs={"class": "input"}),
            "internal_notes": forms.Textarea(attrs={"class": "input", "rows": 3}),
        }

    def __init__(self, *args, operator_queryset=None, **kwargs):
        super().__init__(*args, **kwargs)
        qs = operator_queryset or User.objects.filter(role__in=[User.Role.ADMIN, User.Role.OPERATOR])
        self.fields["assigned_to"].queryset = qs
        self.fields["assigned_to"].required = False


class OrderCommentForm(forms.ModelForm):
    class Meta:
        model = OrderComment
        fields = ("text",)
        widgets = {
            "text": forms.Textarea(attrs={"class": "input", "rows": 3, "placeholder": "Внутренний комментарий"}),
        }


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ("name", "phone", "notes")
        labels = {
            "name": "Имя",
            "phone": "Телефон",
            "notes": "Заметки",
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
        labels = {"notes": "Заметки"}
        widgets = {
            "notes": forms.Textarea(
                attrs={"class": "input", "rows": 4, "placeholder": "Контекст общения, важные детали"}
            ),
        }

