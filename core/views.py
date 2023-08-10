from typing import Any, Dict
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import View, ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from .models import Item, Order, OrderItem, BillingAddress, Code, Payment, Refund
from django.http import Http404
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from .forms import CheckOutForm, RefundForm
from azbankgateways import bankfactories, models as bank_models, default_settings as settings
from azbankgateways.exceptions import AZBankGatewaysException
from datetime import datetime

class HomePage(ListView):
    model = Item
    paginate_by = 8
    template_name = 'home-page.html'

# to user DetailView we must have slug or pk...
class OrderSummary(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        try:
            order = Order.objects.get(user=request.user, ordered=False)
        except ObjectDoesNotExist:
            messages.warning(request, 'You don\'t have an active cart')
            return redirect('/')
        context = {
            'object':order
        }
        return render(request, 'order-summary.html', context)

class ProductPage(DetailView):
    model = Item
    template_name = 'product-page.html'

def is_valid_form(*args):
    valid = True
    for arg in args:
        if arg == '':
            valid = False
            break
    return valid

class CheckoutPage(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        form = CheckOutForm()
        try:
            order = Order.objects.get(user=request.user, ordered=False)
        except ObjectDoesNotExist:
            messages.warning(request, 'You don\'t have an active cart')
            return redirect('/')
        
        if order.items.count() == 0:
            messages.warning(request, 'You did NOT ordered anything')
            return redirect('/')

        context = {
            'form':form,
            'object':order
        }

        address_qs = BillingAddress.objects.filter(user=request.user, default=True)
        if address_qs.exists():
            context.update({'SHOW_ADDRESS': True, 'address':address_qs.last()})
        else:
            context.update({'SHOW_ADDRESS': False})

        return render(request, 'checkout-page.html', context)
    
    def post(self, request, *args, **kwargs):
        form = CheckOutForm(request.POST or None)
        if form.is_valid():
            province = form.cleaned_data.get('province')
            city = form.cleaned_data.get('city')
            postal_code = form.cleaned_data.get('postal_code')
            full_address = form.cleaned_data.get('full_address')
            save_address = request.POST.get('save_address')
            use_saved_address = request.POST.get('use_saved_address')
            payment_method = form.cleaned_data.get('payment_method')

            # creating Address or fetching address from database
            if use_saved_address:
                billing_address = BillingAddress.objects.filter(user=request.user, default=True).first()
            else:
                if not is_valid_form(province, city, postal_code, full_address):
                    messages.warning(request, 'please fill out the required fields')
                    return redirect('core:checkout')
                else:
                    billing_address = BillingAddress.objects.create(
                    user = request.user,
                    province = province,
                    city = city,
                    postal_code = postal_code,
                    full_address = full_address
                )

                if save_address:
                    billing_address.default = True
                    billing_address.save()
            

            try:
                order = Order.objects.get(user=request.user, ordered=False)
                order.billing_address = billing_address
                order.save()
            except:
                messages.info(request, 'You don\'t have an active order!')
                return redirect('/')
            if payment_method == 'ip':
                amount = order.get_IRR_price()
                factory = bankfactories.BankFactory()
                try:
                    bank = factory.create(bank_models.BankType.IDPAY)
                    bank.set_request(request)
                    bank.set_amount(amount)
                    bank.set_client_callback_url(reverse('core:callback-gateway'))
                    bank.set_mobile_number('')
                    bank_record = bank.ready()
                    # print(bank_record.bank_type)
                    context = bank.get_gateway()
                    return render(request, 'redirect_to_bank.html', context)
                except AZBankGatewaysException:
                    return render(request, 'redirect_to_bank.html')
            else:
                messages.info(request, 'zarinpal not supported yet')
                return redirect('core:checkout')
        else:
            print(form.errors)
            messages.warning(request, 'Form is not valid')
            return redirect('core:checkout')
    
@login_required
def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item = OrderItem.objects.get_or_create(user=request.user, item=item, ordered=False)[0]
    order_qs = Order.objects.filter(user=request.user, ordered=False)

    if order_qs.exists():
        order = order_qs.first()
        # check if order_item in order
        if order.items.filter(item=item).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request, 'order item quantity was updated')
            return redirect('core:order-summary')
        else:
            order_item.quantity = 1
            order_item.save()
            order.items.add(order_item)
            messages.info(request, 'item added to your cart')
            return redirect('core:order-summary')
    else:
        order = Order.objects.create(user=request.user)
        order.items.add(order_item)
        messages.info(request, 'item added to your cart')
        return redirect('core:order-summary')
    
@login_required
def remove_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    
    if order_qs.exists():
        order = order_qs.first()
        # if there is no order_item this qs will be None
        if order.items.filter(item=item).exists():
            order_item = OrderItem.objects.filter(
                user=request.user,
                item=item,
                ordered=False
                ).first()

            order.items.remove(order_item)
            if order.items.count() == 0:
                order.code = None
                order.save()

            messages.warning(request, 'Item removed from your cart')
            return redirect('core:order-summary')
        else:
            messages.info(request, 'This item is not in your cart')
            return redirect('core:order-summary')
    else:
        messages.info(request, 'You don\'t have an active cart')
        return redirect('core:order-summary')
    
@login_required
def decrease_item_quantity(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item = OrderItem.objects.filter(
        user=request.user,
        item=item,
        ordered=False
        ).first()
    order_qs = Order.objects.filter(user=request.user, ordered=False)

    if order_qs.exists():
        order = order_qs.first()
        if order.items.filter(item=item).exists():
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
                messages.info(request, 'order item quantity was updated')
                return redirect('core:order-summary')
            else:
                order.items.remove(order_item)
                messages.warning(request, 'Item removed from your cart')
                return redirect('core:order-summary')
        else:
            messages.info(request, 'This item is not in your cart')
            return redirect('core:order-summary')
    else:
        messages.info(request, 'You don\'t have an active cart')
        return redirect('core:order-summary')
    

def callback_gateway_view(request):
    tracking_code = request.GET.get(settings.TRACKING_CODE_QUERY_PARAM, None)
    if not tracking_code:
        raise Http404
    try:
        bank_record = bank_models.Bank.objects.get(tracking_code=tracking_code)
        print('first try')
    except bank_models.Bank.DoesNotExist:
        raise Http404
    
    if bank_record.is_success:
        context = {
            'bank_record':bank_record 
        }
        try:
            order = Order.objects.get(user=request.user, ordered=False)
        except ObjectDoesNotExist:
            order = get_object_or_404(Order, order_id=bank_record.tracking_code)
            context['order'] = order
            return render(request, 'callback-page.html', context)

        try:
            payment = Payment.objects.create(
                user=request.user,
                bank_ref_number=bank_record.reference_number,
                tracking_code=bank_record.tracking_code,
                amount = bank_record.amount
            )
            # all method returns a qs
            order_items = order.items.all()
            order_items.update(ordered=True)
            for order_item in order_items:
                order_item.save()

            order.payment = payment
            order.ordered = True
            order.order_id = bank_record.tracking_code
            order.ordered_date = datetime.now()
            order.save()

            return render(request, 'callback-page.html', context)
        except:
            redirect('/')
        return render(request, 'callback-page.html', context)
    
    message = 'پرداخت با شکست مواجه شده است. اگر پول کم شده است ظرف مدت ۴۸ ساعت پول به حساب شما بازخواهد گشت.'
    messages.warning(request, message)
    return render(request, 'callback-page.html',{'bank_record':bank_record})


def get_promo_code(code):
    try:
        code = Code.objects.get(code=code)
        return code
    except ObjectDoesNotExist:
        return None


class AddPromo(View):
    def post(self, request, *args, **kwargs):
        try:
            order = Order.objects.get(user=request.user, ordered=False)
            promo_code = request.POST.get('promo_code')
            # Must bet Code object
            code = get_promo_code(promo_code)
            if code is not None:
                order.code = code
                order.save()
            else:
                messages.warning(request, 'Invalid Promo Code.')
            return redirect('core:checkout')
        except ObjectDoesNotExist:
            messages.warning(request, 'You don\'t have an active cart')
            return redirect('/')
        

class Profile(ListView):
    model = Order
    template_name = 'profile.html'

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context =  super().get_context_data(**kwargs)
        context['object_list'] = Order.objects.filter(user=self.request.user, ordered=True)
        return context

class OrderDetail(View):
    def get(self, request, *args, **kwargs):
        pk = request.GET.get('pk')
        qs = Order.objects.filter(user=request.user, ordered=True, pk=pk)
        if qs.exists():
            context = {
                'object':qs.first()
            }
        else:
            messages.info(request, 'you don\'t have such an order')
            return redirect('core:profile')
        return render(request, 'order-detail.html', context)
    
class RequestRefund(View):
    def get(self, request, *args, **kwargs):
        context = {
            'form':RefundForm()
        }
        return render(request, 'request-refund.html', context)
    
    def post(self, request, *args, **kwargs):
        form = RefundForm(request.POST or None)
        if form.is_valid():
            order_id = form.cleaned_data.get('order_id')
            title = form.cleaned_data.get('title')
            reason = form.cleaned_data.get('reason')
            qs = Order.objects.filter(order_id=order_id)
            if qs.exists():
                order = qs.first()
                if not order.refund_requested:
                    order.refund_requested = True
                    order.save()
                    Refund.objects.create(order_id=order_id, title=title, reason=reason)
                    messages.info(request, 'your request sent to our team')
                    return redirect('core:request-refund')
                else:
                    messages.warning(request, 'your request have already being sent')
                    return redirect('core:request-refund')
            else:
                messages.warning(request, 'you don\'t have such an order')
                return redirect('core:request-refund')
        else:
            messages.info(request, 'please fill in required fields')
            return redirect('core:request-refund')