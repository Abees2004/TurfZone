from django.db import models
from django.contrib.auth.models import AbstractUser


class User_profile(AbstractUser):
    phno = models.IntegerField(null=True)
    location = models.CharField(max_length=255,null=True)
    image = models.ImageField(null=True,upload_to='uploads/')
    about_me = models.TextField(null=True)

    class Meta:
        indexes = [
            models.Index(fields=['username']),
        ]


class turf_owner(models.Model):

    STATUS_CHOICES = [
        ('P', 'pending'),
        ('A', 'approved'),
        ('R', 'rejected'),
    ]

    user = models.ForeignKey(User_profile,on_delete=models.CASCADE,db_index=True)
    turf = models.TextField()
    location = models.TextField()
    status = models.CharField(max_length=1,choices=STATUS_CHOICES,default='P',db_index=True)
    created_at = models.DateTimeField(auto_now_add=True,db_index=True)

    class Meta:
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
            models.Index(fields=['user']),
        ]


class turfs(models.Model):

    STATUS_CHOICES = [
        ('P', 'pending'),
        ('A', 'approved'),
        ('R', 'rejected'),
    ]

    partner = models.ForeignKey(User_profile,on_delete=models.CASCADE,db_index=True)
    name = models.CharField(max_length=100,db_index=True)
    image = models.ImageField(upload_to='uploads/')
    location = models.TextField(max_length=100)
    normal_price = models.IntegerField()
    price = models.IntegerField()
    description = models.TextField(default='This is dummy description')
    is_active = models.BooleanField(default=True,db_index=True)
    created_at = models.DateTimeField(auto_now_add=True,db_index=True)
    status = models.CharField(max_length=1,choices=STATUS_CHOICES,default='P',db_index=True)

    def __str__(self):
        return f"{self.name} ({self.get_status_display()})"

    class Meta:
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
            models.Index(fields=['partner']),
            models.Index(fields=['is_active']),
        ]


class turfbooking(models.Model):

    PAYMENT_STATUS = [
        ('PENDING', 'Pending'),
        ('SUCCESS', 'Success'),
        ('FAILED', 'Failed'),
        ('REFUNDED', 'Refunded'),
    ]

    user = models.ForeignKey(User_profile,on_delete=models.CASCADE,db_index=True)
    turf = models.ForeignKey(turfs,on_delete=models.CASCADE,db_index=True)
    date = models.DateField(db_index=True)
    start_time = models.TimeField(db_index=True)
    end_time = models.TimeField(db_index=True)
    duration = models.DecimalField(max_digits=6,decimal_places=2)
    ammount = models.DecimalField(max_digits=10,decimal_places=2)
    razorpay_order_id = models.CharField(max_length=255,null=True,blank=True,db_index=True)
    razorpay_payment_id = models.CharField(max_length=255,null=True,blank=True,db_index=True)
    razorpay_signature = models.TextField(null=True,blank=True)
    payment_status = models.CharField(max_length=20,choices=PAYMENT_STATUS,default='PENDING',db_index=True)
    is_paid = models.BooleanField(default=False,db_index=True)
    is_canceled = models.BooleanField(default=False,db_index=True)
    created_at = models.DateTimeField(auto_now_add=True,db_index=True)

    class Meta:
        ordering = ['-created_at']

        indexes = [
            models.Index(fields=['turf', 'date']),
            models.Index(fields=['start_time', 'end_time']),
            models.Index(fields=['user']),
            models.Index(fields=['created_at']),
            models.Index(fields=['is_canceled']),
            models.Index(fields=['payment_status']),
            models.Index(fields=['razorpay_order_id']),
            models.Index(fields=['razorpay_payment_id']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.turf.name} - {self.date}"

class ratingsandreviews(models.Model):
    user = models.ForeignKey(User_profile,on_delete=models.CASCADE,db_index=True)
    turf = models.ForeignKey(turfs,on_delete=models.CASCADE,db_index=True)
    rating = models.IntegerField(db_index=True)
    review = models.TextField()

    class Meta:
        indexes = [
            models.Index(fields=['turf']),
            models.Index(fields=['user']),
            models.Index(fields=['rating']),
        ]


class special_slot_price(models.Model):
    turf = models.ForeignKey(turfs,on_delete=models.CASCADE,db_index=True)
    date = models.DateField(db_index=True)
    start_time = models.TimeField(db_index=True)
    end_time = models.TimeField(db_index=True)
    price = models.IntegerField()

    class Meta:
        indexes = [
            models.Index(fields=['turf', 'date']),
            models.Index(fields=['start_time', 'end_time']),
        ]