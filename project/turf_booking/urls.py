"""
URL configuration for project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from .import views
from django.conf import settings
from django.conf.urls.static import static



urlpatterns = [
    
    path('',views.home,name='home'),
    path('turfs/',views.turfs_view,name='turfs'),
    path('register/',views.register,name='register'),
    path('logout_view/',views.logout_view,name='logout_view'),
    path('login_view/',views.login_view,name='login_view'),
    path('turf_checkout/<int:turfid>/',views.turf_checkout,name='turf_checkout'),
    path('my_bookings/',views.my_bookings,name="my_bookings"),
    path('my_booked_turf/<int:booking_id>/',views.my_booked_turf,name='my_booked_turf'),
    path('turf_booking_list/<int:turf_id>/',views.turf_booking_list,name='turf_booking_list'),
    path('turf_bookings/<int:turf_id>/',views.turf_bookings,name="turf_bookings"),
    path('canceled_booking/<int:booking_id>/',views.canceled_booking,name='canceled_booking'),
    path('myprofile/',views.myprofile,name='myprofile'),
    path('editprofile/',views.editprofile,name='editprofile'),
    path('bookingconfirmed/',views.bookingconfirmed,name='bookingconfirmed'),
    path('bookingcanceled/',views.bookingcanceled,name='bookingcanceled'),
    path('search_list/',views.search_list,name='search_list'),
    path('become_partner/',views.become_partner,name='become_partner'),
    path('direct_partner_registration/',views.direct_partner_registration,name='direct_partner_registration'),
    path('addratings/<int:turf_id>/',views.addratings,name='addratings'),
    path('changeratings/<int:turf_id>/',views.changeratings,name='changeratings'),

    path('checkout/', views.checkout, name='checkout'),
    path('create_order/', views.create_order, name='create_order'),
    path('payment_handler/', views.payment_handler, name='payment_handler'),
    path("checkout/", views.checkout),
    path("create_order/", views.create_order),
    path("payment_handler/", views.payment_handler),


    path('admin_blockuser/<int:user_id>/',views.admin_blockuser,name='admin_blockuser'),
    path('admin_unblockuser/<int:user_id>/',views.admin_unblockuser,name='admin_unblockuser'),
    path('admin_approvestaff/<int:staff_id>/',views.admin_approvestaff,name='admin_approvestaff'),
    path('admin_rejectstaff/<int:staff_id>/',views.admin_rejectstaff,name='admin_rejectstaff'),
    path('admin_approveturf/<int:turf_id>/',views.admin_approveturf,name='admin_approveturf'),
    path('admin_rejectturf/<int:turf_id>/',views.admin_rejectturf,name='admin_rejectturf'),
    path('admin_blockpartnr/<int:user_id>/',views.admin_blockpartner,name='admin_blockpartner'),
    path('admin_unblockparter/<int:user_id>/',views.admin_unblockpartner,name='admin_unblockpartner'),
    path('admin_turfrequestlist/',views.admin_turfrequestlist,name='admin_turfrequestlist'),
    path('admin_turfrequestcheckout/<int:request_id>/',views.admin_turfrequestcheckout,name='admin_turfrequestcheckout'),
    path('admin_turfdelete/<int:turf_id>/',views.admin_deleteturf,name='admin_turfdelete'),
    path('admin_dashboard/',views.admin_dashboard,name='admin_dashboard'),
    path('admin_userlist/',views.admin_userlist,name='admin_userlist'),
    path('admin_partnerlist/',views.admin_partnerlist,name='admin_partnerlist'),
    path('admin_turflist/',views.admin_turflist,name='admin_turflist'),
    path('admin_turfcheckout/<int:turf_id>/',views.admin_turfcheckout,name='admin_turfcheckout'),
    path('admin_bookinglist/',views.admin_bookinglist,name='admin_bookinglist'),
    path('admin_bookingcheckout/<int:booking_id>/',views.admin_bookingcheckout,name='admin_bookingcheckout'),
    path('admin_requestlist/',views.admin_requestlist,name='admin_requestlist'),
    path('admin_requestcheckout/<int:request_id>/',views.admin_requestcheckout,name='admin_requestcheckout'),


    path('staff_dashboard/',views.staff_dashboard,name='staff_dashboard'),
    path('staff_turflist/',views.staff_turf,name='staff_turflist'),
    path('staff_turfcheckout/<int:turf_id>/',views.staff_turfcheckout,name='staff_turfcheckout'),
    path('staff_bookingslist/',views.staff_bookings,name='staff_bookingslist'),
    path('staff_bookingcheckout/<int:booking_id>/',views.staff_bookingcheckout,name='staff_bookingcheckout'),
    path('staff_addnewturf/',views.staff_addnewturf,name='staff_addnewturf'),
    path('staff_profile/',views.staff_profile,name='staff_profile'),
    path('staff_editturf/<int:turf_id>/',views.staff_editturf,name="staff_editturf"),
    path('staff_turfallbookings/<int:turf_id>/',views.staff_turfallbookings,name='staff_turfallbookings'),
    path('staff_bookingcancel/<int:booking_id>/',views.staff_bookingcancel,name='staff_bookingcancel')

]



    

