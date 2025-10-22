from django import forms
from reviews.models import Reviews

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Reviews
        fields = ["venue_name", "rating", "comment", "image_url"]
        widgets = {
            'venue_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-green-500 focus:border-green-500 transition',
                'placeholder': 'Contoh: Cilandak Sport Center',
                'id': 'venue_name_input'
            }),
            # Rating akan di-handle oleh JavaScript (bintang), ini hanya hidden input
            'rating': forms.HiddenInput(attrs={'id': 'rating_input'}),
            'comment': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-green-500 focus:border-green-500 transition',
                'rows': 4,
                'placeholder': 'Ceritakan pengalamanmu di sini...',
                'id': 'comment_input'
            }),
            'image_url': forms.URLInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-green-500 focus:border-green-500 transition',
                'placeholder': 'https://contoh.com/gambar.png (Opsional)',
                'id': 'image_url_input'
            }),
        }
