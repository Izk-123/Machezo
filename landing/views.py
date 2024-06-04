from django.shortcuts import render

# Create your views here.
def index(request):
    template_url = 'landing/index.html'
    return render(request, template_url)