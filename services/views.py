from datetime import timedelta

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.mixins import AccessMixin, LoginRequiredMixin
from django.db import models
from django.db.models import Count
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_http_methods
from django.views.generic import CreateView, DetailView, FormView, ListView, TemplateView, UpdateView

from .forms import (
    ContactRequestForm,
    ContactRequestUpdateForm,
    CustomerForm,
    CustomerNotesForm,
    FeedbackForm,
    OrderCommentForm,
    OrderFilterForm,
    OrderForm,
    OrderUpdateForm,
    ServicePriceCalculatorForm,
    SignUpForm,
)
from .models import ContactRequest, Customer, Feedback, Order, OrderComment, Service, User


class LandingPageView(TemplateView):
    """Landing page - главная страница сайта."""
    template_name = "services/landing.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Статистика компании
        context["total_customers"] = Customer.objects.count()
        context["total_orders"] = Order.objects.filter(status=Order.Status.DONE).count()
        # Годы работы (можно настроить в настройках или использовать дату создания первого заказа)
        first_order = Order.objects.order_by("created_at").first()
        if first_order:
            years_working = (timezone.now() - first_order.created_at).days // 365
            context["years_working"] = max(1, years_working)
        else:
            context["years_working"] = 1
        # Последние услуги для показа (максимум 3)
        context["featured_services"] = list(Service.objects.filter(is_active=True).order_by('id')[:3])
        # Услуги для футера (только 2)
        context["footer_services"] = Service.objects.filter(is_active=True)[:2]
        return context


class ServiceListView(ListView):
    model = Service
    template_name = "services/service_list.html"
    context_object_name = "services"

    def get_queryset(self):
        return Service.objects.filter(is_active=True)


class ServiceDetailView(DetailView):
    """Детальная страница услуги с расчетом цены."""
    model = Service
    template_name = "services/service_detail.html"
    context_object_name = "service"

    def get_queryset(self):
        return Service.objects.filter(is_active=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        service = self.get_object()
        
        # Форма для расчета цены (передаем тип цены для скрытия ненужных полей)
        calculator_form = ServicePriceCalculatorForm(price_type=service.price_type)
        calculated_price = None
        
        # Если форма отправлена, рассчитываем цену
        if self.request.method == "POST":
            calculator_form = ServicePriceCalculatorForm(self.request.POST, price_type=service.price_type)
            if calculator_form.is_valid():
                sqm = calculator_form.cleaned_data.get("sqm") or 0
                hours = calculator_form.cleaned_data.get("hours") or 0
                items = calculator_form.cleaned_data.get("items") or 0
                
                calculated_price = service.calculate_price(sqm=sqm, hours=hours, items=items)
        
        context["calculator_form"] = calculator_form
        context["calculated_price"] = calculated_price
        return context

    def post(self, request, *args, **kwargs):
        """Обработка POST запроса для расчета цены."""
        self.object = self.get_object()
        context = self.get_context_data()
        return self.render_to_response(context)


@require_http_methods(["GET", "POST"])
def logout_view(request):
    """Кастомный logout view, который правильно выходит и перенаправляет на страницу логина."""
    if request.user.is_authenticated:
        messages.info(request, _("Вы успешно вышли из системы."))
        logout(request)
    return redirect("services:login")


class OrderCreateView(LoginRequiredMixin, CreateView):
    template_name = "services/order_form.html"
    form_class = OrderForm
    success_url = reverse_lazy("services:dashboard")

    def get_initial(self):
        initial = super().get_initial()
        service_id = self.request.GET.get("service")
        if service_id:
            initial["service"] = service_id
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Получаем параметры расчета из GET-параметров
        service_id = self.request.GET.get("service")
        context["service_from_url"] = None
        if service_id:
            try:
                service = Service.objects.get(pk=service_id, is_active=True)
                context["service"] = service
                context["service_from_url"] = service
                # Получаем параметры расчета
                sqm = self.request.GET.get("sqm")
                hours = self.request.GET.get("hours")
                items = self.request.GET.get("items")
                calculated_price = self.request.GET.get("calculated_price")
                
                context["calculation_params"] = {
                    "sqm": sqm,
                    "hours": hours,
                    "items": items,
                    "calculated_price": calculated_price,
                }
            except Service.DoesNotExist:
                pass
        return context
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Если услуга передана через URL, ограничиваем выбор только этой услугой
        service_id = self.request.GET.get("service")
        if service_id:
            try:
                service = Service.objects.get(pk=service_id, is_active=True)
                # Ограничиваем queryset только этой услугой
                form.fields["service"].queryset = Service.objects.filter(pk=service_id, is_active=True)
                # Устанавливаем начальное значение
                form.initial["service"] = service_id
                # Если услуга БЕЗ фиксированной цены (с расчетом), делаем поле details обязательным
                # Но не показываем это визуально заранее - только при валидации
                if service.price_type != Service.PriceType.FIXED:
                    form.fields["details"].required = True
                    # Не добавляем атрибут required в HTML, чтобы валидация была только на сервере
            except Service.DoesNotExist:
                pass
        else:
            # Если услуга не передана через URL, добавляем JavaScript для динамической проверки
            # или делаем поле условно обязательным через валидацию формы
            pass
        return form

    def form_valid(self, form):
        form.instance.user = self.request.user
        
        # ВАЖНО: Проверяем, что услуга из формы соответствует услуге из URL
        service_id_from_url = self.request.GET.get("service") or self.request.POST.get("service_from_url")
        service_from_form = form.cleaned_data.get("service")
        
        # Если поле было disabled, оно не попадет в cleaned_data, берем из POST
        if not service_from_form and service_id_from_url:
            try:
                service_from_form = Service.objects.get(pk=service_id_from_url, is_active=True)
            except Service.DoesNotExist:
                form.add_error("service", _("Указанная услуга не найдена или неактивна"))
                return self.form_invalid(form)
        
        # Проверяем соответствие услуги из URL и формы
        if service_id_from_url and str(service_from_form.id) != str(service_id_from_url):
            form.add_error("service", _("Нельзя изменить услугу. Пожалуйста, вернитесь на страницу услуги и создайте заявку заново."))
            return self.form_invalid(form)
        
        service = service_from_form
        
        # ВАЖНО: Валидация соответствия параметров расчета типу услуги
        if not service:
            form.add_error("service", _("Услуга обязательна для заполнения"))
            return self.form_invalid(form)
        
        # Для услуг БЕЗ фиксированной цены (с расчетом) поле details обязательно
        if service.price_type != Service.PriceType.FIXED:
            details = form.cleaned_data.get("details", "").strip()
            if not details:
                form.add_error("details", _("Для услуг с расчетом цены необходимо указать детали заявки. Пожалуйста, опишите, что именно вам нужно."))
                return self.form_invalid(form)
        
        # Получаем параметры расчета из POST (приоритет) или GET
        sqm = self.request.POST.get("sqm") or self.request.GET.get("sqm")
        hours = self.request.POST.get("hours") or self.request.GET.get("hours")
        items = self.request.POST.get("items") or self.request.GET.get("items")
        calculated_price_param = self.request.POST.get("calculated_price") or self.request.GET.get("calculated_price")
        
        # Валидация: проверяем, что параметры расчета соответствуют типу услуги
        if service.price_type == Service.PriceType.PER_SQM:
            if not sqm:
                form.add_error(None, _("Для услуги с расчетом за м² необходимо указать площадь"))
                return self.form_invalid(form)
            if hours or items:
                form.add_error(None, _("Для данной услуги недопустимы параметры часов или единиц"))
                return self.form_invalid(form)
        elif service.price_type == Service.PriceType.PER_HOUR:
            if not hours:
                form.add_error(None, _("Для услуги с расчетом за час необходимо указать количество часов"))
                return self.form_invalid(form)
            if sqm or items:
                form.add_error(None, _("Для данной услуги недопустимы параметры площади или единиц"))
                return self.form_invalid(form)
        elif service.price_type == Service.PriceType.PER_ITEM:
            if not items:
                form.add_error(None, _("Для услуги с расчетом за единицу необходимо указать количество"))
                return self.form_invalid(form)
            if sqm or hours:
                form.add_error(None, _("Для данной услуги недопустимы параметры площади или часов"))
                return self.form_invalid(form)
        elif service.price_type == Service.PriceType.FIXED:
            if sqm or hours or items:
                form.add_error(None, _("Для услуги с фиксированной ценой недопустимы параметры расчета"))
                return self.form_invalid(form)
        
        # Валидация с разумными лимитами
        if sqm:
            try:
                sqm_float = float(sqm)
                if 0 <= sqm_float <= 1000000:  # Разумный лимит
                    form.instance.price_calculation_sqm = sqm_float
            except (ValueError, TypeError):
                pass
        
        if hours:
            try:
                hours_float = float(hours)
                if 0 <= hours_float <= 10000:  # Разумный лимит
                    form.instance.price_calculation_hours = hours_float
            except (ValueError, TypeError):
                pass
        
        if items:
            try:
                items_int = int(items)
                if 0 <= items_int <= 1000000:  # Разумный лимит
                    form.instance.price_calculation_items = items_int
            except (ValueError, TypeError):
                pass
        
        # Пересчитываем цену на сервере для безопасности
        # Это гарантирует, что пользователь не может подделать цену
        sqm_float = None
        hours_float = None
        items_int = None
        
        if sqm:
            try:
                sqm_float = float(sqm)
            except (ValueError, TypeError):
                pass
        
        if hours:
            try:
                hours_float = float(hours)
            except (ValueError, TypeError):
                pass
        
        if items:
            try:
                items_int = int(items)
            except (ValueError, TypeError):
                pass
        
        # Пересчитываем цену на основе реальных параметров услуги
        recalculated_price = service.calculate_price(
            sqm=sqm_float or 0,
            hours=hours_float or 0,
            items=items_int or 0
        )
        
        # Сохраняем пересчитанную цену (игнорируем переданную пользователем)
        form.instance.calculated_price = recalculated_price
        
        # Проверяем, что переданная цена (если есть) не сильно отличается от пересчитанной
        # Допускаем небольшую погрешность из-за округления
        if calculated_price_param:
            try:
                user_price = float(calculated_price_param)
                price_diff = abs(user_price - recalculated_price)
                # Если разница больше 1% или 1000 сум, это подозрительно
                if price_diff > max(recalculated_price * 0.01, 1000):
                    form.add_error(None, _("Обнаружено несоответствие в расчете цены. Пожалуйста, пересчитайте цену."))
                    return self.form_invalid(form)
            except (ValueError, TypeError):
                pass
        
        # Ensure customer profile is created/updated
        Customer.objects.matching_user(self.request.user, form.instance.service)
        messages.success(self.request, _("Заявка создана. Мы свяжемся с вами в ближайшее время."))
        return super().form_valid(form)


class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = "services/order_detail.html"
    context_object_name = "order"

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).select_related("service", "user", "feedback")


class DashboardView(LoginRequiredMixin, ListView):
    template_name = "services/dashboard.html"
    model = Order
    context_object_name = "orders"

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).select_related("service", "feedback").order_by("-created_at")


class FeedbackCreateView(LoginRequiredMixin, CreateView):
    model = Feedback
    form_class = FeedbackForm
    template_name = "services/feedback_form.html"

    def dispatch(self, request, *args, **kwargs):
        self.order = get_object_or_404(Order, pk=kwargs["pk"], user=request.user)
        if self.order.status != Order.Status.DONE:
            messages.error(request, _("Отзыв доступен после завершения заявки."))
            return redirect("services:order_detail", pk=self.order.pk)
        if hasattr(self.order, "feedback"):
            messages.info(request, _("Вы уже оставили отзыв для этой заявки."))
            return redirect("services:order_detail", pk=self.order.pk)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.order = self.order
        messages.success(self.request, _("Спасибо за обратную связь!"))
        response = super().form_valid(form)
        return response

    def get_success_url(self):
        return reverse("services:order_detail", kwargs={"pk": self.order.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["order"] = self.order
        return context


class SignUpView(FormView):
    template_name = "services/signup.html"
    form_class = SignUpForm
    success_url = reverse_lazy("services:login")

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        messages.success(self.request, _("Вы успешно зарегистрированы и вошли в систему."))
        return super().form_valid(form)


class OperatorOrAdminRequiredMixin(AccessMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if request.user.role not in [User.Role.ADMIN, User.Role.OPERATOR]:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)


# CRM Views
class CRMDashboardView(OperatorOrAdminRequiredMixin, ListView):
    template_name = "crm/dashboard.html"
    model = Order

    def get_queryset(self):
        return Order.objects.all().select_related("user", "service", "assigned_to", "customer", "feedback").order_by("-created_at")[:10]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Статистика заявок
        context["new_orders"] = Order.objects.filter(status=Order.Status.CREATED).count()
        context["in_progress_orders"] = Order.objects.filter(status=Order.Status.IN_PROGRESS).count()
        context["done_orders"] = Order.objects.filter(status=Order.Status.DONE).count()
        # Последние заявки
        context["recent_orders"] = Order.objects.all().select_related("user", "service", "customer").order_by("-created_at")[:10]
        # Новые клиенты (за последние 7 дней)
        week_ago = timezone.now() - timedelta(days=7)
        context["new_customers"] = Customer.objects.filter(created_at__gte=week_ago).order_by("-created_at")[:10]
        # Новые заявки обратной связи
        context["new_contact_requests"] = ContactRequest.objects.filter(status=ContactRequest.Status.NEW).count()
        context["recent_contact_requests"] = ContactRequest.objects.all().order_by("-created_at")[:5]
        return context


class CRMStatisticsView(OperatorOrAdminRequiredMixin, TemplateView):
    """Страница статистики для операторов и админов."""
    template_name = "crm/statistics.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from django.db.models import Count, Q, Avg
        from django.utils import timezone
        from datetime import timedelta

        now = timezone.now()
        today = now.date()
        week_ago = now - timedelta(days=7)
        month_ago = now - timedelta(days=30)
        year_ago = now - timedelta(days=365)

        # Статистика заявок
        context["total_orders"] = Order.objects.count()
        # Преобразуем статусы в переведенные значения
        from django.utils import translation
        orders_by_status_raw = Order.objects.values("status").annotate(count=Count("id")).order_by("status")
        # Создаем временные объекты для получения переведенных статусов
        status_choices_dict = {}
        for code, label in Order.Status.choices:
            # Активируем перевод для текущего языка
            status_choices_dict[code] = str(label)
        context["orders_by_status"] = [
            {
                "status": status_choices_dict.get(item["status"], item["status"]),
                "status_code": item["status"],
                "count": item["count"]
            }
            for item in orders_by_status_raw
        ]
        context["orders_today"] = Order.objects.filter(created_at__date=today).count()
        context["orders_week"] = Order.objects.filter(created_at__gte=week_ago).count()
        context["orders_month"] = Order.objects.filter(created_at__gte=month_ago).count()
        context["orders_year"] = Order.objects.filter(created_at__gte=year_ago).count()

        # Статистика по услугам
        context["popular_services"] = Service.objects.annotate(
            order_count=Count("orders")
        ).filter(order_count__gt=0).order_by("-order_count")[:10]

        # Статистика клиентов
        context["total_customers"] = Customer.objects.count()
        context["new_customers_today"] = Customer.objects.filter(created_at__date=today).count()
        context["new_customers_week"] = Customer.objects.filter(created_at__gte=week_ago).count()
        context["new_customers_month"] = Customer.objects.filter(created_at__gte=month_ago).count()

        # Статистика отзывов
        context["total_feedbacks"] = Feedback.objects.count()
        context["average_rating"] = Feedback.objects.aggregate(avg_rating=Avg("rating"))["avg_rating"] or 0
        context["feedbacks_by_rating"] = Feedback.objects.values("rating").annotate(count=Count("id")).order_by("rating")

        # Статистика заявок обратной связи
        context["total_contact_requests"] = ContactRequest.objects.count()
        # Преобразуем статусы в переведенные значения
        contact_requests_by_status_raw = ContactRequest.objects.values("status").annotate(count=Count("id")).order_by("status")
        contact_status_choices_dict = {}
        for code, label in ContactRequest.Status.choices:
            # Активируем перевод для текущего языка
            contact_status_choices_dict[code] = str(label)
        context["contact_requests_by_status"] = [
            {
                "status": contact_status_choices_dict.get(item["status"], item["status"]),
                "status_code": item["status"],
                "count": item["count"]
            }
            for item in contact_requests_by_status_raw
        ]
        context["contact_requests_today"] = ContactRequest.objects.filter(created_at__date=today).count()
        context["contact_requests_week"] = ContactRequest.objects.filter(created_at__gte=week_ago).count()

        # Статистика по операторам
        context["operators_stats"] = User.objects.filter(
            role__in=[User.Role.ADMIN, User.Role.OPERATOR]
        ).annotate(
            total_assigned=Count("assigned_orders"),
            total_completed=Count("assigned_orders", filter=Q(assigned_orders__status=Order.Status.DONE))
        ).order_by("-total_assigned")

        # Статистика по приоритетам
        context["orders_by_priority"] = Order.objects.values("priority").annotate(count=Count("id")).order_by("priority")

        # Динамика заявок за последние 30 дней
        daily_orders = []
        for i in range(30):
            date = today - timedelta(days=i)
            count = Order.objects.filter(created_at__date=date).count()
            daily_orders.append({"date": date, "count": count})
        context["daily_orders"] = reversed(daily_orders)

        return context


class CRMOrderListView(OperatorOrAdminRequiredMixin, ListView):
    template_name = "crm/orders_list.html"
    context_object_name = "orders"
    model = Order
    paginate_by = 20

    def get_queryset(self):
        queryset = Order.objects.select_related("user", "service", "assigned_to", "customer").order_by("-created_at")
        status = self.request.GET.get("status")
        priority = self.request.GET.get("priority")
        assigned_to = self.request.GET.get("assigned_to")
        phone = self.request.GET.get("phone") or self.request.GET.get("search")  # Поддержка обоих параметров

        if status:
            queryset = queryset.filter(status=status)
        if priority:
            queryset = queryset.filter(priority=priority)
        if assigned_to:
            queryset = queryset.filter(assigned_to__id=assigned_to)
        if phone:
            # Ищем в user.phone и customer.phone
            queryset = queryset.filter(
                models.Q(user__phone__icontains=phone) | models.Q(customer__phone__icontains=phone)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        operators = User.objects.filter(role__in=[User.Role.ADMIN, User.Role.OPERATOR])
        
        # Создаем форму с операторами и инициализируем её текущими GET-параметрами
        # Если есть параметр search, преобразуем его в phone для совместимости
        get_data = self.request.GET.copy()
        if "search" in get_data and "phone" not in get_data:
            get_data["phone"] = get_data["search"]
        
        filter_form = OrderFilterForm(
            operators=operators,
            data=get_data if get_data else None,
        )
        
        context["filter_form"] = filter_form
        context["operators"] = operators
        
        # Сохраняем querystring для пагинации (исключая page)
        querystring_parts = []
        for key, value in self.request.GET.items():
            if key != "page" and value:
                querystring_parts.append(f"{key}={value}")
        context["querystring"] = "&".join(querystring_parts)
        
        return context


class CRMOrderDetailView(OperatorOrAdminRequiredMixin, UpdateView):
    model = Order
    template_name = "crm/order_detail.html"
    context_object_name = "order"
    form_class = OrderUpdateForm

    def get_queryset(self):
        return Order.objects.select_related("user", "service", "assigned_to", "customer", "feedback").prefetch_related("comments__operator")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Передаем форму как order_form для шаблона
        if "form" in context:
            context["order_form"] = context["form"]
        else:
            order = self.get_object()
            context["order_form"] = OrderUpdateForm(
                instance=order,
                operator_queryset=User.objects.filter(role__in=[User.Role.ADMIN, User.Role.OPERATOR])
            )
        context["comment_form"] = OrderCommentForm()
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        action = request.POST.get("action")
        
        # Обработка добавления комментария
        if action == "add_comment":
            comment_form = OrderCommentForm(request.POST)
            if comment_form.is_valid():
                comment = comment_form.save(commit=False)
                comment.order = self.object
                comment.operator = request.user
                comment.save()
                messages.success(request, _("Комментарий добавлен."))
                return redirect("crm:order-detail", pk=self.object.pk)
            else:
                # Если форма комментария невалидна, показываем ошибки
                context = self.get_context_data()
                context["comment_form"] = comment_form
                return self.render_to_response(context)
        
        # Обработка обновления заявки
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, _("Заявка успешно обновлена."))
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("crm:order-detail", kwargs={"pk": self.object.pk})


class OrderCommentCreateView(OperatorOrAdminRequiredMixin, CreateView):
    model = OrderComment
    form_class = OrderCommentForm

    def form_valid(self, form):
        order = get_object_or_404(Order, pk=self.kwargs["pk"])
        form.instance.order = order
        form.instance.operator = self.request.user
        messages.success(self.request, _("Комментарий добавлен."))
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("crm:order-detail", kwargs={"pk": self.kwargs["pk"]})


class CRMCustomerListView(OperatorOrAdminRequiredMixin, ListView):
    model = Customer
    template_name = "crm/customers_list.html"
    context_object_name = "customers"
    paginate_by = 20

    def get_queryset(self):
        # Используем prefetch_related для оптимизации, но не annotate, чтобы избежать проблем с группировкой
        queryset = Customer.objects.all().prefetch_related("orders").order_by("-created_at")
        search = self.request.GET.get("phone") or self.request.GET.get("search")
        if search:
            queryset = queryset.filter(phone__icontains=search)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_term"] = self.request.GET.get("phone", "") or self.request.GET.get("search", "")
        return context


class CRMUsersListView(OperatorOrAdminRequiredMixin, ListView):
    """Список всех пользователей (Users), включая тех, у кого нет заказов или только один заказ."""
    model = User
    template_name = "crm/users_list.html"
    context_object_name = "users"
    paginate_by = 20

    def get_queryset(self):
        # Показываем всех пользователей с ролью USER (клиенты)
        # Используем select_related и prefetch_related для оптимизации
        queryset = User.objects.filter(role=User.Role.USER).select_related(
            "customer_profile"
        ).prefetch_related(
            "orders"
        ).annotate(
            orders_count=Count("orders")
        ).order_by("-date_joined")
        
        search = self.request.GET.get("phone") or self.request.GET.get("search")
        if search:
            queryset = queryset.filter(phone__icontains=search)
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_term"] = self.request.GET.get("phone", "") or self.request.GET.get("search", "")
        return context


class CRMCustomerDetailView(OperatorOrAdminRequiredMixin, UpdateView):
    model = Customer
    template_name = "crm/customer_detail.html"
    context_object_name = "customer"
    form_class = CustomerNotesForm

    def get_queryset(self):
        return Customer.objects.prefetch_related("orders__service", "orders__assigned_to")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        customer = self.get_object()
        # Получаем все заказы клиента
        context["orders"] = Order.objects.filter(customer=customer).select_related(
            "service", "assigned_to", "user"
        ).order_by("-created_at")
        return context

    def form_valid(self, form):
        messages.success(self.request, _("Данные клиента успешно обновлены."))
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("crm:customer-detail", kwargs={"pk": self.object.pk})


class ContactRequestCreateView(CreateView):
    """Страница для создания заявки обратной связи (доступна всем)."""
    model = ContactRequest
    form_class = ContactRequestForm
    template_name = "services/contact_request.html"
    success_url = reverse_lazy("services:contact_success")

    def form_valid(self, form):
        messages.success(self.request, _("Спасибо! Ваша заявка отправлена. Мы свяжемся с вами в ближайшее время."))
        return super().form_valid(form)


class ContactRequestSuccessView(TemplateView):
    """Страница успешной отправки заявки."""
    template_name = "services/contact_success.html"


class CRMContactRequestListView(OperatorOrAdminRequiredMixin, ListView):
    """Список заявок обратной связи в CRM."""
    model = ContactRequest
    template_name = "crm/contact_requests_list.html"
    context_object_name = "contact_requests"
    paginate_by = 20

    def get_queryset(self):
        queryset = ContactRequest.objects.all().order_by("-created_at")
        
        # Фильтры
        status = self.request.GET.get("status")
        if status:
            queryset = queryset.filter(status=status)
        
        assigned_to = self.request.GET.get("assigned_to")
        if assigned_to:
            queryset = queryset.filter(assigned_to_id=assigned_to)
        
        search = self.request.GET.get("search")
        if search:
            queryset = queryset.filter(
                models.Q(phone__icontains=search) |
                models.Q(email__icontains=search) |
                models.Q(telegram__icontains=search) |
                models.Q(instagram__icontains=search)
            )
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["status_filter"] = self.request.GET.get("status", "")
        context["assigned_filter"] = self.request.GET.get("assigned_to", "")
        context["search"] = self.request.GET.get("search", "")
        context["operators"] = User.objects.filter(role__in=[User.Role.ADMIN, User.Role.OPERATOR])
        return context


class CRMContactRequestDetailView(OperatorOrAdminRequiredMixin, UpdateView):
    """Детальная страница заявки обратной связи в CRM."""
    model = ContactRequest
    template_name = "crm/contact_request_detail.html"
    context_object_name = "contact_request"
    form_class = ContactRequestUpdateForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if "form" in context:
            context["update_form"] = context["form"]
        else:
            contact_request = self.get_object()
            context["update_form"] = ContactRequestUpdateForm(
                instance=contact_request,
                operator_queryset=User.objects.filter(role__in=[User.Role.ADMIN, User.Role.OPERATOR])
            )
        return context

    def form_valid(self, form):
        messages.success(self.request, _("Заявка обновлена."))
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("crm:contact-request-detail", kwargs={"pk": self.object.pk})
