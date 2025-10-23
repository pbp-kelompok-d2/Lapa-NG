from django import forms
from reviews.models import Reviews

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Reviews
        # 'user' tidak ada di sini karena akan diisi otomatis oleh view
        fields = ['venue_name', 'rating', 'comment', 'image_url']
        
        # Berikan styling Tailwind langsung ke widget
        widgets = {
            'venue_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-green-500 focus:border-green-500 transition',
                'placeholder': 'Nama Lapangan (mis: Cilandak Sport Center)',
                'id': 'venue_name_input' # ID unik
            }),
            'rating': forms.HiddenInput(attrs={
                'id': 'rating_input' # Input tersembunyi untuk menyimpan nilai 1-5
            }),
            'comment': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-green-500 focus:border-green-500 transition',
                'rows': 3,
                'placeholder': 'Ceritakan pengalamanmu di sini...',
                'id': 'comment_input'
            }),
            'image_url': forms.URLInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-green-500 focus:border-green-500 transition',
                'placeholder': 'https://contoh.com/gambar.png (Opsional)',
                'id': 'image_url_input'
            }),
        }
