from django.shortcuts import render
from .models import blogs, tag, taginblog
from django.db import IntegrityError
from django.http import JsonResponse
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from google.oauth2 import id_token
from google.auth.transport import requests
from django.core.exceptions import FieldDoesNotExist
import random,string
import json
import datetime
import ast

# def create_club_member_data(request): can be used to set users from spreadsheet to db
#     a=json.loads(request.body)
#     # print(a)
#     for k in a['user_data']:
#         name=k['name']
#         email=k['email']
#         username=k['email'].split("@")[0]
#         password = ''.join(random.choices(string.ascii_uppercase+string.digits, k = 10)) 
#         print(password)
#         User.objects.create_user(username=username,first_name=name,email=email,password=password)
#     return HttpResponse("added")
def getUser(token):
    try:
        idinfo = id_token.verify_oauth2_token(token, requests.Request(), "450857265760-h4n07vma47ofqrna2ktclm5rvgg3f24l.apps.googleusercontent.com")
        print(idinfo)
        print((idinfo['exp']-idinfo['iat'])/60)
        if idinfo['email_verified'] and idinfo['aud']=="450857265760-h4n07vma47ofqrna2ktclm5rvgg3f24l.apps.googleusercontent.com":
            try:
                user=User.objects.get(email=idinfo['email'])
                return user
            except:
                return -2        #not member of club
        else:
            return -1
    except ValueError:
        return -1


def validate_google_login_token(request):
    a = request.body
    temp = json.loads(a)
    token=temp['token']
    user=getUser(token)
    if user==-1 :
        return HttpResponse("Invalid Access Token Please login",status=401)
    elif user==-2:
        return HttpResponse("Invalid Access Token Please login",status=403 )
    else:
        return HttpResponse(user.email,status=200)

def home(request):
    return HttpResponse("On home page")

def loadBlogs(request):  # this will load all blogs on /blogs path
    blog_obj = blogs.objects.values(
        'heading', 'id', 'sample_text', 'date', 'user_name').order_by('-id')
    data = []
    for k in blog_obj:
        temp = dict()
        print(k)
        temp['blog'] = k
        tag_list = []
        for k in taginblog.objects.filter(blog_id=k['id']):
            tag_list += [tag.objects.get(id=k.tag_id).name]
        temp['tags'] = tag_list
        data += [temp]
    return JsonResponse({'blogs': data})


def loadBlog(request, id):  # loads specific blog with blog id
    try:
        blog = blogs.objects.get(id=id)
    except blogs.DoesNotExist:
        print("no blog")
        return HttpResponse(0)
    print("blog present")
    temp = dict()
    temp['id'] = blog.id
    temp['heading'] = blog.heading
    temp['content'] = blog.content
    temp['sample_text'] = blog.sample_text
    temp['date'] = blog.date
    temp['user_email'] = blog.user_email
    temp['writer'] = blog.user_name
    tag_list = []
    for k in taginblog.objects.filter(blog_id=temp['id']):
        tag_list += [tag.objects.get(id=k.tag_id).name]
    temp['tag_list'] = tag_list
    return JsonResponse(temp)


def postBlog(request):
    a = request.body
    temp = json.loads(a)
    token=temp['token']
    user=getUser(token)
    print(user)
    if user==-1 :
        return HttpResponse("Invalid Login Credentials Please login.Copy The Text Editor Data To Avoid Loss",status=401)
    elif user==-2:
        return HttpResponse("You Are Not Authorized To Write Blogs",status=403 )
    else:
        if temp['blogId']==-1:
            obj = blogs()
            obj.heading = temp['heading']
            obj.user_email = user.email
            obj.user_name = user.first_name
            print(user.first_name)
            obj.content = temp['content']
            obj.date = datetime.date.today()
            obj.sample_text = temp['sample_text']
            obj.save()
            # print(obj)
            for k in temp['tag_list']:
                try:
                    tag_obj = tag.objects.get(name=k)
                except tag.DoesNotExist:
                    tag_obj = tag()
                    tag_obj.name = k
                    tag_obj.save()
                try:
                    taginblog_obj = taginblog()
                    taginblog_obj.blog = obj
                    taginblog_obj.tag = tag_obj
                    taginblog_obj.save()
                except IntegrityError:
                    print("already there")
            return HttpResponse("Blog Published Successfully",status=200)
        else:
            try:
                obj=blogs.objects.get(id=temp['blogId'])
                if obj.user_email!=user.email:
                    return HttpResponse("You Are Not Authorized To Edit This Blog",status=403)
            except blogs.DoesNotExist:
                return HttpResponse("The Blog You Are Trying To Update Does Not Exist",status=401)
            obj.heading = temp['heading']
            obj.content = temp['content']
            obj.date = datetime.date.today()
            obj.sample_text = temp['sample_text']
            obj.save()
            print(temp['tag_list'])
            for k in temp['tag_list']:
                try:
                    tag_obj = tag.objects.get(name=k)
                except tag.DoesNotExist:
                    tag_obj = tag()
                    tag_obj.name = k
                    tag_obj.save()
                try:
                    taginblog_obj = taginblog() #delete the tag which are changed.
                    taginblog_obj.blog = obj
                    taginblog_obj.tag = tag_obj
                    taginblog_obj.save()
                except IntegrityError:
                    print("already there")
            return HttpResponse("Blog Updated Successfully",status=200)

def deleteblog(request):
    temp=json.loads(request.body)
    print(temp)
    user=getUser(temp['token'])
    if user==-1 :
        return HttpResponse("Invalid Login Credentials Please login",status=401)
    elif user==-2:
        return HttpResponse("You Are Not Authorized To Write Blogs",status=403 )
    else:
        try:
            blog=blogs.objects.get(id=temp['blogid'])
        except blogs.DoesNotExist:
            return HttpResponse('Blog Does not exist',status=404)
        if user.email==temp['user_email']:
            if blog.user_email==user.email:
                blogtag=taginblog.objects.filter(blog=blog)
                for k in blogtag:
                    k.delete()
                blog.delete()
                return HttpResponse("Blog deleted successfully",status=200)
            else:
                return HttpResponse("You are not authorized to delete this blogs",status=403 )
        else:
            return HttpResponse("Enter a valid email",status=401 )