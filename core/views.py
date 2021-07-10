from django.shortcuts import render, redirect
# from .forms import NewUserForm, UpdateProfile, UploadFileForm, ModelFormWithFileField, FileFieldForm, FormView, ImageForm
# from .models import ModelWithFileField
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.messages import get_messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.forms import modelformset_factory
from django.http import HttpResponseRedirect, JsonResponse
from django.template import RequestContext
from django.urls import reverse
from django.views.generic.edit import FormView

from .forms import NewUserForm, UpdateProfile, UploadFileForm, FileFieldForm, ImageForm, PostForm, ImageTrimForm, ImageFrameForm, ImageRemoveBackgroundForm
from .models import Images
from .utility import handle_uploaded_file
from .image_processing_methods import compress, trim, frame, convert_jpg_to_png, remove_background

# Create your views here.
def homepage(request):
    return render(request, 'core/header.html', {'title': 'header'})

def update_profile_success(request):
    return render(request, 'core/update_profile_success.html', {'title': 'update_profile_success'})

def register_request(request):
    if request.method == "POST":
        form = NewUserForm(request.POST)
        print('0')
        print(form.is_valid())
        if form.is_valid():
            print('1')
            user = form.save(1)
            print('2')
            login(request, user)
            print("[+] user, type(user): ", user, type(user))
            print("[+] dir(user): ", dir(user))
            print("[+] user.EMAIL_FIELD: ", user.EMAIL_FIELD)
            send_mail('Image Processing Web Registration Success', 'You have successfully registered!', 'huy.learns.dl@gmail.com', ['huy3041997@gmail.com'], fail_silently=False)
            print('3')
            messages.success(request, "Registration successful.")
            print('4')
            return redirect("core:homepage")
        messages.error(request, "Unsuccessful registration. Invalid information.")
    form = NewUserForm()
    return render(request=request, template_name="core/register.html", context={"register_form":form})

def login_request(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                print('[+] Login: ')
                login(request, user)
                print('[+] Messages: ')
                messages.success(request, f"You are now logged in as {username}.")
                ## Print messages
                # storage = get_messages(request)
                # for message in storage:
                #     print('[++] message: ', message)
                print('[+] Return: ')
                return redirect("core:homepage")
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")

    form = AuthenticationForm()
    return render(request=request, template_name="core/login.html", context={"login_form":form})

def logout_request(request):
    logout(request)
    messages.info(request, "You have successfully logged out.")
    return redirect("core:homepage")

def update_profile(request):
    args = {}

    if request.method == 'POST':
        print('[+] request.user: ', request.user)
        form = UpdateProfile(request.POST, instance=request.user, user=request.user)
        print('[+] request.user: ', request.user)
        form.actual_user = request.user
        print('[+] request.user: ', request.user)
        print('[+] form: ', form)
        if form.is_valid():
            form.save(1)
            return HttpResponseRedirect(reverse('core:update_profile_success'))
    else:
        form = UpdateProfile(instance=request.user, user=request.user)

    args['form'] = form
    return render(request, 'core/update_profile.html', context={"update_form":form})

# def upload_file(request):
#     if request.method == 'POST':
#         form = UploadFileForm(request.POST, request.FILES)
#         if form.is_valid():
#             handle_uploaded_file(request.FILES['file'])
#             return HttpResponseRedirect('/success/url')
#     else:
#         form = UploadFileForm()
#     return render(request, 'upload.html', {'form': form})
        
# def upload_file(request):
#     if request.method == 'POST':
#         form = ModelFormWithFileField(request.POST, request.FILES)
#         if form.is_valid():
#             form.save()
#             return HttpResponseRedirect('/success/url')
#         else:
#             form = ModelFormWithFileField()
#     return render(request, 'upload.html', {'form': form})

# def upload_file(request):
#     if request.method == 'POST':
#         form = UploadFileForm(request.POST, request.FILES)
#         if form.is_valid():
#             instance = ModelWithFileField(file_field=request.FILES['file'])
#             instance.save()
#             return HttpResponseRedirect('/success/url')
#         else:
#             form = UploadFileForm()
#     return render(request, 'upload.html', {'form': form})


# class FileFieldFormView(FormView):
#     form_class = FileFieldForm
#     template_name = 'upload.html' # Replace with your template
#     success_url = '...' # Replace with your URL or reverse().

#     def post(self, request, *args, **kwargs):
#         form_class = self.get_form_class()
#         form = self.get_form(form_class)
#         files = request.FILES.getlist('file_field')
#         if form.is_valid():
#             for f in files:
#                 ...
#             return self.form_valid(form)
#         else:
#             return self.form_valid(form)

def image_upload_view(request):
    if request.method == 'POST':
        form = ImageForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            # Get the current instance object to display in the template
            img_obj = form.instance
            return render(request, 'core/index.html', {'form': form, 'img_obj': img_obj})

    else:
        form = ImageForm()
    return render(request, 'core/index.html', {'form': form})

@login_required
def post(request):
    ImageFormSet = modelformset_factory(Images,
                                        form=ImageForm,
                                        extra=3)
    print("[###] ImageFormSet, type(ImageFormSet): ", ImageFormSet, type(ImageFormSet))
    
    if request.method == 'POST':
        postForm = PostForm(request.POST)
        formset = ImageFormSet(request.POST, request.FILES,
                  queryset=Images.objects.none())
        for f in formset:
            form = f

        if postForm.is_valid() and formset.is_valid():
            post_form = postForm.save(commit=False)
            post_form.user = request.user
            post_form.save()

            # print('[+] formset: ', dir(formset))
            # print('[+] formset.data: ', formset.data)
            # print('[+] formset.files: ', formset.files)
            # print('[+] formset.cleaned_data: ', formset.cleaned_data)
            # images = formset.save(commit=False)
            # print('[+] images formset.save: ', images)

            # for form in formset.cleaned_data:
            #     print('[+] form: ', form)
            #     image = form['image']
            #     print('[++] image: ', image)
            #     # photo = Images(post=post_form, image=image)
            #     # photo.save()
            #     print('[+] request.FILES: ', request.FILES)
            #     files = request.FILES.getlist('image')
            #     print('[+] files', files)
            #     for f in files:
            #         photo = Images(post=post_form, image=f)
            #         photo.save()

            photos = [] 
            for key in formset.files:
                images = formset.files.getlist(key)
                for img in images:
                    print("[+] type(img)", type(img))
                    photo = Images(post=post_form, image=img)
                    print("[+] type(photo)", type(photo))
                    photos.append(photo)
                    photo.save()
            
            messages.success(request, "Posted!")
            #return HttpResponseRedirect("/")
            return render(request, 'core/index.html',
                        {'postForm': postForm, 'formset': formset, 'img_obj': photos})
        else:
            print(postForm.errors, formset.errors)
    else:
        postForm = PostForm()
        formset = ImageFormSet(queryset=Images.objects.none())

        return render(request, 'core/index.html',
                    {'postForm': postForm, 'formset': formset})

@login_required
def preprocess_image(request):
    if request.method == 'POST':
        postForm = PostForm(request.POST)
        form = ImageForm(request.POST, request.FILES)
        if postForm.is_valid() and form.is_valid():
            post_form = postForm.save(commit=False)
            post_form.user = request.user
            post_form.save()

            form.save(0)
            img_obj = form.instance
            print('[+] img_obj: ', img_obj)
            img_obj.save()
            ori_img = img_obj.image
            new_img = compress(ori_img)
            new_img_obj = Images(post=post_form, image=new_img)
            new_img_obj.save()

            return render(request, 'core/preprocess_image.html', {'postForm': postForm, 'form': form, 'img_obj': new_img_obj})
    else:
        postForm = PostForm(request.POST)
        form = ImageForm()
    return render(request, 'core/preprocess_image.html', {'postForm': postForm, 'form': form})

def convert_image_to_png(request):
    if request.method == 'POST':
        postForm = PostForm(request.POST)
        form = ImageForm(request.POST, request.FILES)
        if postForm.is_valid() and form.is_valid():
            post_form = postForm.save(commit=False)
            post_form.user = request.user
            post_form.save()

            form.save(0)
            img_obj = form.instance
            img_obj.save()
            ori_img = img_obj.image
            new_img = convert_jpg_to_png(ori_img)
            new_img_obj = Images(post=post_form, image=new_img)
            new_img_obj.save(convert=1)

            return render(request, 'core/preprocess_image.html', {'postForm': postForm, 'form': form, 'img_obj': new_img_obj})
    else:
        postForm = PostForm(request.POST)
        form = ImageForm()
    return render(request, 'core/preprocess_image.html', {'postForm': postForm, 'form': form})


def main_view(request):
    # obj = Images.objects.get(pk=244)
    # context = {'obj': obj}
    form = ImageForm(request.POST, request.FILES)
    if form.is_valid():
        form.save()
        return JsonResponse({'message': 'works'})
    context = {'form': form}
    return render(request, 'core/crop_image.html', context)

def trim_image(request):
    if request.method == 'POST':
        postForm = PostForm(request.POST)
        form = ImageTrimForm(request.POST, request.FILES)
        if postForm.is_valid() and form.is_valid():
            post_form = postForm.save(commit=False)
            post_form.user = request.user
            post_form.save()

            form.save(1)
            left = form.cleaned_data['left']
            print('[++] type(left): ', type(left))
            top = form.cleaned_data['top']
            right = form.cleaned_data['right']
            bottom = form.cleaned_data['bottom']
            img_obj = form.instance
            img_obj.save()
            ori_img = img_obj.image
            # new_img = trim(ori_img, 10, 10, 100, 100)
            new_img = trim(ori_img, left, top, right, bottom)
            new_img_obj = Images(post=post_form, image=new_img)
            new_img_obj.save()

            return render(request, 'core/preprocess_image.html', {'postForm': postForm, 'form': form, 'img_obj': new_img_obj})
    else:
        postForm = PostForm(request.POST)
        form = ImageTrimForm()
    return render(request, 'core/preprocess_image.html', {'postForm': postForm, 'form': form})

def frame_image(request):
    if request.method == 'POST':
        postForm = PostForm(request.POST)
        form = ImageFrameForm(request.POST, request.FILES)
        if postForm.is_valid() and form.is_valid():
            post_form = postForm.save(commit=False)
            post_form.user = request.user
            post_form.save()

            form.save(1)
            padding = form.cleaned_data['padding']
            color = form.cleaned_data['color']
            img_obj = form.instance
            img_obj.save()
            ori_img = img_obj.image
            new_img = frame(ori_img, padding, color)
            new_img_obj = Images(post=post_form, image=new_img)
            new_img_obj.save()

            return render(request, 'core/preprocess_image.html', {'postForm': postForm, 'form': form, 'img_obj': new_img_obj})
    else:
        postForm = PostForm(request.POST)
        form = ImageFrameForm()
    return render(request, 'core/preprocess_image.html', {'postForm': postForm, 'form': form})

def remove_background_image(request):
    if request.method == 'POST':
        postForm = PostForm(request.POST)
        form = ImageRemoveBackgroundForm(request.POST, request.FILES)
        if postForm.is_valid() and form.is_valid():
            post_form = postForm.save(commit=False)
            post_form.user = request.user
            post_form.save()

            form.save(1)
            blur = form.cleaned_data['blur']
            canny_thresh_1 = form.cleaned_data['canny_thresh_1']
            canny_thresh_2 = form.cleaned_data['canny_thresh_2']
            mask_dilate_iter = form.cleaned_data['mask_dilate_iter']
            mask_erode_iter = form.cleaned_data['mask_erode_iter']
            mask_color_b = form.cleaned_data['mask_color_b']
            mask_color_g = form.cleaned_data['mask_color_g']
            mask_color_r = form.cleaned_data['mask_color_r']

            img_obj = form.instance
            img_obj.save()
            ori_img = img_obj.image
            new_img = remove_background(ori_img, blur, canny_thresh_1, canny_thresh_2, mask_dilate_iter, mask_erode_iter, (mask_color_b, mask_color_g, mask_color_r))
            new_img_obj = Images(post=post_form, image=new_img)
            new_img_obj.save()

            return render(request, 'core/preprocess_image.html', {'postForm': postForm, 'form': form, 'img_obj': new_img_obj})
    else:
        postForm = PostForm(request.POST)
        form = ImageRemoveBackgroundForm()
    return render(request, 'core/preprocess_image.html', {'postForm': postForm, 'form': form})


# @login_required
# def post(request):
#     ImageFormSet = modelformset_factory(Images,
#                                         form=ImageForm,
#                                         extra=3)
    
#     if request.method == 'POST':
#         postForm = PostForm(request.POST)
#         formset = ImageFormSet(request.POST, request.FILES,
#                   queryset=Images.objects.none())

#         if postForm.is_valid() and formset.is_valid():
#             post_form = postForm.save(commit=False)
#             post_form.user = request.user
#             post_form.save()

#             for form in formset.cleaned_data:
#                 image = form['image']
#                 print('[++] image: ', image)
#                 photo = Images(post=post_form, image=image)
#                 photo.save()
#             messages.success(request, "Posted!")
#             return HttpResponseRedirect("/")
#         else:
#             print(postForm.errors, formset.errors)
#     else:
#         postForm = PostForm()
#         formset = ImageFormSet(queryset=Images.objects.none())
#     return render(request, 'core/index.html',
#                   {'postForm': postForm, 'formset': formset})
