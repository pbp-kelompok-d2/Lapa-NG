from django.forms import ModelForm, Textarea, Select, TextInput
from .models import Post

class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ["content", "category", "thumbnail", "is_featured"]
        
        widgets = {
            'content': Textarea(attrs={
                'class': "border border-gray-300 rounded-lg p-2 w-full text-gray-800 focus:ring-emerald-500 focus:border-emerald-500",
                'rows': 5,
            }),
            'category': Select(attrs={
                'class': "border border-gray-300 rounded-lg p-2 w-full text-gray-800 focus:ring-emerald-500 focus:border-emerald-500",
            }),
            'thumbnail': TextInput(attrs={
                'class': "border border-gray-300 rounded-lg p-2 w-full text-gray-800 focus:ring-emerald-500 focus:border-emerald-500",
            }),
        }