from django.shortcuts import render

def contact(request): 
    return render(request, "sitepages/contact.html")

def about(request):
    return render(request, "sitepages/about.html")

def terms(request): 
    return render(request, "sitepages/terms.html") 

def privacy(request): 
    return render(request, "sitepages/privacy.html")
