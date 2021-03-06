from django.contrib.auth import login, authenticate
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404, redirect
from django.template.loader import render_to_string
from django.views.generic import DetailView, View
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from .models import UserProfile
from .forms import UserRegisterForm
from .tokens import account_activation_token

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            date_of_birth = form.cleaned_data.get('date_of_birth')
            new_user = form.save(commit=False)
            new_user.is_active = False
            new_user.save()
            profile = new_user.profile
            profile.date_of_birth = date_of_birth
            profile.save()
            current_site = get_current_site(request)
            message = render_to_string('email_activation_link.html', {
                'new_user':new_user,
                'domain':current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(new_user.pk)),
                'token': account_activation_token.make_token(new_user),
            })
            mail_subject = 'Activate your Frac account.'
            to_email = EmailMessage(mail_subject, message, to=[email])
            to_email.send()
            return render(request, 'register_confirm.html', {'form': form})
    else:
        form = UserRegisterForm()

    return render(request, 'register.html', {'form': form})

# Only if we want to automatically login users when they signed up
spec_backend = 'django.contrib.auth.backends.ModelBackend'

def activate(request, uidb64, token): #, backend=spec_backend):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        new_user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        new_user = None
    if new_user is not None and account_activation_token.check_token(new_user, token):
        new_user.is_active = True
        new_user.save()
        #login(request, user, backend=spec_backend)
        return render(request, 'register_complete.html', {})
    else:
        return render(request, 'registration_incomplete.html', {})


class UserProfileView(DetailView):
    template_name = 'accounts/user_profile.html'
    queryset = User.objects.all()

    def get_object(self):
        '''
        lookup field with username for the url
        '''
        return get_object_or_404(User,
                                    username__iexact=self.kwargs.get('username'))

    def get_context_data(self, *args, **kwargs):
        context = super(UserProfileView, self).get_context_data(*args, **kwargs)
        following = UserProfile.objects.is_following(self.request.user, self.get_object())
        context['following'] = following
        return context


class UserFollowView(View):
    '''
    follow toggle based on a url
    '''
    def get(self, request, username, *args, **kwargs):
        toggle_user = get_object_or_404(User, username__iexact=username)
        if request.user.is_authenticated():
            is_following = UserProfile.objects.toggle_follow(request.user, toggle_user)
        return redirect("profiles:detail", username=username)
