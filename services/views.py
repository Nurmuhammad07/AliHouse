from datetime import timedelta

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.mixins import AccessMixin, LoginRequiredMixin
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, DetailView, FormView, ListView, TemplateView, UpdateView
from django.views.decorators.http import require_http_methods

from .forms import CustomerForm, FeedbackForm, OrderCommentForm, OrderForm, OrderUpdateForm, SignUpForm
from .models import Customer, Order, OrderComment, Service, User


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
        # Последние услуги для показа
        context["featured_services"] = Service.objects.filter(is_active=True)[:3]
        # Услуги для футера (только 2)
        context["footer_services"] = Service.objects.filter(is_active=True)[:2]
        return context


class ServiceListView(ListView):
    model = Service
    template_name = "services/service_list.html"
    context_object_name = "services"

    def get_queryset(self):
        return Service.objects.filter(is_active=True)


@require_http_methods(["GET", "POST"])
def logout_view(request):
    """Кастомный logout view, который правильно выходит и перенаправляет на страницу логина."""
    if request.user.is_authenticated:
        messages.info(request, "Вы успешно вышли из системы.")
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

    def form_valid(self, form):
        form.instance.user = self.request.user
        # Ensure customer profile is created/updated
        Customer.objects.matching_user(self.request.user, form.instance.service)
        messages.success(self.request, "Заявка создана. Мы свяжемся с вами в ближайшее время.")
        return super().form_valid(form)


class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = "services/order_detail.html"
    context_object_name = "order"

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).select_related("service", "user", "feedback")


class DashboardView(LoginRequiredMixin, ListView):
    model = Order
    template_name = "services/dashboard.html"
    context_object_name = "orders"

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).select_related("service", "feedback")


class FeedbackCreateView(LoginRequiredMixin, CreateView):
    template_name = "services/feedback_form.html"
    form_class = FeedbackForm

    def dispatch(self, request, *args, **kwargs):
        self.order = get_object_or_404(Order, pk=kwargs["pk"], user=request.user)
        if self.order.status != Order.Status.DONE:
            messages.error(request, "Отзыв доступен после завершения заявки.")
            return redirect("services:order_detail", pk=self.order.pk)
        if hasattr(self.order, "feedback"):
            messages.info(request, "Отзыв для этой заявки уже существует.")
            return redirect("services:order_detail", pk=self.order.pk)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.order = self.order
        messages.success(self.request, "Спасибо за обратную связь!")
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
    success_url = reverse_lazy("services:dashboard")

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        messages.success(self.request, "Аккаунт создан. Добро пожаловать!")
        return super().form_valid(form)


class OperatorOrAdminRequiredMixin(AccessMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if request.user.role not in [User.Role.OPERATOR, User.Role.ADMIN]:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)


# CRM Views
class CRMDashboardView(OperatorOrAdminRequiredMixin, ListView):
    template_name = "crm/dashboard.html"
    model = Order

    def get_queryset(self):
        return Order.objects.all().select_related("user", "service", "assigned_to", "customer").order_by("-created_at")[:10]

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
        return context


class CRMOrderListView(OperatorOrAdminRequiredMixin, ListView):
    template_name = "crm/orders_list.html"
    context_object_name = "orders"
    model = Order
    paginate_by = 20

    def get_queryset(self):
        queryset = Order.objects.select_related("user", "service", "assigned_to").order_by("-created_at")
        status = self.request.GET.get("status")
        priority = self.request.GET.get("priority")
        assigned_to = self.request.GET.get("assigned_to")
        search = self.request.GET.get("search")

        if status:
            queryset = queryset.filter(status=status)
        if priority:
            queryset = queryset.filter(priority=priority)
        if assigned_to:
            queryset = queryset.filter(assigned_to__id=assigned_to)
        if search:
            queryset = queryset.filter(user__phone__icontains=search)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["statuses"] = Order.Status.choices
        context["priorities"] = Order.Priority.choices
        context["operators"] = User.objects.filter(role__in=[User.Role.ADMIN, User.Role.OPERATOR])
        context["current_status"] = self.request.GET.get("status", "")
        context["current_priority"] = self.request.GET.get("priority", "")
        context["current_assigned_to"] = self.request.GET.get("assigned_to", "")
        context["current_search"] = self.request.GET.get("search", "")
        return context


class CRMOrderDetailView(OperatorOrAdminRequiredMixin, UpdateView):
    model = Order
    template_name = "crm/order_detail.html"
    context_object_name = "order"
    form_class = OrderUpdateForm

    def get_queryset(self):
        return Order.objects.select_related("user", "service", "assigned_to", "customer").prefetch_related("comments__operator")

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
                messages.success(request, "Комментарий добавлен.")
                return redirect("crm:order-detail", pk=self.object.pk)
            else:
                # Если форма комментария невалидна, показываем ошибки
                context = self.get_context_data()
                context["comment_form"] = comment_form
                return self.render_to_response(context)
        
        # Обработка обновления заявки
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, "Заявка успешно обновлена.")
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
        messages.success(self.request, "Комментарий добавлен.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("crm:order-detail", kwargs={"pk": self.kwargs["pk"]})


class CRMCustomerListView(OperatorOrAdminRequiredMixin, ListView):
    model = Customer
    template_name = "crm/customers_list.html"
    context_object_name = "customers"
    paginate_by = 20

    def get_queryset(self):
        queryset = Customer.objects.all().order_by("-created_at")
        search = self.request.GET.get("search")
        if search:
            queryset = queryset.filter(phone__icontains=search)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["current_search"] = self.request.GET.get("search", "")
        return context


class CRMCustomerDetailView(OperatorOrAdminRequiredMixin, UpdateView):
    model = Customer
    template_name = "crm/customer_detail.html"
    context_object_name = "customer"
    form_class = CustomerForm

    def get_queryset(self):
        return Customer.objects.prefetch_related("orders__service", "orders__assigned_to")

    def form_valid(self, form):
        messages.success(self.request, "Данные клиента успешно обновлены.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("crm:customer_detail", kwargs={"pk": self.object.pk})
