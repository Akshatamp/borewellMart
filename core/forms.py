from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.files.uploadedfile import InMemoryUploadedFile
from .models import UserProfile, Vendor, VendorService, Booking, Review, VendorGallery, Blog, City, SubService, Sector, Service, Enquiry, BookingPayment, ForumCategory, ForumThread, ForumPost, ForumTag, ForumThreadService, Community, CommunityPost, CommunityComment, VendorEquipment, EquipmentInquiry, Partner, PartnerCoupon
from .utils import validate_image_size, compress_image


class BulkVendorRegistrationForm(forms.Form):
    """Form for bulk vendor registration via Excel upload"""
    excel_file = forms.FileField(
        label='Upload Excel File (.xlsx or .xls)',
        required=True,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.xlsx,.xls'
        }),
        help_text='Maximum 100 vendors per day. File should contain columns: company_name, email, phone, city, address, experience, license_number'
    )

    def clean_excel_file(self):
        file = self.cleaned_data.get('excel_file')
        if file:
            # Check file extension
            if not file.name.endswith(('.xlsx', '.xls')):
                raise forms.ValidationError('Only Excel files (.xlsx or .xls) are allowed.')
        return file


class VendorUserRegisterForm(UserCreationForm):
    STATE_CHOICES = [
        ('', 'Select State'),
        ('Andhra Pradesh', 'Andhra Pradesh'),
        ('Arunachal Pradesh', 'Arunachal Pradesh'),
        ('Assam', 'Assam'),
        ('Bihar', 'Bihar'),
        ('Chhattisgarh', 'Chhattisgarh'),
        ('Goa', 'Goa'),
        ('Gujarat', 'Gujarat'),
        ('Haryana', 'Haryana'),
        ('Himachal Pradesh', 'Himachal Pradesh'),
        ('Jharkhand', 'Jharkhand'),
        ('Karnataka', 'Karnataka'),
        ('Kerala', 'Kerala'),
        ('Madhya Pradesh', 'Madhya Pradesh'),
        ('Maharashtra', 'Maharashtra'),
        ('Manipur', 'Manipur'),
        ('Meghalaya', 'Meghalaya'),
        ('Mizoram', 'Mizoram'),
        ('Nagaland', 'Nagaland'),
        ('Odisha', 'Odisha'),
        ('Punjab', 'Punjab'),
        ('Rajasthan', 'Rajasthan'),
        ('Sikkim', 'Sikkim'),
        ('Tamil Nadu', 'Tamil Nadu'),
        ('Telangana', 'Telangana'),
        ('Tripura', 'Tripura'),
        ('Uttar Pradesh', 'Uttar Pradesh'),
        ('Uttarakhand', 'Uttarakhand'),
        ('West Bengal', 'West Bengal'),
        ('Andaman and Nicobar Islands', 'Andaman and Nicobar Islands'),
        ('Chandigarh', 'Chandigarh'),
        ('Dadra and Nagar Haveli and Daman and Diu', 'Dadra and Nagar Haveli and Daman and Diu'),
        ('Delhi', 'Delhi'),
        ('Jammu and Kashmir', 'Jammu and Kashmir'),
        ('Ladakh', 'Ladakh'),
        ('Lakshadweep', 'Lakshadweep'),
        ('Puducherry', 'Puducherry'),
    ]

    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=15, required=True)
    city = forms.ModelChoiceField(queryset=None, required=True)
    state = forms.ChoiceField(choices=STATE_CHOICES, required=False, widget=forms.Select(attrs={'class': 'form-select'}))

    # Vendor-specific fields
    company_name = forms.CharField(max_length=200, required=True)
    experience = forms.IntegerField(required=True, min_value=0)
    address = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=True)
    license_number = forms.CharField(max_length=100, required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from .models import City
        self.fields['city'].queryset = City.objects.all()

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            # Create UserProfile
            UserProfile.objects.create(
                user=user,
                phone=self.cleaned_data['phone'],
                user_type='vendor',
                city=self.cleaned_data['city'],
                state=self.cleaned_data.get('state', '')
            )
            # Create Vendor profile
            from .models import Vendor
            Vendor.objects.create(
                user=user,
                company_name=self.cleaned_data['company_name'],
                city=self.cleaned_data['city'],
                state=self.cleaned_data.get('state', ''),
                experience=self.cleaned_data['experience'],
                phone=self.cleaned_data['phone'],
                email=self.cleaned_data['email'],
                address=self.cleaned_data['address'],
                license_number=self.cleaned_data.get('license_number', ''),
                verification_status='pending'
            )
        return user


class UserRegisterForm(UserCreationForm):
    STATE_CHOICES = [
        ('', 'Select States'),
        ('Andhra Pradesh', 'Andhra Pradesh'),
        ('Arunachal Pradesh', 'Arunachal Pradesh'),
        ('Assam', 'Assam'),
        ('Bihar', 'Bihar'),
        ('Chhattisgarh', 'Chhattisgarh'),
        ('Goa', 'Goa'),
        ('Gujarat', 'Gujarat'),
        ('Haryana', 'Haryana'),
        ('Himachal Pradesh', 'Himachal Pradesh'),
        ('Jharkhand', 'Jharkhand'),
        ('Karnataka', 'Karnataka'),
        ('Kerala', 'Kerala'),
        ('Madhya Pradesh', 'Madhya Pradesh'),
        ('Maharashtra', 'Maharashtra'),
        ('Manipur', 'Manipur'),
        ('Meghalaya', 'Meghalaya'),
        ('Mizoram', 'Mizoram'),
        ('Nagaland', 'Nagaland'),
        ('Odisha', 'Odisha'),
        ('Punjab', 'Punjab'),
        ('Rajasthan', 'Rajasthan'),
        ('Sikkim', 'Sikkim'),
        ('Tamil Nadu', 'Tamil Nadu'),
        ('Telangana', 'Telangana'),
        ('Tripura', 'Tripura'),
        ('Uttar Pradesh', 'Uttar Pradesh'),
        ('Uttarakhand', 'Uttarakhand'),
        ('West Bengal', 'West Bengal'),
        ('Andaman and Nicobar Islands', 'Andaman and Nicobar Islands'),
        ('Chandigarh', 'Chandigarh'),
        ('Dadra and Nagar Haveli and Daman and Diu', 'Dadra and Nagar Haveli and Daman and Diu'),
        ('Delhi', 'Delhi'),
        ('Jammu and Kashmir', 'Jammu and Kashmir'),
        ('Ladakh', 'Ladakh'),
        ('Lakshadweep', 'Lakshadweep'),
        ('Puducherry', 'Puducherry'),
    ]

    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=15, required=True)
    user_type = forms.ChoiceField(choices=UserProfile.USER_TYPE_CHOICES, required=True)
    city = forms.ModelChoiceField(queryset=None, required=False)
    state = forms.ChoiceField(choices=STATE_CHOICES, required=False, widget=forms.Select(attrs={'class': 'form-select'}))
    profile_image = forms.ImageField(required=False, widget=forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}))

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from .models import City
        self.fields['city'].queryset = City.objects.all()

    def clean_profile_image(self):
        image = self.cleaned_data.get('profile_image')
        if image:
            is_valid, error_msg = validate_image_size(image, max_size_mb=1)
            if not is_valid:
                raise forms.ValidationError(error_msg)
            # Compress image and return as InMemoryUploadedFile
            return compress_image(image, max_size=(300, 300), quality=85)
        return image

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            UserProfile.objects.create(
                user=user,
                phone=self.cleaned_data['phone'],
                user_type=self.cleaned_data['user_type'],
                city=self.cleaned_data['city'],
                state=self.cleaned_data.get('state', ''),
                profile_image=self.cleaned_data.get('profile_image')
            )
        return user


class CustomerProfileForm(forms.ModelForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    profile_image = forms.ImageField(required=False, widget=forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}))

    class Meta:
        model = UserProfile
        fields = ['phone', 'city', 'address', 'profile_image']
        widgets = {
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.Select(attrs={'class': 'form-select'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        from .models import City
        self.fields['city'].queryset = City.objects.all()
        if self.user:
            self.fields['email'].initial = self.user.email
            self.fields['first_name'].initial = self.user.first_name
            self.fields['last_name'].initial = self.user.last_name

    def save(self, commit=True):
        profile = super().save(commit=False)
        if self.user:
            self.user.email = self.cleaned_data['email']
            self.user.first_name = self.cleaned_data['first_name']
            self.user.last_name = self.cleaned_data['last_name']
            if commit:
                self.user.save()
        if commit:
            profile.save()
        return profile


class VendorProfileForm(forms.ModelForm):
    STATE_CHOICES = [
        ('', 'Select State'),
        ('Andhra Pradesh', 'Andhra Pradesh'),
        ('Arunachal Pradesh', 'Arunachal Pradesh'),
        ('Assam', 'Assam'),
        ('Bihar', 'Bihar'),
        ('Chhattisgarh', 'Chhattisgarh'),
        ('Goa', 'Goa'),
        ('Gujarat', 'Gujarat'),
        ('Haryana', 'Haryana'),
        ('Himachal Pradesh', 'Himachal Pradesh'),
        ('Jharkhand', 'Jharkhand'),
        ('Karnataka', 'Karnataka'),
        ('Kerala', 'Kerala'),
        ('Madhya Pradesh', 'Madhya Pradesh'),
        ('Maharashtra', 'Maharashtra'),
        ('Manipur', 'Manipur'),
        ('Meghalaya', 'Meghalaya'),
        ('Mizoram', 'Mizoram'),
        ('Nagaland', 'Nagaland'),
        ('Odisha', 'Odisha'),
        ('Punjab', 'Punjab'),
        ('Rajasthan', 'Rajasthan'),
        ('Sikkim', 'Sikkim'),
        ('Tamil Nadu', 'Tamil Nadu'),
        ('Telangana', 'Telangana'),
        ('Tripura', 'Tripura'),
        ('Uttar Pradesh', 'Uttar Pradesh'),
        ('Uttarakhand', 'Uttarakhand'),
        ('West Bengal', 'West Bengal'),
        ('Andaman and Nicobar Islands', 'Andaman and Nicobar Islands'),
        ('Chandigarh', 'Chandigarh'),
        ('Dadra and Nagar Haveli and Daman and Diu', 'Dadra and Nagar Haveli and Daman and Diu'),
        ('Delhi', 'Delhi'),
        ('Jammu and Kashmir', 'Jammu and Kashmir'),
        ('Ladakh', 'Ladakh'),
        ('Lakshadweep', 'Lakshadweep'),
        ('Puducherry', 'Puducherry'),
    ]

    state = forms.ChoiceField(choices=STATE_CHOICES, required=False, widget=forms.Select(attrs={'class': 'form-select'}))

    class Meta:
        model = Vendor
        fields = ['company_name', 'logo', 'cover_image', 'city', 'state', 'experience',
                  'phone', 'email', 'address', 'license_number', 'certifications', 'is_emergency_available']
        widgets = {
            'company_name': forms.TextInput(attrs={'class': 'form-control'}),
            'logo': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'cover_image': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'city': forms.Select(attrs={'class': 'form-select'}),
            'experience': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'rating': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'min': '0', 'max': '5'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'license_number': forms.TextInput(attrs={'class': 'form-control'}),
            'certifications': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Enter certifications separated by commas', 'class': 'form-control'}),
            'is_emergency_available': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean_logo(self):
        logo = self.cleaned_data.get('logo')
        if logo:
            is_valid, error_msg = validate_image_size(logo, max_size_mb=2)
            if not is_valid:
                raise forms.ValidationError(error_msg)
            # Compress image and return as InMemoryUploadedFile
            return compress_image(logo, max_size=(400, 400), quality=85)
        return logo

    def clean_cover_image(self):
        cover_image = self.cleaned_data.get('cover_image')
        if cover_image:
            is_valid, error_msg = validate_image_size(cover_image, max_size_mb=3)
            if not is_valid:
                raise forms.ValidationError(error_msg)
            # Compress image and return as InMemoryUploadedFile
            return compress_image(cover_image, max_size=(1200, 400), quality=85)
        return cover_image


class VendorServiceForm(forms.ModelForm):
    sector = forms.ModelChoiceField(
        queryset=Sector.objects.none(),
        required=True,
        empty_label="Select Sector",
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'sector-select'})
    )
    service = forms.ModelChoiceField(
        queryset=Service.objects.none(),
        required=False,
        empty_label="Select Service",
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'service-select'})
    )
    service_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter new service name if not listed (optional)',
            'id': 'service-input'
        })
    )
    subservice_name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter subservice name (e.g., Borewell Drilling, Pump Repair)'
        })
    )

    class Meta:
        model = VendorService
        fields = ['description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['sector'].queryset = Sector.objects.all().order_by('order')
        self.fields['service'].queryset = Service.objects.select_related('sector').all().order_by('sector__order', 'order')

        if self.instance and self.instance.pk:
            if self.instance.subservice and self.instance.subservice.service:
                self.fields['service'].initial = self.instance.subservice.service
                self.fields['service_name'].initial = ''
                self.fields['subservice_name'].initial = self.instance.subservice.name

    def clean(self):
        cleaned_data = super().clean()
        service = cleaned_data.get('service')
        service_name = cleaned_data.get('service_name')

        if not service and not service_name:
            raise forms.ValidationError('Select an existing service or enter a new service name.')

        return cleaned_data

    def clean_subservice_name(self):
        subservice_name = self.cleaned_data.get('subservice_name')
        if not subservice_name:
            raise forms.ValidationError('SubService name is required.')
        return subservice_name.strip()


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['date', 'time', 'address', 'description']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'time': forms.TimeInput(attrs={'type': 'time'}),
            'address': forms.Textarea(attrs={'rows': 3}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment', 'customer_image']
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 4}),
            'customer_image': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        }

    def clean_customer_image(self):
        image = self.cleaned_data.get('customer_image')
        if image:
            is_valid, error_msg = validate_image_size(image, max_size_mb=1)
            if not is_valid:
                raise forms.ValidationError(error_msg)
            # Compress image
            compressed = compress_image(image, max_size=(300, 300), quality=85)
            return InMemoryUploadedFile(
                compressed, None, image.name, 'image/jpeg', compressed.tell(), None
            )
        return image


class VendorGalleryForm(forms.ModelForm):
    class Meta:
        model = VendorGallery
        fields = ['image', 'caption', 'image_type']
        widgets = {
            'image': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        }

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            is_valid, error_msg = validate_image_size(image, max_size_mb=2)
            if not is_valid:
                raise forms.ValidationError(error_msg)
            # Compress image
            compressed = compress_image(image, max_size=(800, 800), quality=85)
            return InMemoryUploadedFile(
                compressed, None, image.name, 'image/jpeg', compressed.tell(), None
            )
        return image


class CityForm(forms.ModelForm):
    class Meta:
        model = City
        fields = ['name', 'image', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'image': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        }

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            is_valid, error_msg = validate_image_size(image, max_size_mb=2)
            if not is_valid:
                raise forms.ValidationError(error_msg)
            # Compress image
            compressed = compress_image(image, max_size=(800, 600), quality=85)
            return InMemoryUploadedFile(
                compressed, None, image.name, 'image/jpeg', compressed.tell(), None
            )
        return image


class SubServiceForm(forms.ModelForm):
    """Form for SubService (formerly Service)"""
    class Meta:
        model = SubService
        fields = ['name', 'image', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'image': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        }

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            is_valid, error_msg = validate_image_size(image, max_size_mb=1)
            if not is_valid:
                raise forms.ValidationError(error_msg)
            # Compress image
            compressed = compress_image(image, max_size=(400, 400), quality=85)
            return InMemoryUploadedFile(
                compressed, None, image.name, 'image/jpeg', compressed.tell(), None
            )
        return image


class BlogForm(forms.ModelForm):
    class Meta:
        model = Blog
        fields = ['title', 'slug', 'image', 'content', 'category']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 10}),
            'image': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        }

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            is_valid, error_msg = validate_image_size(image, max_size_mb=2)
            if not is_valid:
                raise forms.ValidationError(error_msg)
            # Compress image
            compressed = compress_image(image, max_size=(1200, 630), quality=85)
            return InMemoryUploadedFile(
                compressed, None, image.name, 'image/jpeg', compressed.tell(), None
            )
        return image


class EnquiryForm(forms.ModelForm):
    class Meta:
        model = Enquiry
        fields = ['subservice', 'message']
        widgets = {
            'subservice': forms.Select(attrs={'class': 'form-select'}),
            'message': forms.Textarea(attrs={'rows': 6, 'class': 'form-control', 'placeholder': 'Describe your requirements, location, depth of borewell (if applicable), and any specific details about the service you need...'}),
        }

    def __init__(self, *args, vendor=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.vendor = vendor

        if vendor is not None:
            vendor_subservice_ids = VendorService.objects.filter(vendor=vendor).values_list('subservice_id', flat=True)
            self.fields['subservice'].queryset = SubService.objects.filter(id__in=vendor_subservice_ids).order_by('name')
        else:
            self.fields['subservice'].queryset = SubService.objects.none()

    def clean_subservice(self):
        subservice = self.cleaned_data.get('subservice')
        if self.vendor and subservice:
            if not VendorService.objects.filter(vendor=self.vendor, subservice=subservice).exists():
                raise forms.ValidationError('Please select a service offered by this vendor.')
        return subservice


class EnquiryResponseForm(forms.ModelForm):
    class Meta:
        model = Enquiry
        fields = ['vendor_response', 'quoted_amount']
        widgets = {
            'vendor_response': forms.Textarea(attrs={'rows': 6, 'class': 'form-control', 'placeholder': 'Provide detailed pricing information (e.g., drilling charges, pipe charges per foot, labor costs, etc.) and service details...'}),
            'quoted_amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter the total amount in ₹', 'step': '0.01'}),
        }


class BookingPaymentForm(forms.ModelForm):
    class Meta:
        model = BookingPayment
        fields = ['transaction_id']
        widgets = {
            'transaction_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your UPI transaction ID'}),
        }


# ==================== FORUM FORMS ====================

class ForumThreadForm(forms.ModelForm):
    """Form for creating/editing forum threads"""
    tags = forms.ModelMultipleChoiceField(
        queryset=ForumTag.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        help_text='Select relevant tags for your question'
    )
    subservices = forms.ModelMultipleChoiceField(
        queryset=SubService.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        help_text='Link to specific subservices (optional)'
    )

    class Meta:
        model = ForumThread
        fields = ['title', 'category', 'content', 'tags', 'subservices']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'What\'s your question? Be specific.',
                'required': 'required'
            }),
            'category': forms.Select(attrs={
                'class': 'form-select',
                'required': 'required'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'Describe your issue in detail. Include symptoms, what you\'ve tried, and what you need help with.',
                'required': 'required'
            }),
        }


class ForumPostForm(forms.ModelForm):
    """Form for creating replies/posts"""
    class Meta:
        model = ForumPost
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Write your answer or reply...',
                'required': 'required'
            }),
        }


class ForumCategoryForm(forms.ModelForm):
    """Admin form for forum categories"""
    class Meta:
        model = ForumCategory
        fields = ['name', 'description', 'icon', 'order', 'is_service_related', 'sector']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'icon': forms.TextInput(attrs={'class': 'form-control'}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
        }


# ==================== COMMUNITY FORMS ====================

class CommunityForm(forms.ModelForm):
    """Form for creating/editing communities (admin only)"""
    class Meta:
        model = Community
        fields = ['name', 'description', 'image', 'cover_image']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Community name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Describe what this community is about...'}),
            'image': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'cover_image': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        }

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            is_valid, error_msg = validate_image_size(image, max_size_mb=2)
            if not is_valid:
                raise forms.ValidationError(error_msg)
            return compress_image(image, max_size=(400, 400), quality=85)
        return image

    def clean_cover_image(self):
        image = self.cleaned_data.get('cover_image')
        if image:
            is_valid, error_msg = validate_image_size(image, max_size_mb=3)
            if not is_valid:
                raise forms.ValidationError(error_msg)
            return compress_image(image, max_size=(1200, 400), quality=85)
        return image


class CommunityPostForm(forms.ModelForm):
    """Form for creating posts in communities"""
    class Meta:
        model = CommunityPost
        fields = ['content', 'image', 'post_type']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'What\'s on your mind? Share updates, questions, or announcements...'
            }),
            'image': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'post_type': forms.Select(attrs={'class': 'form-select'}),
        }

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            is_valid, error_msg = validate_image_size(image, max_size_mb=2)
            if not is_valid:
                raise forms.ValidationError(error_msg)
            compressed = compress_image(image, max_size=(800, 600), quality=85)
            return InMemoryUploadedFile(
                compressed, None, image.name, 'image/jpeg', compressed.tell(), None
            )
        return image


class CommunityCommentForm(forms.ModelForm):
    """Form for commenting on community posts"""
    class Meta:
        model = CommunityComment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Write a comment...'
            }),
        }


class VendorEquipmentForm(forms.ModelForm):
    """Form for adding/editing vendor equipment"""
    class Meta:
        model = VendorEquipment
        fields = ['title', 'description', 'category', 'condition', 'price', 'is_negotiable',
                  'image', 'year_manufactured', 'brand', 'location', 'is_available']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Used Borewell Drilling Rig - 200ft Capacity'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe the equipment, its condition, usage history, and any other relevant details...'
            }),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'condition': forms.Select(attrs={'class': 'form-select'}),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter price in INR',
                'min': '0',
                'step': '0.01'
            }),
            'is_negotiable': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'image': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'year_manufactured': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 2018',
                'min': '1980',
                'max': '2026'
            }),
            'brand': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., JCB, Kirloskar, L&T...'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Nagpur, Maharashtra'
            }),
            'is_available': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            is_valid, error_msg = validate_image_size(image, max_size_mb=2)
            if not is_valid:
                raise forms.ValidationError(error_msg)
            compressed = compress_image(image, max_size=(800, 600), quality=85)
            return InMemoryUploadedFile(
                compressed, None, image.name, 'image/jpeg', compressed.tell(), None
            )
        return image


class EquipmentInquiryForm(forms.ModelForm):
    """Form for customer inquiries about equipment"""
    class Meta:
        model = EquipmentInquiry
        fields = ['message']
        widgets = {
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'I am interested in this equipment. Please provide more details about availability and pricing...'
            }),
        }


class PartnerUserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=15, required=True)
    company_name = forms.CharField(max_length=200, required=True, label='Your Name / Company Name')

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('An account with this email already exists.')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            UserProfile.objects.create(
                user=user,
                phone=self.cleaned_data['phone'],
                user_type='partner',
            )
            Partner.objects.create(
                user=user,
                company_name=self.cleaned_data['company_name'],
                phone=self.cleaned_data['phone'],
                status='pending',
            )
        return user


class PartnerCouponForm(forms.ModelForm):
    """Form for partners to create tracking coupon codes"""
    class Meta:
        model = PartnerCoupon
        fields = ['code', 'max_uses']
        widgets = {
            'max_uses': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
        }

    def clean_code(self):
        import re
        code = self.cleaned_data.get('code', '').strip().upper()
        if code:
            if not re.match(r'^[A-Z0-9]+$', code):
                raise forms.ValidationError('Code can only contain letters and numbers.')
            if len(code) < 6:
                raise forms.ValidationError('Code must be at least 6 characters.')
            if len(code) > 20:
                raise forms.ValidationError('Code cannot exceed 20 characters.')
        return code
