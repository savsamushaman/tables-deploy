from django.shortcuts import render


def test_view(request):
    template_name = 'pages/index.html'
    return render(request, template_name, {})
