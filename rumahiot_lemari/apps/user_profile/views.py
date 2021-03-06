from django.shortcuts import render,HttpResponse
import json
from uuid import uuid4
from django.views.decorators.csrf import csrf_exempt
from rumahiot_lemari.apps.user_profile.utils import ResponseGenerator,LemariUtils,RequestUtils
from rumahiot_lemari.apps.sidik_modules.authorization import LemariSidikModule
from rumahiot_lemari.apps.user_profile.dynamodb import LemariDynamoDB
from rumahiot_lemari.apps.user_profile.forms import UpdateProfileForm,UpdateProfilePictureForm
from rumahiot_lemari.apps.user_profile.s3 import S3
from rumahiot_lemari.settings import RUMAHIOT_UPLOAD_BUCKET,RUMAHIOT_REGION

from rumahiot_lemari.apps.sidik_modules.decorator import post_method_required, get_method_required, authentication_required, authentication_required_with_email

# Create your views here.
@get_method_required
@authentication_required_with_email
def user_profile(request, user):

    # Lemari classes
    rg = ResponseGenerator()
    db= LemariDynamoDB()

    try:
        user_profile = db.get_user_profile(user['user_uuid'])
    except:
        # for unknown internal server error
        response_data = rg.error_response_generator(500, "Internal server error")
        return HttpResponse(json.dumps(response_data), content_type="application/json", status=500)
    else:
        # add aditional data
        user_profile['email'] = user['email']
        response_data = rg.data_response_generator(user_profile)
        return HttpResponse(json.dumps(response_data), content_type="application/json", status=200)


@csrf_exempt
@post_method_required
@authentication_required_with_email
def user_profile_update(request, user):

    # Lemari classes
    rg = ResponseGenerator()
    db = LemariDynamoDB()

    form = UpdateProfileForm(request.POST)
    if form.is_valid():
        # Check for string in the number
        if form.cleaned_data['phone_number'].isdigit():
            # check if defined form field is submitted (check only for the field with required = False)
            # use '-' as business logic for None in DynamoDB
            if form.cleaned_data['phone_number'] == '':
                form.cleaned_data['phone_number'] = '-'
            # catch the exception if DynamoDB client got error
            try:
                db.update_user_profile(user['user_uuid'], form.cleaned_data['full_name'],
                                       form.cleaned_data['phone_number'])
            except:
                response_data = rg.error_response_generator(500, "Internal server error")
                return HttpResponse(json.dumps(response_data), content_type="application/json",
                                    status=500)
            else:
                response_data = rg.success_response_generator(200, "Profile successfully updated")
                return HttpResponse(json.dumps(response_data), content_type="application/json",
                                    status=200)
        else:
            response_data = rg.error_response_generator(400, "Phone Number must be number only")
            return HttpResponse(json.dumps(response_data), content_type="application/json", status=400)

    else:
        response_data = rg.error_response_generator(400, "Invalid or missing parameter submitted")
        return HttpResponse(json.dumps(response_data), content_type="application/json", status=400)

@csrf_exempt
@post_method_required
@authentication_required_with_email
def user_profile_image_update(request, user):
    # Lemari classes
    rg = ResponseGenerator()
    auth = LemariSidikModule()
    utils = LemariUtils()
    db = LemariDynamoDB()
    s3 = S3()
    requtils = RequestUtils()

    form = UpdateProfilePictureForm(request.POST, request.FILES)
    if form.is_valid():
        profile_image_file = form.cleaned_data['profile_image']
        file_extension = utils.get_file_type(profile_image_file)
        target_location = 'image/profile/{}/{}{}'.format(user['user_uuid'], uuid4().hex, file_extension)
        try:
            response = s3.put_object(RUMAHIOT_UPLOAD_BUCKET, target_location, profile_image_file.file.getvalue())
        except:
            # catch unknown error
            response_data = rg.error_response_generator(500, "Internal server error")
            return HttpResponse(json.dumps(response_data), content_type="application/json", status=500)
        else:
            file_location = 'https://s3-{}.amazonaws.com/{}/{}'.format(RUMAHIOT_REGION, RUMAHIOT_UPLOAD_BUCKET, target_location)
            try:
                db.update_user_profile_image(user['user_uuid'], file_location)
            except:
                # catch unknown error
                response_data = rg.error_response_generator(500, "Internal server error")
                return HttpResponse(json.dumps(response_data), content_type="application/json",
                                    status=500)
            else:
                response_data = rg.success_response_generator(200, "Profile picture successfully updated")
                return HttpResponse(json.dumps(response_data), content_type="application/json",
                                    status=200)
    else:
        response_data = rg.error_response_generator(400, "Invalid image format")
        return HttpResponse(json.dumps(response_data), content_type="application/json", status=400)









