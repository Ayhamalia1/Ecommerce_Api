from rest_framework import serializers
from .models import *
from account.serializers import UserSerializer
import json



class ProductSerializers(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model=Product 
        fields="__all__"

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model=Category
        fields="__all__"
        
class CartItemSerializer(serializers.ModelSerializer):
    productName = serializers.CharField(source='product.name', read_only=True)
    price = serializers.DecimalField(source='product.price',max_digits=10, decimal_places=2, read_only=True)
    productImage= serializers.ImageField(source='product.image',read_only=True)


    class Meta:
        model = CartItems
        fields = ['id', 'product','productName', 'quantity', 'price','productImage']
        
class CartSerializer(serializers.ModelSerializer):
    items =CartItemSerializer(many=True ,read_only=True)
    total = serializers.SerializerMethodField()
    count = serializers.SerializerMethodField()



    class Meta:
        model = Cart
        fields = ['id', 'user','items','total','count']
    def get_total(self, obj):
        total = sum([item.product.price * item.quantity for item in obj.items.all()])
        return total
    def get_count(self, obj):
        return obj.items.count()
    


class OrderItemSerializer(serializers.ModelSerializer):
    productName = serializers.CharField(source='product.name', read_only=True)
    productImage= serializers.ImageField(source='product.image')
    price = serializers.DecimalField(max_digits=7, decimal_places=2, read_only=True)  # ✅ read_only

    class Meta:
        model = OrderItem
        fields = ['id', 'product','productName', 'quantity', 'price','productImage']
class AddressSerializer(serializers.Serializer):
    fullName = serializers.CharField(
        required=True,
        min_length=3,
        max_length=100,
        error_messages={
            'required': 'الاسم الكامل مطلوب',
            'min_length': 'الاسم يجب أن يكون 3 أحرف على الأقل'
        }
    )
    phone = serializers.RegexField(
        regex=r'^[0-9]{10}$',
        required=True,
        error_messages={
            'required': 'رقم الهاتف مطلوب',
            'invalid': 'رقم الهاتف يجب أن يكون 10 أرقام'
        }
    )
    city = serializers.CharField(
        required=True,
        min_length=2,
        error_messages={
            'required': 'المدينة مطلوبة'
        }
    )
    street = serializers.CharField(
        required=True,
        min_length=2,
        error_messages={
            'required': 'الشارع مطلوبة'
        }
    )
        
    notes = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=500
    )
    
    def validate_fullName(self, value):
        """تنظيف وتحقق من الاسم"""
        value = value.strip()
        if not value:
            raise serializers.ValidationError('الاسم لا يمكن أن يكون فارغاً')
        return value
    
    def validate_phone(self, value):
        """تنظيف وتحقق من رقم الهاتف"""
        value = value.strip()
        if not value.isdigit():
            raise serializers.ValidationError('رقم الهاتف يجب أن يحتوي على أرقام فقط')
        return value
class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    user = UserSerializer(read_only=True)
    address_data = serializers.SerializerMethodField()  # ✅ إضافة هذا

    class Meta:
        model = Order
        fields = ['id', 'user', 'status', 'total', 'created_at', 'items', 'address_data']
    
    def get_address_data(self, obj):
        """تحويل address من JSON string إلى dict"""
        if isinstance(obj.address, str):
            try:
                return json.loads(obj.address)
            except json.JSONDecodeError:
                return {'error': 'Invalid JSON'}
        return obj.address

            
        

