import re
from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib.auth.models import User, auth
from django.contrib import messages
from .models import FollowUser, PostLike, Profile, Post
from django.contrib.auth.decorators import login_required
from itertools import chain
# Create your views here.
@login_required(login_url='signin')
def index(request):
    user_profile = Profile.objects.get(user=request.user)
    suggested_user = fetch_suggested_user(request.user)
    user_following_list=[]
    feed_list=[]
    followers = FollowUser.objects.filter(follower=request.user.username)
    for i in followers:
        user_following_list.append(i.user)
    print(len(user_following_list))
    for i in user_following_list:
        x=Post.objects.filter(user=i)
        feed_list.append(x)
    feed=list(chain(*feed_list))
    print(type(feed))
    print(type(feed_list))
    return render(request, 'index.html', {'user_profile': user_profile, 'posts': feed, "suggestions_username_profile_list": suggested_user})

def signin(request):

    if request.method == 'POST':
        print(type(request.POST))
        username = request.POST["username"]
        password = request.POST["password"]
        
        user = auth.authenticate(username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return redirect('/')
        else:
            messages.info(request, "Credential invalid")
            return redirect('signin')
    else:
        return render(request, 'signin.html')


def signup(request):

    if request.method=='POST':
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]
        password2 = request.POST["password2"]

        if password==password2:
            if User.objects.filter(email=email).exists():
                messages.info(request, "email already registered")                 
                return redirect('signup')
            elif User.objects.filter(username=username).exists():
                messages.info(request, "Username already exist")
                return redirect('signup')
            else:
                user = User.objects.create_user(username=username, email=email, password=password)
                user.save()
                
                user_login = auth.authenticate(username=username, password=password)
                auth.login(request, user_login)
                #create a profile object for the new user
                user_model = User.objects.get(username=username)
                new_profile = Profile.objects.create(user=user_model, id_user=user_model.id)
                new_profile.save()

                return redirect('settings')
        else:
            messages.info(request, "Password does not match!")
            return redirect('signup')
    else:
        return render(request, 'signup.html')


login_required(login_url='signin')
def logout(request):
    auth.logout(request)
    return redirect('signin')

login_required(login_url='signin')
def settings(request):
    user_profile = Profile.objects.get(user=request.user)
        
    if request.method=="POST":
        if request.FILES.get('image')==None:
            image=user_profile.progileimg
        else:
            image = request.FILES.get('image')
    
        bio = request.POST["bio"]
        location = request.POST["location"]
        user_profile.progileimg = image
        user_profile.bio=bio
        user_profile.location=location
        user_profile.save()
        return redirect('settings')          
        
    return render(request, 'setting.html', {'user_profile': user_profile})

login_required(login_url='signin')
def uploads(request):
        
    if request.method=="POST":
        image = request.FILES.get('image_upload')
        user = request.user.username
        caption = request.POST["caption"]
        new_post = Post.objects.create(user=user, caption=caption, image=image)
        new_post.save()
        return redirect('/')
    return redirect('/')

login_required(login_url='signin')
def likes(request):
    id = request.GET.get("post_id")
    
    post_ = Post.objects.get(id=id)
    
    if PostLike.objects.filter(post_id=id, username=request.user.username).exists():
        post = PostLike.objects.get(post_id=id, username=request.user.username).delete()
        post_.no_of_like-=1
        post_.save()
    else:
        post = PostLike.objects.create(post_id=id, username=request.user.username)
        post.save()
        post_.no_of_like+=1
        post_.save()
    return redirect('/')

login_required(login_url='signin')
def profile(request, pk):
    user_obj = User.objects.get(username=pk)
    user_profile = Profile.objects.get(user = user_obj)
    user_post = Post.objects.filter(user=pk)
    user_post_length = len(user_post)

    follow_status= "follow"
    if FollowUser.objects.filter(user=user_obj.username, follower=request.user.username).exists():
        follow_status = "Unfollow"

    follower_count = FollowUser.objects.filter(user=user_obj).count()
    following_count = FollowUser.objects.filter(follower=user_obj).count()
    context = {
        "user_object": user_obj,
        "user_profile": user_profile,
        "user_posts": user_post,
        "user_post_length": user_post_length,
        "user_followers": follower_count,
        "user_following": following_count,
        "button_text": follow_status,
        "user": request.user
    }

    return render(request, 'profile.html', context)



login_required(login_url='signin')
def follow(request):
    if request.method == "POST":
        followee = request.POST["user"]
        follower = request.user.username
        if FollowUser.objects.filter(user = followee, follower= follower).exists():
            obj = FollowUser.objects.get(user = followee, follower= follower)
            obj.delete()
            
        else:
            obj = FollowUser.objects.create(user = followee, follower= follower)
            obj.save()
        return redirect('/profile/'+request.POST["user"])
    return redirect('/')

        
def fetch_suggested_user(obj):
    all_users = Profile.objects.all()
    all_user=set()
    di={}
    for i in all_users:
        if i.user!=obj:
            all_user.add(i.user.username)
            di[i.user.username]=i
    followed_user=set()
    list_of_users = FollowUser.objects.filter(follower=obj.username)
    for i in list_of_users:
        followed_user.add(i.user)
    rest=all_user-followed_user
    print(all_user)
    print(followed_user)
    print(rest) 
    obj=[]
    for i in rest:
        obj.append(di[i])
    return obj

def search(request):
    find_user = request.POST["username"]
    users= User.objects.filter(username__icontains=find_user)
    user_list=[]
    for i in users:
        user_list.append(Profile.objects.get(user=i))

    return render(request, 'search.html', {"username_profile_list": user_list})