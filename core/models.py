from django.db import models
from django.conf import settings
from django.urls import reverse
from .data import PROVINCES

CATEGORIES = (
    ('S', 'Shirt'),
    ('SW', 'Sport wear'),
    ('OW', 'Outwear'),
)

LABELS = (
    ('PC', 'primary-color'),
    ('SC', 'secondary-color'),
    ('DC', 'danger-color'),
)

class Item(models.Model):
    title = models.CharField(max_length=100)
    category = models.CharField(choices=CATEGORIES, max_length=2)
    price = models.FloatField()
    discount = models.FloatField(default=0 , blank=True, null=True)
    label = models.CharField(choices=LABELS, max_length=2)
    description = models.TextField()
    slug = models.SlugField()

    def get_price_after_discount(self):
        return self.price - self.discount

    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('core:product', kwargs={
            'slug': self.slug
        })
    
    def get_add_to_cart_url(self):
        return reverse('core:add-to-cart', kwargs={
            'slug':self.slug
        })
        
    def get_remove_form_cart_url(self):
        return reverse('core:remove-from-cart', kwargs={
            'slug':self.slug
        })
    

class OrderItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)
    quantity = models.IntegerField(default=1)
    def __str__(self):
        return f'{self.quantity} of {self.item}'
    
    def get_item_price(self):
        return self.quantity * self.item.price
    
    def get_item_price_after_discount(self):
        return self.quantity * (self.item.price - self.item.discount)
    
    def get_amount_saved(self):
        return self.get_item_price() - self.get_item_price_after_discount()
    
    def get_effective_price(self):
        return self.get_item_price() - self.get_amount_saved()

class BillingAddress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    province = models.CharField(choices= PROVINCES, max_length=2)
    city = models.CharField(max_length=50)
    postal_code = models.CharField(max_length=50)
    full_address = models.CharField(max_length=250)
    default = models.BooleanField(default=False, blank=True, null=True)

    def __str__(self):
        return self.get_province_display() + ',' + self.city + '-' + self.full_address

class Order(models.Model):
    order_id = models.CharField(max_length=50 , blank=True, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    items = models.ManyToManyField(OrderItem)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField(blank=True, null=True)
    ordered = models.BooleanField(default=False)
    billing_address = models.ForeignKey(BillingAddress, on_delete=models.SET_NULL, blank=True, null=True)
    payment = models.ForeignKey('Payment', on_delete=models.SET_NULL, blank=True, null=True)
    code = models.ForeignKey('Code', on_delete=models.SET_NULL, blank=True, null=True)
    being_delivered = models.BooleanField(default=False, blank=True, null=True)
    recived = models.BooleanField(default=False, blank=True, null=True)
    refund_requested = models.BooleanField(default=False, blank=True, null=True)
    refund_granted = models.BooleanField(default=False, blank=True, null=True)


    def __str__(self):
        order_id = self.order_id if self.order_id else 'Not Orered'
        return str(self.user.username) + str(self.pk) + '-' + order_id

    def get_items_count(self):
        return self.items.count()
    
    def get_total_price(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.get_effective_price()
        if self.code:
            total -= self.code.amount
        return total
    
    def get_IRR_price(self):
        return (self.get_total_price() * 10000)


class Code(models.Model):
    code = models.CharField(max_length=16, blank=True, null=True)
    amount = models.IntegerField(blank=True, null=True, default = 0)

    def __str__(self):
        return self.code


class Payment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    bank_ref_number = models.CharField(max_length=60)
    tracking_code = models.CharField(max_length=60)
    amount = models.CharField(max_length=10)
    timestamp = models.DateTimeField(auto_now_add=True)


class Refund(models.Model):
    order_id = models.CharField(max_length=50)
    title = models.CharField(max_length=50)
    reason = models.CharField(max_length=250)





    

