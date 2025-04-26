from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import os
from django.db import transaction
from django.db.models import Avg, Count
from django.http import HttpResponse, JsonResponse
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import random
import string
import razorpay
import json
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import Table, TableStyle
from reportlab.lib.utils import ImageReader
from .models import Sock, Review, Cart, CartItem, User, Profile, Order, OrderItem
from .forms import SignUpForm, SignInForm, ReviewForm, ProfileForm, OrderForm

# Email utility for sending OTP
def send_otp_email(user_email, otp):
    subject = "Your OTP Code"
    message = f"Your OTP code is {otp}."
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [user_email]
    try:
        send_mail(subject, message, from_email, recipient_list)
        print("OTP sent successfully")
    except Exception as e:
        print(f"Error sending email: {e}")

# Home view with normalized sock names and ratings
def home(request):
    # Annotate socks with average rating and review count
    socks = Sock.objects.annotate(
        average_rating=Avg('reviews__rating'),
        review_count=Count('reviews')
    ).order_by('name')

    # Normalize sock names to avoid duplicates (case-insensitive)
    sock_dict = {}
    for sock in socks:
        normalized_name = sock.name.lower().strip()
        if normalized_name in sock_dict:
            # Aggregate reviews for duplicates
            existing_sock = sock_dict[normalized_name]
            existing_sock.review_count += sock.review_count
            if sock.average_rating and existing_sock.average_rating:
                # Weighted average for ratings
                total_ratings = existing_sock.review_count + sock.review_count
                existing_sock.average_rating = (
                    (existing_sock.average_rating * existing_sock.review_count + sock.average_rating * sock.review_count) / total_ratings
                )
            elif sock.average_rating:
                existing_sock.average_rating = sock.average_rating
        else:
            sock_dict[normalized_name] = sock

    # Convert back to list, excluding duplicates
    unique_socks = list(sock_dict.values())
    unique_socks.sort(key=lambda x: x.name.lower())

    context = {
        'socks': unique_socks,
    }
    return render(request, 'store/home.html', context)

# Sock detail view
def sock_detail(request, sock_id):
    sock = get_object_or_404(Sock.objects.annotate(
        average_rating=Avg('reviews__rating'),
        review_count=Count('reviews')
    ), id=sock_id)
    reviews = Review.objects.filter(sock=sock).order_by('-created_at')

    if request.method == 'POST':
        text = request.POST.get('text')
        rating = request.POST.get('rating')
        media = request.FILES.get('media')

        try:
            rating = float(rating) if rating else None
            if rating is None or rating < 1 or rating > 5:
                return render(request, 'store/sock_detail.html', {
                    'sock': sock,
                    'reviews': reviews,
                    'error': 'Please provide a valid rating between 1 and 5.',
                })
            review = Review.objects.create(
                sock=sock,
                user=request.user,
                text=text,
                rating=rating,
                photo=media if media and media.content_type.startswith('image') else None,
                video=media if media and media.content_type.startswith('video') else None,
            )
            return redirect('sock_detail', sock_id=sock.id)
        except Exception as e:
            return render(request, 'store/sock_detail.html', {
                'sock': sock,
                'reviews': reviews,
                'error': f'Error submitting review: {e}',
            })

    context = {
        'sock': sock,
        'reviews': reviews,
    }
    return render(request, 'store/sock_detail.html', context)

# Review view (alternative way to add reviews, but we'll merge with sock_detail)
@login_required
def review_view(request, sock_id):
    # This view is redundant since sock_detail now handles review submission
    return redirect('sock_detail', sock_id=sock_id)

# Cart view
@login_required
def cart_view(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    items = CartItem.objects.filter(cart=cart)
    is_cart_empty = not items

    for item in items:
        item.total_price = item.quantity * item.sock.price

    subtotal = sum(item.total_price for item in items)
    blocked = any(item.quantity > item.sock.stock for item in items)
    total_amount = subtotal + 150

    return render(request, 'store/cart.html', {
        'items': items,
        'total_amount': total_amount,
        'subtotal': subtotal,
        'is_cart_empty': is_cart_empty,
        'blocked': blocked,
    })

# Add to cart
@login_required
def add_to_cart(request, sock_id):
    sock = get_object_or_404(Sock, id=sock_id)
    quantity = int(request.GET.get('quantity', 1))
    cart, _ = Cart.objects.get_or_create(user=request.user)
    item, created = CartItem.objects.get_or_create(cart=cart, sock=sock, user=request.user)

    if not created:
        item.quantity += quantity
    else:
        item.quantity = quantity
    item.save()

    return redirect('cart_view')

# Remove from cart
@login_required
def remove_from_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id)
    item.delete()
    return redirect('cart_view')

# Update cart item quantity
@login_required
def update_quantity(request, item_id):
    item = get_object_or_404(CartItem, id=item_id)
    action = request.POST.get("action")
    if item.cart.user == request.user:
        if action == "increase":
            item.quantity += 1
        elif action == "decrease" and item.quantity > 1:
            item.quantity -= 1
        item.save()
    return redirect('cart_view')

# Contact us page
def contact_us(request):
    return render(request, 'store/contact_us.html')

# Logout view
def logout_view(request):
    logout(request)
    response = redirect('home')
    if settings.SESSION_COOKIE_NAME in request.COOKIES:
        response.delete_cookie(settings.SESSION_COOKIE_NAME)
    return response

# Profile view
@login_required
def profile_view(request):
    if not hasattr(request.user, 'profile'):
        Profile.objects.create(user=request.user)
    profile = request.user.profile

    if request.method == 'POST':
        if 'remove' in request.POST:
            profile.pfp.delete(save=True)
            return redirect('profile')
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = ProfileForm(instance=profile)

    orders = Order.objects.filter(user=request.user).order_by('-order_time')
    return render(request, 'store/profile.html', {
        'form': form,
        'orders': orders,
    })

# Sign-up view
def signup(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username is already taken.")
            return render(request, "store/signup.html")
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email is already registered.")
            return render(request, "store/signup.html")

        user = User.objects.create_user(username=username, email=email, password=password, is_active=False)
        user.save()

        otp = "".join(random.choices(string.digits, k=6))
        request.session["pending_user_id"] = user.id
        request.session["otp"] = otp

        send_mail(
            "Your SockShop OTP",
            f"Your OTP is {otp}",
            settings.EMAIL_HOST_USER,
            [email],
            html_message=render_to_string("store/email_template.html", {"otp": otp})
        )

        return redirect("otp_verification")
    return render(request, "store/signup.html")

# OTP verification
def otp_verification(request):
    if request.method == "POST":
        entered = request.POST.get("otp")
        stored = request.session.get("otp")
        uid = request.session.get("pending_user_id")

        if stored and entered == stored and uid:
            user = User.objects.get(id=uid)
            user.is_active = True
            user.save()
            login(request, user)
            del request.session["otp"]
            del request.session["pending_user_id"]            
            return redirect("home")
        else:
            messages.error(request, "Invalid OTP. Please try again.")
    return render(request, "store/otp_verification.html")

# Resend OTP
def resend_otp(request):
    user_id = request.session.get("pending_user_id")
    if not user_id:
        messages.error(request, "Cannot resend OTP right now.")
        return redirect("signup")

    user = User.objects.get(id=user_id)
    new_otp = "".join(random.choices(string.digits, k=6))
    request.session["otp"] = new_otp

    send_mail(
        "Your SockShop OTP",
        f"Your new OTP is {new_otp}",
        settings.EMAIL_HOST_USER,
        [user.email],
        html_message=render_to_string("store/email_template.html", {"otp": new_otp})
    )
    messages.success(request, "A new OTP has been sent to your email.")
    return redirect("otp_verification")

# Check username/email availability
def check_username_email(request):
    username = request.GET.get('username', None)
    email = request.GET.get('email', None)
    data = {
        'username_taken': User.objects.filter(username=username).exists(),
        'email_taken': User.objects.filter(email=email).exists()
    }
    return JsonResponse(data)

# Sign-in view
def signin_view(request):
    error_message = None
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        
        # Check if user exists
        user_exists = User.objects.filter(username=username).exists()
        if not user_exists:
            error_message = "no_user"
        else:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                request.session.set_expiry(0)
                response = redirect('home')
                request.session.save()
                response.set_cookie(
                    settings.SESSION_COOKIE_NAME,
                    request.session.session_key,
                    domain=None,
                    path='/',
                )
                login(request, user)
                return response
            else:
                error_message = "wrong_password"

    return render(request, 'store/signin.html', {'error_message': error_message})

# Order confirmation
@login_required
def order_confirmation(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order_items = order.items.all()
    return render(request, 'store/order_confirmation.html', {
        'order': order,
        'order_items': order_items
    })

# Buy view (checkout)
@login_required
def buy_view(request):
    cart = get_object_or_404(Cart, user=request.user)
    cart_items = CartItem.objects.filter(cart=cart)

    if not cart_items.exists():
        messages.error(request, "Your cart is empty.")
        return redirect('cart_view')

    subtotal = sum(item.sock.price * item.quantity for item in cart_items)
    total_amount = subtotal + 150

    if request.method == "POST":
        form = OrderForm(request.POST)
        payment_method = request.POST.get("payment_method", "unknown")

        if form.is_valid():
            try:
                with transaction.atomic():
                    order = form.save(commit=False)
                    order.user = request.user
                    order.total_amount = total_amount
                    order.payment_method = payment_method
                    order.save()

                    for item in cart_items:
                        item.sock.stock -= item.quantity
                        item.sock.save()
                        order_item = OrderItem.objects.create(
                            sock=item.sock,
                            quantity=item.quantity,
                            price=item.sock.price
                        )
                        order.items.add(order_item)

                    order.save()
                    cart_items.delete()
                    cart.delete()

                    send_mail(
                        subject=f"New Order #{order.id} ({payment_method})",
                        message=f"{request.user.username} placed an order of ₹{order.total_amount} via {payment_method}.",
                        from_email=settings.EMAIL_HOST_USER,
                        recipient_list=[admin[1] for admin in settings.ADMINS]
                    )

                    return redirect('order_confirmation', order_id=order.id)

            except Exception as e:
                messages.error(request, f"Order failed: {e}")

    else:
        form = OrderForm()

    return render(request, 'store/buy.html', {
        'form': form,
        'cart_items': cart_items,
        'subtotal': subtotal,
        'total_amount': total_amount
    })

# Payment handler for Razorpay
@csrf_exempt
def paymenthandler(request):
    if request.method == "POST":
        try:
            payment_id = request.POST.get('razorpay_payment_id')
            order_id = request.POST.get('razorpay_order_id')
            signature = request.POST.get('razorpay_signature')

            order = Order.objects.get(order_id=order_id)
            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_SECRET_KEY))

            params_dict = {
                'razorpay_order_id': order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            }

            try:
                client.utility.verify_payment_signature(params_dict)
                order.payment_id = payment_id
                order.signature = signature
                order.status = 'Completed'
                order.save()
                messages.success(request, "Payment successful!")
                return redirect('order_confirmation', order_id=order.id)
            except razorpay.errors.SignatureVerificationError:
                order.status = 'Failed'
                order.save()
                messages.error(request, "Invalid payment signature.")
                return redirect('buy_view')

        except Order.DoesNotExist:
            messages.error(request, "Order not found.")
            return redirect('buy_view')

        except Exception as e:
            messages.error(request, f"Error during payment: {e}")
            return redirect('buy_view')

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.core.mail import EmailMessage
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
import os
from django.conf import settings
from io import BytesIO

def download_invoice(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    # Generate PDF in memory
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # Company Branding (Header)
    p.setFillColor(colors.HexColor('#49986b'))
    p.rect(0, height - 100, width, 100, fill=1, stroke=0)
    p.setFillColor(colors.white)
    p.setFont("Helvetica", 24)
    p.drawCentredString(width / 2, height - 70, "NEGIZON")
    p.setFont("Helvetica", 10)
    p.drawCentredString(width / 2, height - 90, "Your One-Stop Store")
    p.line(50, height - 110, width - 50, height - 110)

    # Invoice Title and Number
    p.setFillColor(colors.black)
    p.setFont("Helvetica-Bold", 18)
    p.drawString(50, height - 140, f"Invoice - Order #{order.id}")
    p.setFont("Helvetica", 10)
    p.drawString(50, height - 155, f"Date: {order.order_time.strftime('%Y-%m-%d %H:%M:%S')}")
    p.drawString(200, height - 155, f"Invoice No: INV-{order.id:04d}")

    # Customer Information (Bill To)
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, height - 180, "Bill To:")
    p.setFont("Helvetica", 10)
    y = height - 195
    p.drawString(50, y, f"Name: {order.name or 'N/A'}")
    p.drawString(50, y - 12, f"Email: {order.email or 'N/A'}")
    p.drawString(50, y - 24, f"Phone: {order.phone or 'N/A'}")
    p.drawString(50, y - 36, f"Address: {order.address1 or ''} {order.address2 or ''}, {order.city or ''}, {order.state or ''}, {order.postal_code or ''}")

    # Draw Product Image between header and table
    image_size = 80
    image_x = width - image_size - 50
    image_y = (height - 110 + (y - 60)) / 2 - image_size / 2
    first_item = order.items.first()
    if first_item:
        try:
            image_path = first_item.sock.image.path
            if os.path.exists(image_path):
                p.drawImage(image_path, image_x, image_y, width=image_size, height=image_size, preserveAspectRatio=True)
            else:
                p.setFillColor(colors.grey)
                p.rect(image_x, image_y, image_size, image_size, fill=1, stroke=0)
                p.setFillColor(colors.white)
                p.setFont("Helvetica", 8)
                p.drawCentredString(image_x + image_size / 2, image_y + image_size / 2, "No Image")
        except AttributeError:
            p.setFillColor(colors.grey)
            p.rect(image_x, image_y, image_size, image_size, fill=1, stroke=0)
            p.setFillColor(colors.white)
            p.setFont("Helvetica", 8)
            p.drawCentredString(image_x + image_size / 2, image_y + image_size / 2, "No Image")

    # Items Table
    y -= 60
    data = [["Item", "Quantity", "Price (₹)", "Subtotal (₹)"]]
    for item in order.items.all():
        subtotal = item.quantity * item.price
        data.append([item.sock.name, str(item.quantity), f"{item.price:.2f}", f"{subtotal:.2f}"])

    table = Table(data, colWidths=[2.5 * inch, 1 * inch, 1 * inch, 1.5 * inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
    ]))
    table.wrapOn(p, width, height)
    table.drawOn(p, 50, y - table._height)

    # Total Section
    y -= table._height + 40
    p.setFont("Helvetica-Bold", 12)
    p.drawRightString(width - 150, y, "Subtotal:")
    p.drawRightString(width - 150, y - 15, "Shipping:")
    p.drawRightString(width - 150, y - 30, "Total:")
    p.setFont("Helvetica", 12)
    subtotal = sum(item.quantity * item.price for item in order.items.all())
    p.drawRightString(width - 50, y, f"₹{subtotal:.2f}")
    p.drawRightString(width - 50, y - 15, "₹150.00")
    p.drawRightString(width - 50, y - 30, f"₹{order.total_amount:.2f}")

    # Payment Method
    p.setFont("Helvetica-Bold", 10)
    p.drawString(50, y - 50, "Payment Method:")
    p.setFont("Helvetica", 10)
    p.drawString(150, y - 50, order.payment_method or 'N/A')

    # Footer
    p.showPage()
    p.setFont("Helvetica", 8)
    p.drawCentredString(width / 2, 50, "Thank you for shopping with NEGIZON!")
    p.drawCentredString(width / 2, 30, "Contact us at support@sockshop.com | Terms: Payment due within 30 days")

    p.save()

    # Get the PDF content from the buffer
    pdf_content = buffer.getvalue()

    # Send email with the PDF attachment and detailed product list
    if order.email:
        # Build the product details table for the email body
        product_details = "Order Details:\n\n"
        product_details += "Item Name\tQty\tPrice (₹)\tSubtotal (₹)\n"
        product_details += "-" * 50 + "\n"
        for item in order.items.all():
            subtotal = item.quantity * item.price
            product_details += f"{item.sock.name}\t{item.quantity}\t{item.price:.2f}\t{subtotal:.2f}\n"
        product_details += "-" * 50 + "\n"
        product_details += f"Subtotal:\t\t\t{sum(item.quantity * item.price for item in order.items.all()):.2f}\n"
        product_details += f"Shipping:\t\t\t150.00\n"
        product_details += f"Total:\t\t\t{order.total_amount:.2f}\n"
        product_details += f"Payment Method: {order.payment_method or 'N/A'}\n\n"

        email = EmailMessage(
            subject=f"Your Invoice for Order #{order.id} - NEGIZON",
            body=f"""
Dear {order.name or 'Customer'},

Thank you for shopping with NEGIZON! Please find attached the invoice for your order #{order.id}.

{product_details}

Order Date: {order.order_time.strftime('%Y-%m-%d %H:%M:%S')}

If you have any questions, feel free to contact us at support@sockshop.com.

Best regards,
The NEGIZON Team
            """,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[order.email],
        )
        email.attach(f'invoice_{order_id}.pdf', pdf_content, 'application/pdf')
        email.send(fail_silently=True)

    # Prepare the HTTP response for the user to download
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_{order_id}.pdf"'
    response.write(pdf_content)

    # Close the buffer
    buffer.close()

    return response

import random
import string
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.core.mail import EmailMessage
from django.conf import settings
from django.urls import reverse

User = get_user_model()

def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        otp = request.POST.get('otp')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        # Step 1: Send OTP
        if 'email' in request.POST and not request.POST.get('resend'):
            try:
                user = User.objects.get(email=email)
                # Generate OTP
                otp_value = ''.join(random.choices(string.digits, k=6))
                request.session['otp'] = otp_value
                request.session['email'] = email
                
                # Send OTP via email
                email_msg = EmailMessage(
                    subject="Your OTP for Password Reset",
                    body=f"Dear {user.username},\n\nYour OTP for password reset is: {otp_value}\n\nThis OTP is valid for 10 minutes.\n\nBest,\nThe NEGIZON Team",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[email],
                )
                email_msg.send(fail_silently=True)
                return render(request, 'store/forgot_password.html', {'step': 2})
            except User.DoesNotExist:
                return render(request, 'store/forgot_password.html', {'step': 1, 'error_message': 'No account exists with this email.'})

        # Step 2: Verify OTP
        elif 'otp' in request.POST:
            stored_otp = request.session.get('otp')
            if otp == stored_otp:
                del request.session['otp']  # Clear OTP after successful verification
                return render(request, 'store/forgot_password.html', {'step': 3})
            else:
                return render(request, 'store/forgot_password.html', {'step': 2, 'error_message': 'Wrong OTP. Please try again.'})

        # Step 3: Change Password
        elif 'new_password' in request.POST and 'confirm_password' in request.POST:
            email = request.session.get('email')
            user = User.objects.get(email=email)
            if new_password == confirm_password:
                user.set_password(new_password)
                user.save()
                del request.session['email']
                return redirect(reverse('signin'))  # Redirect to sign-in page
            else:
                return render(request, 'store/forgot_password.html', {'step': 3, 'error_message': 'Passwords do not match.'})

        # Resend OTP
        elif request.GET.get('resend'):
            try:
                user = User.objects.get(email=request.session.get('email'))
                otp_value = ''.join(random.choices(string.digits, k=6))
                request.session['otp'] = otp_value
                email_msg = EmailMessage(
                    subject="Your New OTP for Password Reset",
                    body=f"Dear {user.username},\n\nYour new OTP for password reset is: {otp_value}\n\nThis OTP is valid for 10 minutes.\n\nBest,\nThe NEGIZON Team",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[user.email],
                )
                email_msg.send(fail_silently=True)
                return render(request, 'store/forgot_password.html', {'step': 2})
            except Exception:
                return render(request, 'store/forgot_password.html', {'step': 2, 'error_message': 'Error resending OTP. Try again.'})

    # Initial render or invalid request
    return render(request, 'store/forgot_password.html', {'step': 1})
