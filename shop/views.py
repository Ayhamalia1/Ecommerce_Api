from rest_framework import viewsets, filters ,parsers,status
from .models import *
from .serializers import *
from rest_framework.permissions import IsAuthenticated
from .permissions import IsManagerOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404


import json



class ProductPagination(PageNumberPagination):
    page_size = 12
    page_size_query_param = 'page_size'
    max_page_size = 50


class ProductViewset(viewsets.ModelViewSet):
    serializer_class = ProductSerializers
    permission_classes = [IsManagerOrReadOnly]
    pagination_class = ProductPagination
    def get_queryset(self):
      product_catergory= self.request.query_params.get('category')
      if product_catergory:
        queryset=Product.objects.filter(category=product_catergory)
      else:
          queryset = Product.objects.all()
      return queryset


    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'price']
    search_fields = ['name', 'id']
    ordering_fields = ['price', 'created_at']
    parser_classes = [parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser]


class CategoryViewset(viewsets.ModelViewSet):
    serializer_class=CategorySerializer
    queryset=Category.objects.all()
    permission_classes = [IsManagerOrReadOnly]

class CartViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        cart, created = Cart.objects.get_or_create(user=request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def add(self, request):
        cart, created = Cart.objects.get_or_create(user=request.user)
        product_id = request.data.get('product')
        quantity = int(request.data.get("quantity", 1))

        if not product_id:
            return Response({'error': 'Product ID is required'}, status=400)

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=404)

        if quantity < 1:
            return Response({'error': 'Quantity must be at least 1'}, status=400)

        if quantity > product.stock:
            return Response({'error': 'Not enough stock'}, status=400)

        item, created = CartItems.objects.get_or_create(cart=cart, product=product)
        if not created:
            item.quantity += quantity
            if item.quantity > product.stock:
                item.quantity = product.stock
        else:
            item.quantity = quantity

        item.save()
        return Response({'message': 'Product added to cart'})
    @action(detail=False, methods=['post'])
    def remove(self ,request):
        cart =Cart.objects.filter(user=request.user).first()
        if not cart or not cart.items.exists():
            return Response({'error': 'Cart is empty'}, status=400)
        product_id =request.data.get('product')
        if not product_id:
            return Response({'error': 'Product ID is required'}, status=400)
        try:
            item=CartItems.objects.get(cart=cart ,product_id=product_id)
        except CartItems.DoesNotExist:
            return Response({'error': 'Product not in cart'}, status=404)
        item.delete()
        return Response({'message': 'Product removed from cart'})
    
    @action(detail=False, methods=['post'])
    def update_quantity(self, request):
        cart = Cart.objects.filter(user=request.user).first()
        if not cart or not cart.items.exists():
            return Response({'error': 'Cart is empty'}, status=400)

        product_id = request.data.get('product')
        quantity = request.data.get('quantity')

        if not product_id or quantity is None:
            return Response({'error': 'Product and quantity are required'}, status=400)

        try:
            item = CartItems.objects.get(cart=cart, product_id=product_id)
        except CartItems.DoesNotExist:
            return Response({'error': 'Product not in cart'}, status=404)

        if int(quantity) < 1:
            return Response({'error': 'Quantity must be at least 1'}, status=400)

        if item.product.stock < int(quantity):
            return Response({'error': 'Not enough stock'}, status=400)

        item.quantity = int(quantity)
        item.save()

        return Response({'message': 'Quantity updated successfully'})
             

class OrderViewset(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'manager':
            return Order.objects.all()
        return Order.objects.filter(user=user)
    
    @action(detail=False, methods=['post'])
    def create_order(self, request):
        try:
            user = request.user
            
            # 1. التحقق من السلة
            cart = Cart.objects.filter(user=user).first()
            
            if not cart or not cart.items.exists():
                return Response(
                    {'error': 'السلة فارغة'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # 2. الحصول على العنوان
            address_data = request.data.get('address')
            
            print("Received address data:", address_data)  # للتشخيص
            
            if not address_data:
                return Response(
                    {'error': 'العنوان مطلوب'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # 3. التحقق من صحة العنوان
            address_serializer = AddressSerializer(data=address_data)
            
            if not address_serializer.is_valid():
                print("Address validation errors:", address_serializer.errors)  # للتشخيص
                return Response(
                    {
                        'error': 'بيانات العنوان غير صحيحة',
                        'details': address_serializer.errors
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # 4. الحصول على البيانات المنظفة
            validated_address = address_serializer.validated_data
            
            # 5. إنشاء الأوردر
            order = Order.objects.create(
                user=user,
                address=json.dumps(validated_address, ensure_ascii=False)  # ✅ حفظ كـ JSON
            )

            total = 0

            # 6. معالجة العناصر
            for item in cart.items.all():
                product = item.product
                qty = item.quantity

                # التحقق من المخزون
                if product.stock < qty:
                    order.delete()
                    return Response(
                        {'error': f'المخزون غير كافٍ للمنتج: {product.name}'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                # إنشاء OrderItem
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=qty,
                    price=product.price
                )

                # تحديث المخزون
                product.stock -= qty
                product.save()

                # حساب المجموع
                total += product.price * qty

            # 7. حفظ المجموع
            order.total = total
            order.save()

            # 8. تفريغ السلة
            cart.items.all().delete()

            # 9. إرجاع البيانات
            serializer = OrderSerializer(order)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            print(f"Unexpected error: {str(e)}")  # للتشخيص
            return Response(
                {'error': f'حدث خطأ غير متوقع: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'total', 'created_at']
    search_fields = ['id', 'user__username']
    ordering_fields = ['created_at', 'total']
    @action(detail=True ,methods=['patch'])
    def update_status(self ,request ,pk=None):
        order = get_object_or_404(Order, pk=pk)
        newStatus=request.data.get("status")
        validate_status=['pending', 'processing', 'shipped', 'delivered', 'cancelled', 'completed']
        
        if request.user.role != 'manager':
             return Response(
                {'error': 'غير مصرح لك بتغيير حالة الطلب'},
                status=status.HTTP_403_FORBIDDEN
            )
        if not newStatus :
             return Response(
                {'error': 'حالة غير موجودة'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        if newStatus not in validate_status :
            return Response(
                {'error': 'حالة غير صالحة'},
                status=status.HTTP_400_BAD_REQUEST
            )
        order.status =newStatus
        order.save()
        
        serializer =OrderSerializer(order)
        return Response({
            'message': 'تم تحديث الحالة بنجاح',
            'order': serializer.data
        })
    







