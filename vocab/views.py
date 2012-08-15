#TODO: showback function - finish
from vocab.models import *
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext

def get_profile_safe(user):
	try:
		return user.get_profile()
	except StudentProfile.DoesNotExist:
		return None
	
@login_required
def index(request):
	user = request.user
	profile = get_profile_safe(user)
	if not profile:	
		return render_to_response('base.html')

	courses = profile.course_set.all()

	return render_to_response('vocab/index.html', 
								{'username': user.username, 'courses': courses, 
								'profile': profile})

@login_required
def review(request, studyunit_id):
	user = request.user
	profile = get_profile_safe(user)
	if not profile:	
		return render_to_response('base.html')

	print studyunit_id
	studyunit = StudyUnit.objects.get(pk=studyunit_id)
	first_due = profile.get_studyunit_schedulers_due(studyunit)[0]

	return render_to_response('vocab/review.html',
							{'username': user.username, 'first_due': first_due, 
							'studyunit': studyunit}, 
							context_instance=RequestContext(request))

@login_required
def showback(request, studyunit_id):
	user = request.user
	profile = get_profile_safe(user)
	if not profile:	
		return render_to_response('base.html')

	return render_to_response('vocab/review.html',
							{'username': user.username, 'first_due': first_due, 
							'studyunit': studyunit}, 
							context_instance=RequestContext(request))
