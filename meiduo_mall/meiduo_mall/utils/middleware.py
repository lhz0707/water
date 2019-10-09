from django.shortcuts import render, redirect
def myview(get_response):
    def middle(request, *args, **kwargs):
        if request.path in ['/info/','/address/']:
            if not request.user.is_authenticated:
                return redirect('/login/?next=%s'%request.path)

        respone = get_response(request, *args, **kwargs)

        return respone

    return middle
