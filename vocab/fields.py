#TODO: make clearing functionality work
from django.db import models
from vocab.models import *
from django import forms

class CourseManyToManyField(models.ManyToManyField):
	#neuter clearing functionality for now
	def clear(self):
		"""disabled and throws an error because it breaks validation in djangoadmin"""
		raise forms.ValidationError("cannot use clear() on CourseManyToManyField - use remove() instead")
		print "inside clear"
		return
		#for x in self.all():
			#self.remove(x)

