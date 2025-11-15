from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DetailView, FormView, ListView, TemplateView

from .forms import (
    CustomerNotesForm,
    FeedbackForm,
    OrderCommentForm,
    OrderFilterForm,
    OrderForm,
    OrderUpdateForm,
    SignUpForm,
)
from .models import Customer, Order, Service, User


class ServiceListView(ListView):
    model = Service
    template_name = "services/service_list.html"
    context_object_name = "services"

    def get_queryset(self):
        return Service.objects.filter(is_active=True)


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
        form.instance.customer = Customer.objects.matching_user(self.request.user, form.cleaned_data.get("service"))
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


class CRMRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.role in {User.Role.ADMIN, User.Role.OPERATOR}

    def handle_no_permission(self):
        messages.error(self.request, "Недостаточно прав для доступа к CRM.")
        return redirect("services:service_list")


class CRMDashboardView(CRMRequiredMixin, TemplateView):
    template_name = "crm/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        orders = Order.objects.all()
        context["new_orders"] = orders.filter(status=Order.Status.CREATED).count()
        context["done_orders"] = orders.filter(status=Order.Status.DONE).count()
        context["in_progress_orders"] = orders.filter(
            status__in=[Order.Status.ACCEPTED, Order.Status.IN_PROGRESS]
        ).count()
        context["new_customers"] = Customer.objects.order_by("-created_at")[:5]
        context["recent_orders"] = orders.select_related("customer", "service")[:5]
        return context


class CRMOrderListView(CRMRequiredMixin, ListView):
    template_name = "crm/orders_list.html"
    context_object_name = "orders"
    paginate_by = 20

    def get_filter_form(self):
        operators = User.objects.filter(role__in=[User.Role.ADMIN, User.Role.OPERATOR])
        return OrderFilterForm(self.request.GET or None, operators=operators)

    def get_queryset(self):
        qs = (
            Order.objects.select_related("customer", "service", "assigned_to")
            .prefetch_related("comments")
            .all()
        )
        form = self.get_filter_form()
        if form.is_valid():
            data = form.cleaned_data
            if data.get("status"):
                qs = qs.filter(status=data["status"])
            if data.get("priority"):
                qs = qs.filter(priority=data["priority"])
            if data.get("assigned_to"):
                qs = qs.filter(assigned_to_id=data["assigned_to"])
            if data.get("phone"):
                qs = qs.filter(customer__phone__icontains=data["phone"])
        self.filter_form = form
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["filter_form"] = getattr(self, "filter_form", self.get_filter_form())
        context["querystring"] = self.request.GET.urlencode()
        return context


class CRMOrderDetailView(CRMRequiredMixin, DetailView):
    template_name = "crm/order_detail.html"
    model = Order
    context_object_name = "order"

    def get_queryset(self):
        return Order.objects.select_related("customer", "service", "user", "assigned_to").prefetch_related("comments")

    def get_order_form(self):
        operators = User.objects.filter(role__in=[User.Role.ADMIN, User.Role.OPERATOR])
        if self.request.method == "POST" and self.request.POST.get("action") == "update_order":
            return OrderUpdateForm(self.request.POST, instance=self.object, operator_queryset=operators)
        return OrderUpdateForm(instance=self.object, operator_queryset=operators)

    def get_comment_form(self):
        if self.request.method == "POST" and self.request.POST.get("action") == "add_comment":
            return OrderCommentForm(self.request.POST)
        return OrderCommentForm()

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        action = request.POST.get("action")
        if action == "update_order":
            form = self.get_order_form()
            if form.is_valid():
                form.save()
                messages.success(request, "Заявка обновлена.")
                return redirect(request.path)
            return self.render_to_response(self.get_context_data(order_form=form))
        elif action == "add_comment":
            comment_form = self.get_comment_form()
            if comment_form.is_valid():
                comment = comment_form.save(commit=False)
                comment.order = self.object
                comment.operator = request.user
                comment.save()
                messages.success(request, "Комментарий добавлен.")
                return redirect(request.path)
            return self.render_to_response(self.get_context_data(comment_form=comment_form))
        return self.get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["order_form"] = kwargs.get("order_form") or self.get_order_form()
        context["comment_form"] = kwargs.get("comment_form") or self.get_comment_form()
        return context


class CRMCustomerListView(CRMRequiredMixin, ListView):
    template_name = "crm/customers_list.html"
    context_object_name = "customers"
    paginate_by = 20

    def get_queryset(self):
        qs = Customer.objects.select_related("user").all()
        search = self.request.GET.get("phone")
        if search:
            qs = qs.filter(phone__icontains=search)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_term"] = self.request.GET.get("phone", "")
        return context


class CRMCustomerDetailView(CRMRequiredMixin, DetailView):
    template_name = "crm/customer_detail.html"
    model = Customer
    context_object_name = "customer"

    def get_queryset(self):
        return Customer.objects.select_related("user").prefetch_related("orders__service")

    def get_form(self):
        if self.request.method == "POST":
            return CustomerNotesForm(self.request.POST, instance=self.object)
        return CustomerNotesForm(instance=self.object)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            form.save()
            messages.success(request, "Заметки сохранены.")
            return redirect(request.path)
        return self.get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = self.get_form()
        context["orders"] = self.object.orders.select_related("service", "assigned_to").all()
        return context

