# sweetspot_app/views.py
from sweetspot_pro import settings
import googlemaps  # type: ignore
from django.conf import settings
from django.shortcuts import get_object_or_404
from .models import Customer, Cake, Cart, CartItem, CakeCustomization, Order
from .serializers import CustomerSerializer, CakeSerializer, CartSerializer, OrderSerializer, CakeCustomizationSerializer
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.core.mail import send_mail
from .models import Customer, Cart, Order, CakeCustomization
from .serializers import OrderSerializer
import threading
import time


class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

    @action(detail=False, methods=['post'])
    def login(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        
        try:
            customer = Customer.objects.get(email=email, password=password)
            return Response({'message': 'Login Successful'})
        except Customer.DoesNotExist:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)

class CakeViewSet(viewsets.ModelViewSet):
    queryset = Cake.objects.all()
    serializer_class = CakeSerializer

class CakeCustomizationViewSet(viewsets.ModelViewSet):
    queryset = CakeCustomization.objects.all()
    serializer_class = CakeCustomizationSerializer

class CartViewSet(viewsets.ModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer

    def create(self, request, *args, **kwargs):
        customer_id = request.data.get('customer')
        
        existing_cart = Cart.objects.filter(customer_id=customer_id, is_active=True).first()
        
        if existing_cart:
            return Response(CartSerializer(existing_cart).data, status=status.HTTP_200_OK)

        return super().create(request, *args, **kwargs)

    @action(detail=True, methods=['post'])
    def add_item(self, request, pk=None):
        try:
            cart = self.get_object()
            if not cart.is_active:
                return Response({'error': 'This cart is no longer active'}, status=status.HTTP_400_BAD_REQUEST)

            cake_id = request.data.get('cake_id')
            quantity = request.data.get('quantity', 1)
            customization_data = request.data.get('customization')

            cake = get_object_or_404(Cake, id=cake_id)
            if not cake.available:
                return Response({'error': 'This cake is not available'}, status=status.HTTP_400_BAD_REQUEST)

            customization = None
            if customization_data:
                customization = CakeCustomization.objects.create(cake=cake, customer=cart.customer, **customization_data)

            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                cake=cake,
                defaults={'quantity': quantity, 'customization': customization}
            )

            if not created:
                cart_item.quantity += quantity
                cart_item.save()

            return Response(CartSerializer(cart).data, status=status.HTTP_200_OK)

        except Cart.DoesNotExist:
            return Response({'error': 'Cart not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

def send_email(subject, message, recipient):
    try:
        send_mail(subject, message, settings.EMAIL_HOST_USER, [recipient], fail_silently=True)
    except Exception as e:
        print(f"An error occurred while sending the email: {e}")

def order_confirmation_email(order):
    customer = order.customer
    subject = 'Order Confirmation - SweetSpot'
    message = f"""
    Dear {customer.last_name},

    Thank you for your order!

    Order ID: {order.id}
    Total Amount: ₹ {order.total_price}
    Payment Method: {order.payment_method}
    
    Estimated delivery duration: {order.duration}    
    Delivery Distance: {order.distance}

    We'll notify you once your order is ready for delivery.

    Best regards,
    SweetSpot Team
    """
    send_email(subject, message, customer.email)

def order_ready_email(order):
    time.sleep(300)  
    customer = order.customer
    subject = 'Your Order Will Be Delivered Soon!'
    message = f"""
    Dear {customer.last_name},

    Your order is almost ready and will be delivered in approximately 5 minutes.

    Order ID: {order.id}
    Delivery Distance: {order.distance}

    Best regards,
    SweetSpot Team
    """
    send_email(subject, message, customer.email)

def order_delivered_email(order):
    time.sleep(600)  
    customer = order.customer
    subject = 'Order Delivered'
    message = f"""
    Dear {customer.last_name},

    Your order has been successfully delivered!

    Order ID: {order.id}
    Delivery Distance: {order.distance}

    We hope you enjoy your purchase. Thank you for choosing SweetSpot!

    Best regards,
    SweetSpot Team
    """
    send_email(subject, message, customer.email)

gmaps = googlemaps.Client(key=settings.GOOGLE_MAPS_API_KEY)

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    @action(detail=False, methods=['post'])
    def place_order(self, request):
        customer_id = request.data.get('customer_id')
        payment_method = request.data.get('payment_method', 'cod')
        card_holder_name = request.data.get('card_holder_name')
        card_number = request.data.get('card_number')
        cvv = request.data.get('cvv')
        expiration_date = request.data.get('expiration_date')

        try:
            customer = get_object_or_404(Customer, id=customer_id)
            cart = Cart.objects.get(customer=customer, is_active=True)

            if not cart.items.exists():
                return Response({'error': 'Cart is empty'}, status=status.HTTP_400_BAD_REQUEST)

            total_price = cart.total_amount
            order = Order.objects.create(
                customer=customer,
                total_price=total_price,
                delivery_address=customer.address,
                payment_method=payment_method,
                card_holder_name=card_holder_name,
                card_number=card_number,
                cvv=cvv,
                expiration_date=expiration_date
            )

            for cart_item in cart.items.all():
                order.items.add(cart_item.cake)
                if cart_item.customization:
                    order_customization = CakeCustomization.objects.create(
                        message=cart_item.customization.message,
                        egg_version=cart_item.customization.egg_version,
                        toppings=cart_item.customization.toppings,
                        shape=cart_item.customization.shape,
                        cake=cart_item.cake,
                        customer=customer
                    )
                    order.cake_customization = order_customization
                    order.save()

            
            origin = "Kovvada"  
            destination = customer.city 

            distance_result = gmaps.distance_matrix(origin, destination)

            element = distance_result['rows'][0]['elements'][0]
            if element['status'] == 'OK':
                distance = element['distance']['text']
                duration = element['duration']['text']
                
                order.distance = distance 
                order.duration = duration  
            else:
                order.distance = "Distance not available"
                order.duration = "Duration not available"

            order.save()  
            
            threading.Thread(target=order_confirmation_email, args=(order,)).start()
            threading.Thread(target=order_ready_email, args=(order,)).start()
            threading.Thread(target=order_delivered_email, args=(order,)).start()

            cart.items.all().delete()
            cart.is_active = False
            cart.save()

            Cart.objects.create(customer=customer)

            return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)

        except Cart.DoesNotExist:
            return Response({'error': 'No active cart found for this customer'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['patch'])
    def update_payment(self, request, pk=None):
        order = self.get_object()
        order.payment_status = request.data.get('payment_status', order.payment_status)
        order.payment_method = request.data.get('payment_method', order.payment_method)
        order.save()
        return Response(OrderSerializer(order).data)
