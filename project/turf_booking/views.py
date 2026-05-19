from django.shortcuts import render,redirect,get_object_or_404
from django.contrib import messages
from .models import *
from django.contrib.auth import logout,login,authenticate
from django.db.models import Q
from django.db.models import Sum,Case,Avg,Count,When,IntegerField,F, Value
from datetime import datetime
from datetime import timedelta
from django.shortcuts import render,redirect,get_object_or_404
from django.contrib import messages
from turf_booking.models import *
from django.contrib.auth import logout,login,authenticate
from django.shortcuts import render,redirect,get_object_or_404
import json
import razorpay
from datetime import datetime

from django.conf import settings
from django.shortcuts import render
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt

from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from datetime import datetime
from django.conf import settings
import razorpay
import json




# Create your views here.
def home(request):
    return render(request,'home.html')

def myprofile(request):
    current_user=request.user
    bookings=turfbooking.objects.filter(user=current_user)
    turf_list=turfs.objects.filter(partner=current_user,status='P')
    return render(request,'myprofile.html',{'user':current_user,
                                            'bookings':bookings,
                                            'turfs':turf_list})

def editprofile(request):
    current_user=request.user
    if request.method=='POST':
        current_user.username=request.POST.get('username')
        current_user.email=request.POST.get('email')
        current_user.save()
    
    return render(request,'editprofile.html',{'user':current_user})

def search_list(request):
    turf_list = turfs.objects.filter(is_active=True, status='A')  # base queryset
    if request.method == 'POST':
        search = request.POST.get('search')
        if search:  # only filter if search is not empty or None
            turf_list = turf_list.filter(Q(name__icontains=search) | Q(location__icontains=search))
    return render(request, 'turf.html', {'turfs': turf_list})

def turfs_view(request):
    # Start with all active and approved turfs
    turf_list = turfs.objects.filter(is_active=True, status='A')

    if request.method == 'POST':
        search = request.POST.get('search')
        location = request.POST.get('location')
        price = request.POST.get('price')

        # Filter by search term if provided
        if search:
            turf_list = turf_list.filter(Q(name__icontains=search) | Q(location__icontains=search))
            return render(request, 'turf.html', {'turfs': turf_list})

        # Filter by location if provided
        if location:
            turf_list = turf_list.filter(location__icontains=location)

        # Filter by price if provided and not empty
        if price:
            try:
                price_val = float(price)
                turf_list = turf_list.filter(price__lte=price_val)
            except ValueError:
                pass  # Ignore invalid price inputs

    return render(request, 'turf.html', {'turfs': turf_list})

def register(request):
    if request.method=='POST':
        user_name=request.POST.get('username')
        user_email=request.POST.get('email')
        user_password=request.POST.get('password')
        confirm_password=request.POST.get('confirm_password')
        if user_password!=confirm_password:
            messages.error(request,'MISMATCH PASSWORD')
            return redirect('register') 
        if User_profile.objects.filter(username=user_name).exists():
            messages.error(request,'User name already exists')
            return redirect('register')
        if User_profile.objects.filter(email=user_email).exists():
            messages.error(request,'Email already Exists')
            return redirect('register')
        user=User_profile.objects.create_user(username=user_name,email=user_email,password=user_password)
        login(request,user)
        return redirect('home')
    return render(request,'register.html')


def is_slot_available(book_date, turf, book_start_time, book_end_time):

    new_start = datetime.combine(book_date, book_start_time)
    new_end = datetime.combine(book_date, book_end_time)

    if new_end <= new_start:
        return False

    bookings = turfbooking.objects.filter(
        turf=turf,
        date=book_date,
        is_canceled=False
    )

    for b in bookings:

        existing_start = datetime.combine(b.date, b.start_time)
        existing_end = datetime.combine(b.date, b.end_time)

        print("COMPARE:", existing_start, existing_end, new_start, new_end)

        if existing_start < new_end and existing_end > new_start:
            return False

    return True


def is_special_price_available(book_date,turf):
    return  special_slot_price.objects.filter(
        turf=turf,
        date=book_date,
    ).exists()


def bookingconfirmed(request):
    return render(request,'bookingconfirmed.html')

def bookingcanceled(request):
    return render(request,'canceledbooking.html')





from datetime import datetime
from decimal import Decimal
from django.shortcuts import render, redirect
from django.contrib import messages


def turf_checkout(request, turfid):

    current_turf = turfs.objects.get(id=turfid)
    user = request.user

    if request.method == 'POST':

        form_date = request.POST.get('date')
        form_start_time = request.POST.get('start_time')
        form_end_time = request.POST.get('end_time')

        if not (form_date and form_start_time and form_end_time):
            messages.error(request, "All fields are required.")
            return redirect('turf_checkout', turfid=turfid)

        try:
            book_date = datetime.strptime(form_date, "%Y-%m-%d").date()
            book_start_time = datetime.strptime(form_start_time, "%H:%M").time()
            book_end_time = datetime.strptime(form_end_time, "%H:%M").time()
        except:
            messages.error(request, "Invalid date/time format.")
            return redirect('turf_checkout', turfid=turfid)

        start_dt = datetime.combine(book_date, book_start_time)
        end_dt = datetime.combine(book_date, book_end_time)

        if end_dt <= start_dt:
            messages.error(request, "End time must be after start time.")
            return redirect('turf_checkout', turfid=turfid)

        if not is_slot_available(book_date, current_turf, book_start_time, book_end_time):
            messages.error(request, "Slot is already booked.")
            return redirect('turf_checkout', turfid=turfid)

        # ---------------------------
        # ✅ PRICE LOGIC FIXED
        # ---------------------------
        try:
            slot_turf = special_slot_price.objects.get(turf=current_turf)
            special_available = is_special_price_available(book_date, current_turf)
        except:
            slot_turf = None
            special_available = False

        if special_available and slot_turf:
            rate_per_hour = Decimal(slot_turf.price)
        else:
            rate_per_hour = Decimal(current_turf.normal_price)

        # ---------------------------
        # duration
        # ---------------------------
        seconds = (end_dt - start_dt).total_seconds()
        hours = Decimal(seconds / 3600)

        booking_amount = hours * rate_per_hour

        # ---------------------------
        # SAVE BOOKING (FIXED)
        # ---------------------------
        current_booking = turfbooking.objects.create(
            user=user,
            turf=current_turf,
            date=book_date,
            start_time=book_start_time,   # ✅ FIXED
            end_time=book_end_time,       # ✅ FIXED
            duration=hours,
            ammount=booking_amount
        )

        messages.success(request, "Your slot is booked.")
        return render(request, 'my_booked_turf.html', {
            'booking': current_booking
        })

    return render(request, 'turfcheckout.html', {
        'turf': current_turf
    })



def login_view(request):
    if request.method=='POST':
        user_name=request.POST.get('user_name')
        user_password=request.POST.get('user_password')
        user=authenticate(request,username=user_name,password=user_password)
        if user is not None:
            login(request,user)
            if user.is_superuser:
                return redirect('admin_dashboard')
            elif user.is_staff:
                return redirect('staff_dashboard')
            else:
                return redirect('home')
        else:
            messages.error(request,'Invalid Username or Password')
            return render(request, 'login.html')
        
    return render(request,'login.html')

def logout_view(request):
    logout(request)
    return render(request,'home.html')


def my_bookings(request):
    user = request.user
    bookings = turfbooking.objects.filter(user=user)
    current_time =datetime.now()

    # Split bookings
    upcoming = bookings.filter(start_time__gt=current_time,is_canceled=False).order_by('start_time')
    ongoing = bookings.filter(start_time__lte=current_time, end_time__gte=current_time,is_canceled=False).order_by('start_time')
    past = bookings.filter(end_time__lt=current_time,is_canceled=False).order_by('-start_time')
    canceled_booking=bookings.filter(is_canceled=True).order_by('-start_time')

    return render(request, 'turfbookinglist.html', {
        'upcoming_bookings': upcoming,
        'ongoing_bookings': ongoing,
        'past_bookings': past,
        'canceled_bookings':canceled_booking,
    })


def my_booked_turf(request,booking_id):
    booking=turfbooking.objects.get(id=booking_id)
    return render(request,'my_booked_turf.html',{'booking':booking})

def turf_booking_list(request,turf_id):
    return render(request,'new20.html')

def turf_bookings(request,turf_id):
    turf=turfs.objects.get(id=turf_id)
    if request.method=='POST':
        date=request.POST.get('date')
        bookings=turfbooking.objects.filter(turf=turf,date=date).order_by('start_time')
        return render(request,'new30.html',{'bookings':bookings,'date':date})
    bookings=turfbooking.objects.filter(turf=turf).order_by('-date','start_time')
    return render(request,'new30.html',{'bookings':bookings})

def canceled_booking(request,booking_id):
    current_booking=turfbooking.objects.get(id=booking_id)
    current_time=datetime.now()
    new_time=current_time+timedelta(hours=3)
    
    try:
        newest_current_time = new_time.strftime("%Y-%m-%d %H:%M")
        booking_time =current_booking.start_time
        booking_date=current_booking.date
        old_booking_time=datetime.combine(booking_date,booking_time)
        booking_time_old=old_booking_time.strftime("%Y-%m-%d %H:%M")
    except:
        messages.error(request, "Date or Time format is incorrect.")
        return render(request,'login.html')
    if newest_current_time<booking_time_old:
        current_booking.is_canceled=True
        current_booking.save()
        return render(request,'my_booked_turf.html',{'booking':current_booking})

    else:
        messages.error(request,'cannot cancel booking')
    return redirect('my_booked_turf',booking_id=booking_id)

def become_partner(request):
    if request.method=='POST':
        turf=request.POST.get('turf')
        location=request.POST.get('location')


        partner=turf_owner.objects.create(user=request.user,turf=turf,location=location)
        partner.save()
        return render(request,'home.html')
    return render(request,'becomepartner.html')

def direct_partner_registration(request):
    if request.method=='POST':
        user_name=request.POST.get('username')
        user_email=request.POST.get('email')
        user_password=request.POST.get('password')
        turf=request.POST.get('turf')
        location=request.POST.get('location')
        #confirm_password=request.POST.get('cpassword')
        user=User_profile.objects.create_user(username=user_name,email=user_email,password=user_password)
        user.save()

        partner=turf_owner.objects.create(user=user,turf=turf,location=location)
        partner.save()
        return redirect('home')
    return render(request,'direct_partner.html')

def addratings(request,turf_id):
    currnt_turf=turfs.objects.get(id=turf_id)
    if request.method=='POST':
        rating=request.POST.get('rating')
        comment=request.POST.get('review')
        if not (ratingsandreviews.objects.filter(user=request.user,turf=currnt_turf).exists()):
            ratingsandreviews.objects.create(user=request.user,turf=currnt_turf,rating=rating,review=comment)
    return render(request,'turfcheckout.html',{'turf':currnt_turf})

def changeratings(request,turf_id):
    currnt_turf=turfs.objects.get(id=turf_id)
    currnt_rating=ratingsandreviews.objects.get(user=request.user,turf=currnt_turf)
    if request.method=='POST':
        currnt_rating.rating=request.POST.get('rating')
        currnt_rating.review=request.POST.get('review')
        currnt_rating.save()
    return render(request,'turfcheckout.html',{'turf':currnt_turf})


# views.py


from .models import turfs, turfbooking


def get_client():
    return razorpay.Client(auth=(
        settings.RAZORPAY_KEY_ID,
        settings.RAZORPAY_KEY_SECRET
    ))


def checkout(request):
    return render(request, "paymentcheckout.html")

@csrf_exempt
def create_order(request):

    client = get_client()

    if request.method != "POST":
        return JsonResponse({
            "status": "failure",
            "message": "Invalid request method"
        }, status=400)

    try:
        body = json.loads(request.body)

    except json.JSONDecodeError:

        return JsonResponse({
            "status": "failure",
            "message": "Invalid JSON data"
        }, status=400)

    from datetime import datetime
    from django.utils import timezone


    date_value = body.get("date")
    start = body.get("start_time")
    end = body.get("end_time")
    turf_id = body.get("turf_id")

    if not (date_value and start and end and turf_id):

        return JsonResponse({
            "status": "failure",
            "message": "Missing booking details"
        }, status=400)


    try:
        turf = turfs.objects.get(id=turf_id)

    except turfs.DoesNotExist:

        return JsonResponse({
            "status": "failure",
            "message": "Invalid turf selected"
        }, status=400)


    try:

        booking_date = datetime.strptime(
            date_value,
            "%Y-%m-%d"
        ).date()

        start_time = datetime.strptime(
            start,
            "%H:%M"
        ).time()

        end_time = datetime.strptime(
            end,
            "%H:%M"
        ).time()

    except ValueError:

        return JsonResponse({
            "status": "failure",
            "message": "Invalid date or time format"
        }, status=400)


    if end_time <= start_time:

        return JsonResponse({
            "status": "failure",
            "message": "End time must be greater than start time"
        }, status=400)

    now = timezone.localtime()

    if booking_date == now.date():

        booking_start_datetime = datetime.combine(
            booking_date,
            start_time
        )

        if booking_start_datetime <= now.replace(tzinfo=None):

            return JsonResponse({
                "status": "failure",
                "message": "Cannot book past time slots"
            }, status=400)
        
    if not is_slot_available(
        booking_date,
        turf,
        start_time,
        end_time
    ):

        return JsonResponse({
            "status": "failure",
            "message": "Slot already booked"
        }, status=400)


    start_decimal = (
        start_time.hour +
        start_time.minute / 60
    )

    end_decimal = (
        end_time.hour +
        end_time.minute / 60
    )

    diff_hours = end_decimal - start_decimal

    amount = int(diff_hours * turf.price * 100)

    order_data = {
        "amount": amount,
        "currency": "INR",
        "receipt": f"receipt_{date_value}_{start}_{end}"
    }

    order = client.order.create(data=order_data)

    return JsonResponse({
        "status": "success",
        "key": settings.RAZORPAY_KEY_ID,
        "order_id": order["id"],
        "amount": order["amount"],
        "currency": order["currency"]
    })



@csrf_exempt
@login_required
def payment_handler(request):

    client = get_client()


    if request.method != "POST":

        return JsonResponse({
            "status": "failure",
            "message": "Invalid request method"
        }, status=400)


    try:

        body = json.loads(request.body)

    except json.JSONDecodeError:

        return JsonResponse({
            "status": "failure",
            "message": "Invalid JSON"
        }, status=400)

    payment_id = body.get("razorpay_payment_id")
    order_id = body.get("razorpay_order_id")
    signature = body.get("razorpay_signature")

    booking_date = body.get("booking_date")
    start_time = body.get("start_time")
    end_time = body.get("end_time")
    turf_id = body.get("turf_id")
    extras = body.get("extras", {})

    if not all([
        payment_id,
        order_id,
        signature,
        booking_date,
        start_time,
        end_time,
        turf_id
    ]):

        return JsonResponse({
            "status": "failure",
            "message": "Missing booking data"
        }, status=400)


    try:

        params_dict = {

            "razorpay_order_id": order_id,

            "razorpay_payment_id": payment_id,

            "razorpay_signature": signature
        }

        client.utility.verify_payment_signature(
            params_dict
        )

    except razorpay.errors.SignatureVerificationError:

        return JsonResponse({
            "status": "failure",
            "message": "Payment verification failed"
        }, status=400)

    existing_booking = turfbooking.objects.filter(
        razorpay_payment_id=payment_id
    ).first()

    if existing_booking:

        return JsonResponse({
            "status": "failure",
            "message": "Payment already processed"
        }, status=400)

    try:

        from datetime import datetime

        profile = request.user

        turf = turfs.objects.get(id=turf_id)

        fmt = "%H:%M"

        booking_date_obj = datetime.strptime(
            booking_date,
            "%Y-%m-%d"
        ).date()

        t0 = datetime.strptime(
            start_time,
            fmt
        )

        t1 = datetime.strptime(
            end_time,
            fmt
        )

        if not is_slot_available(
            booking_date_obj,
            turf,
            t0.time(),
            t1.time()
        ):

            return JsonResponse({
                "status": "failure",
                "message": "Slot already booked by another user"
            }, status=400)


        diff_minutes = (
            (t1.hour * 60 + t1.minute)
            - (t0.hour * 60 + t0.minute)
        )

        duration_hours = diff_minutes / 60

        if duration_hours <= 0:

            return JsonResponse({
                "status": "failure",
                "message": "Invalid duration"
            }, status=400)


        rate_per_hour = turf.price

        base_amount = duration_hours * rate_per_hour

        extras_cost = 0

        if extras.get("floodlights"):
            extras_cost += 100 * duration_hours

        if extras.get("shoes"):
            extras_cost += 50

        total_amount = base_amount + extras_cost


        booking = turfbooking.objects.create(

            user=profile,

            turf=turf,

            date=booking_date_obj,

            start_time=t0.time(),

            end_time=t1.time(),

            duration=duration_hours,

            ammount=total_amount,

            razorpay_order_id=order_id,

            razorpay_payment_id=payment_id,

            razorpay_signature=signature,

            payment_status="SUCCESS",

            is_paid=True
        )

        return JsonResponse({

            "status": "success",

            "message": "Booking confirmed successfully",

            "booking_id": booking.id,

            "amount_paid": total_amount
        })

    except turfs.DoesNotExist:

        return JsonResponse({
            "status": "failure",
            "message": "Invalid turf selected"
        }, status=400)

    except Exception as e:

        import traceback
        traceback.print_exc()

        return JsonResponse({
            "status": "failure",
            "message": str(e)
        }, status=500)

















#---------------------
#  Admin
#---------------------






# Create your views here.
total_userrequest=0
total_turfrequest=0

def admin_dashboard(request):
    bookings=turfbooking.objects.all()

    booking_ammount=turfbooking.objects.filter(is_canceled=False).aggregate(total_sum=Sum('ammount'))  
    total=booking_ammount['total_sum']

    booking_count=turfbooking.objects.filter(is_canceled=False).aggregate(total_booking=Count('id'))
    booking_counts=booking_count['total_booking']

    active_turf=turfs.objects.filter(is_active=True).aggregate(total_turfs=Count('id'))
    active_turfs=active_turf['total_turfs']

    pending_requests=total_userrequest+total_turfrequest

    return render(request,'admindashboard.html',
                  {'bookings':bookings,                   
                   'bookings_count':total,
                   'booking_total':booking_counts,
                   'total_turfs':active_turfs,
                   'total_requests':pending_requests
                   }
                  )

def admin_blockuser(request,user_id):
    user=User_profile.objects.get(id=user_id)
    if user.is_active==True:
        user.is_active=False
        user.save()
    users=User_profile.objects.all()
    return render(request,'adminuserlist.html',{'users':users})

def admin_unblockuser(request,user_id):
    user=User_profile.objects.get(id=user_id)
    if user.is_active==False:
        user.is_active=True
        user.save()
    users=User_profile.objects.all()
    return render(request,'adminuserlist.html',{'users':users})

def admin_blockpartner(request,user_id):
    user=User_profile.objects.get(id=user_id)
    if user.is_active==True:
        user.is_active=False
        user.save()
    partners=User_profile.objects.filter(is_staff=True,is_superuser=False)
    return render(request,'admin_partnerlist.html',{'partners':partners})

def admin_unblockpartner(request,user_id):
    user=User_profile.objects.get(id=user_id)
    if user.is_active==False:
        user.is_active=True
        user.save()
    partners=User_profile.objects.filter(is_staff=True,is_superuser=False)
    return render(request,'admin_partnerlist.html',{'partners':partners})

def admin_userlist(request):
    users=User_profile.objects.all()
    return render(request,'adminuserlist.html',{'users':users})

def admin_partnerlist(request):
    partners=User_profile.objects.filter(is_staff=True,is_superuser=False)
    return render(request,'admin_partnerlist.html',{'partners':partners})

def admin_turflist(request):

    turf_list=turfs.objects.filter(status='A')
    return render(request,'adminturflist.html',{'turf_list':turf_list})

def admin_turfcheckout(request,turf_id):
    current_turf=turfs.objects.get(id=turf_id)
    bookings=turfbooking.objects.filter(id=turf_id).order_by('-id')
    return render(request,'admin_turfcheckout.html',{'current_turf':current_turf,'bookings':bookings})

def admin_bookinglist(request):
    booking=turfbooking.objects.all()
    turf_list=turfs.objects.all()
    search_user=request.POST.get('searchuser')
    search_status=request.POST.get('status')
    search_turf=request.POST.get('searchturf')
    if request.method=='POST':
        if search_user:
            booking=turfbooking.objects.filter(user__username=search_user)
        if search_status:
            booking=turfbooking.objects.filter(is_canceled=search_status)
        if search_turf:
            booking=turfbooking.objects.filter(turf__name=search_turf)

    return render(request,'admin_bookinglist.html',{'bookings':booking,
                                                    'turfs':turf_list})

def admin_bookingcheckout(request,booking_id):
    booking=turfbooking.objects.get(id=booking_id)
    return render(request,'admin_bookingcheckout.html',{'booking':booking})

def admin_requestlist(request):
    requests=turf_owner.objects.filter(status='P')
    global total_userrequest
    total_userrequest=len(requests)
    total_userrequest=10
    return render(request,'admin_newrequestlist.html',{'requests':requests})

def admin_requestcheckout(request,request_id):
    current_request=turf_owner.objects.get(id=request_id)
    return render(request,'admin_requestcheckout.html',{'current_request':current_request})

def admin_turfrequestlist(request):
    requests=turfs.objects.filter(status='P')
    global total_turfrequest
    total_turfrequest=len(requests)
    return render(request,'admin_turfrequestlist.html',{'requests':requests})

def admin_turfrequestcheckout(request,request_id):
    current_request=turfs.objects.get(id=request_id)
    return render(request,'admin_turfrequestcheckout.html',{'current_request':current_request})

def admin_approvestaff(request,staff_id):
    turf=turf_owner.objects.get(id=staff_id)
    user=User_profile.objects.get(id=turf.user_id)
    if turf.status=='P':
        if user.is_staff==False:
            user.is_staff=True
            turf.status='A'
            user.save()
            turf.save()
   # users=User_profile.objects.all()
    return render(request,'admin_newrequestlist.html')

def admin_rejectstaff(request,staff_id):
    turf=turf_owner.objects.get(id=staff_id)
    user=User_profile.objects.get(id=turf.user_id)
    if turf.status=='P':
        if user.is_staff==False:
            user.is_staff=False
            turf.status='R'
            user.save()
            turf.save()
#    users=User_profile.objects.all()
    return render(request,'admin_newrequestlist.html')

def admin_approveturf(request,turf_id):
    turf=turfs.objects.get(id=turf_id)
    if turf.status=='P':
        turf.status='A'
        turf.save()
    return render(request,'admin_turfrequestlist.html')

def admin_rejectturf(request,turf_id):
    turf=turfs.objects.get(id=turf_id)
    if turf.status=='P':
        turf.status='R'
        turf.save()
    return render(request,'admin_turfrequestlist.html')

def admin_deleteturf(request,turf_id):
    current_turf=turfs.objects.get(id=turf_id)
    current_turf.delete()
    return render(request,'admindashboard.html')
















#----------------
# Partner
#----------------















def staff_dashboard(request):
    bookings = turfbooking.objects.filter(turf__partner=request.user)
    totalbookings = turfbooking.objects.filter(turf__partner=request.user).aggregate(count=Count('id'))
    totalamount     = turfbooking.objects.filter(turf__partner=request.user).aggregate(sum=Sum('ammount'))
    bookingtotal = totalbookings.get('count', 0)
    amounttotal = totalamount.get('sum', 0)

    today = datetime.now().date()  # just the date part
    pastsevendays=today-timedelta(days=7)

    
    bookings = turfbooking.objects.filter(turf__partner=request.user)
    current_time =datetime.now()

    # Split bookings
    upcoming = bookings.filter(start_time__gt=current_time,is_canceled=False).order_by('start_time')

    # Option A: using __date lookup
    pastbookings = turfbooking.objects.filter(turf__partner=request.user,created_at__gte = pastsevendays)
    sevendayscount=len(pastbookings)


    print(f'past bookings: {pastbookings}')

    return render(request, 'staff_dashboard.html', {
        'bookings': bookings,
        'totalbookings': bookingtotal,
        'totalammount': amounttotal,
        'pastbookings': pastbookings,
        'sevendayscount':sevendayscount,
        'upcommingbookings':upcoming,
    })

def staff_turf(request):
    turf_list= turfs.objects.filter(partner=request.user)
    return render(request,'staff_turf.html',{'turfs':turf_list})

def staff_turfcheckout(request,turf_id):
    current_turf=turfs.objects.get(id=turf_id)
    bookings=turfbooking.objects.filter(turf=current_turf)
    totalbookings=turfbooking.objects.filter(turf=current_turf).aggregate(count=Count('id'))
    totalammount=turfbooking.objects.filter(turf=current_turf).aggregate(sum=Sum('ammount'))
    ratingsavg=ratingsandreviews.objects.filter(turf=current_turf).aggregate(avg=Avg('rating'))
    bookingtotal=totalbookings['count']
    ammounttotal=totalammount['sum']
    avgratings=ratingsavg['avg']

    current_time =datetime.now()

    # Split bookings
    upcoming = bookings.filter(start_time__gt=current_time,is_canceled=False).order_by('start_time')
    ongoing = bookings.filter(start_time__lte=current_time, end_time__gte=current_time,is_canceled=False).order_by('start_time')
    past = bookings.filter(end_time__lt=current_time,is_canceled=False).order_by('-start_time')
    canceled_booking=bookings.filter(is_canceled=True).order_by('-start_time')
  
    return render (request,'staff_turfcheckout.html',{'turf':current_turf,
                                                     'totalbookings':bookingtotal,
                                                     'totalammount':ammounttotal,
                                                     'avgratings':avgratings,
                                                     'bookings':bookings,
                                                     'upcoming_bookings': upcoming,
                                                    'ongoing_bookings': ongoing,
                                                    'past_bookings': past,
                                                    'canceled_bookings':canceled_booking
                                                     })

def staff_editturf(request,turf_id):
    current_turf=turfs.objects.get(id=turf_id)
    if request.method=='POST':
        current_turf.name=request.POST.get('name')
        current_turf.description=request.POST.get('description')
        current_turf.image=request.FILES.get('image')
        current_turf.price=request.POST.get('price')
        current_turf.location=request.POST.get('location')
        current_turf.save()
        return redirect('staff_turfcheckout',turf_id=turf_id)
    
    return render(request,'staff_editturf.html',{
        'turf':current_turf
    })

def staff_profile(request):
    user=request.user
    return render(request,'staff_myprofile.html',{'user':user})

def staff_bookings(request):
    bookings_list=turfbooking.objects.filter(turf__partner=request.user)
    turf_list=turfs.objects.filter(partner=request.user,is_active=True)
    if request.method=='POST':
        search_turf=request.POST.get('searchturf')
        search_status=request.POST.get('status')
        search_user=request.POST.get('searchuser')
        if search_status:
            bookings_list=turfbooking.objects.filter(is_canceled=search_status)
        if search_turf:
            bookings_list=turfbooking.objects.filter(turf__name=search_turf)
        if search_user:
            bookings_list=turfbooking.objects.filter(user__username=search_user)
    return render(request,'staff_bookings.html',{'bookings':bookings_list,
                                                 'turfs':turf_list})

def staff_bookingcheckout(request,booking_id):
    booking=turfbooking.objects.get(id=booking_id)
    return render(request,'staff_bookingcheckout.html',{'booking':booking})

def staff_turfallbookings(request,turf_id):
    turf=turfs.objects.get(id=turf_id)
    bookings = turfbooking.objects.filter(turf=turf)
    current_time =datetime.now()

    # Split bookings
    upcoming = bookings.filter(start_time__gt=current_time,is_canceled=False).order_by('start_time')
    ongoing = bookings.filter(start_time__lte=current_time, end_time__gte=current_time,is_canceled=False).order_by('start_time')
    past = bookings.filter(end_time__lt=current_time,is_canceled=False).order_by('-start_time')
    canceled_booking=bookings.filter(is_canceled=True).order_by('-start_time')
    return render(request,'staff_turfbookings.html',{
                            'upcoming_bookings': upcoming,
                            'ongoing_bookings': ongoing,
                            'past_bookings': past,
                            'canceled_bookings':canceled_booking
    })

def staff_bookingcancel(requset,booking_id):
    current_booking=turfbooking.objects.get(id=booking_id)
    if current_booking.is_canceled==False:
        current_booking.is_canceled=True
        current_booking.save()
    return redirect('staff_bookingcheckout',booking_id=booking_id)


def staff_addnewturf(request):
    if request.method=='POST':
        name=request.POST.get('name')
        location=request.POST.get('location')
        description=request.POST.get('description')
        image=request.FILES.get('image')
        price=request.POST.get('price')
        turfs.objects.create(partner=request.user,name=name,location=location,normal_price=price,price=price,image=image,description=description)
    return render(request,'staff_addturf.html')