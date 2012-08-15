
#note: the Student class raises an error when you try to modify it through a many
#to many with the Course field

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models.signals import m2m_changed, post_save
from django import forms

#a studyunit is a batch of cards that are meant to be studied together
#an example would be the first 100 words of a vocabulary course
#StudyUnits can be bunched together to create courses
class StudyUnit(models.Model):
	name = models.CharField(max_length=150)
	def num_cards(self):
		return self.card_set.all().count()
	num_cards.short_description = 'Number of cards'

	#add schedulers for all students related to this card
	@staticmethod
	def create_card_scheduler(sender, instance, created, **kwargs):
		for course in instance.studyunit.course_set.all():
			for student in course.students.all():
				print "generating card schedulers for SU"
				student.generate_card_scheduler(instance)

	def __unicode__(self):
		return self.name

#a simple flashcard
class Card(models.Model):
	front = models.TextField()
	back = models.TextField()
	studyunit = models.ForeignKey(StudyUnit)

	def has_studyunit(self, studyunit):
		return self.studyunit == studyunit

	def __unicode__(self):
		return "F:" + self.front[:10] + "|B: " + self.back[:10]

class Student(models.Model):
	user = models.OneToOneField(User)

	def num_courses(self):
		return self.course_set.all().count()
	num_courses.short_description = "Number of courses enrolled in"

	def num_cards_due(self, studyunit):
		return self.get_studyunit_schedulers_due(studyunit).count()

	#gets all Schedulers associated with a given StudyUnit
	def get_studyunit_schedulers(self, studyunit):
		return filter(lambda sch: sch.has_studyunit(studyunit), 
						self.scheduler_set.all())

	#gets all due Schedulers associated with a given StudyUnit that are due
	def get_studyunit_schedulers_due(self, studyunit):
		schedulers = self.get_studyunit_schedulers(studyunit)
		return schedulers.filter(due_date__lte=timezone.now())
	
	def __unicode__(self):
		return self.user.username

	def generate_card_scheduler(self, card):
		sched, created_bool = Scheduler.objects.get_or_create(
			studentprofile=self, card=card, defaults={'notes': ''})

	#creates review units for the course given
	def generate_course_schedulers(self, course):
		for su in course.studyunits.all():
			self.generate_studyunit_schedulers(su)

	#deletes all studyunits passed (must be a list)
	def delete_studyunit_schedulers(self, studyunits):
		for su in studyunits:
			for c in su.card_set.all():
				try:
					Scheduler.objects.get(student=self, card=c).delete()
				except Scheduler.DoesNotExist:
					return

	#helper to add all schedulers of a studyunit from a course
	def generate_studyunit_schedulers(self, studyunit):
		for c in studyunit.card_set.all():
			sched, created_bool = Scheduler.objects.get_or_create(
				student=self, card=c, defaults={'notes': ''})

	@staticmethod
	def create_student_profile(sender, instance, created, **kwargs):
		if created:
			Student.objects.create(user=instance)

	@staticmethod
	def course_student_changed(sender, instance, action, model, reverse, pk_set, **kwargs):
		print action
	#throw an error when this method tries to clear the table
		if action == 'pre_clear' and reverse == False:
			raise forms.ValidationError("cannot use 'clear' method on Course.manytomany")
	@staticmethod 
	def course_studyunit_changed(sender, instance, action, model, reverse, pk_set, **kwargs):
		if action == 'pre_clear' and reverse == False:
			raise forms.ValidationError("cannot use 'clear' method on Course.manytomany")

class Course(models.Model):
	"""#a Course holds all the StudyUnits that should be studied in that course
	all many2many operations are done through extra fields
	#an example of 'Course' would be SAT 2012 June"""
	name = models.CharField(max_length=150)
	studyunits = models.ManyToManyField(StudyUnit, through='CourseStudyUnitTracker')
	students = models.ManyToManyField(Student, through='CourseStudentTracker')

	def num_studyunit_cards(self):
		return reduce(lambda x, y: x+y, [su.card_set.all().count()
						 for su in self.studyunits.all()])
			
	def add_student(self, student):
		CourseStudentTracker.objects.create(student=student, course=self)
		#propagate study units
		student.generate_course_schedulers(self)
		
	def add_studyunit(self, studyunit):
		CourseStudyUnitTracker.objects.create(studyunit=studyunit, course=self)
		#propagate study units
		for s in self.students.all():
			s.generate_studyunit_schedulers(studyunit)
		
	def delete_student(self, student):
		CourseStudentTracker.objects.get(student=student, course=self).delete()
		#delete the student's schedulers for that course
		student.delete_studyunit_schedulers(self.studyunits.all())

	def delete_studyunit(self, studyunit):
		CourseStudyUnitTracker.objects.get(studyunit=studyunit, course=self).delete()
		#delete study units
		for s in self.students.all():
			s.delete_studyunit_schedulers([studyunit])
		
	def __unicode__(self):
		return self.name
	
class CourseStudyUnitTracker(models.Model):
	studyunit = models.ForeignKey(StudyUnit)
	course = models.ForeignKey(Course)
	date_added = models.DateTimeField('Date Added')

	def save(self, *args, **kwargs):
		"""custom save method to autopopulate the due_date and new_card field"""
		if not self.id:
			self.date_added = timezone.now()
		super(CourseStudyUnitTracker, self).save()

	class Meta:
		unique_together = (("studyunit", "course"),)

class CourseStudentTracker(models.Model):
	student = models.ForeignKey(Student)
	course = models.ForeignKey(Course)
	date_added = models.DateTimeField('Date Added')

	def save(self, *args, **kwargs):
		"""custom save method to autopopulate the due_date and new_card field"""
		if not self.id:
			self.date_added = timezone.now()
		super(CourseStudentTracker, self).save()

	class Meta:
		unique_together = (("student", "course"),)

class Scheduler(models.Model):
	"""#each Scheduler is linked to a card in a many to one relationship
	#a Scheduler holds all scheduling information for a card, and any extra notes added
	#think of a Scheduler as a student's marked up version of the platonic Card"""
	notes = models.CharField(max_length=200)
	student = models.ForeignKey(Student)
	card = models.ForeignKey(Card)
	due_date = models.DateTimeField('next review date')
	new_card = models.BooleanField('new card?')

	#returns True iff the scheduler is associated with the studyunit
	def has_studyunit(self, studyunit):
		return self.card.has_studyunit(studyunit)

	#custom save method to autopopulate the due_date and new_card field
	def save(self, *args, **kwargs):
		if not self.id:
			self.due_date = timezone.now()
			self.new_card = True
		super(Scheduler, self).save()

	def __unicode__(self):
		return self.due_date.__str__()

class LoginForm(forms.Form):
	username = forms.CharField(max_length=100)
	password = forms.CharField(widget=forms.PasswordInput(render_value=False), max_length=100)	

#signal connection
m2m_changed.connect(Student.course_studyunit_changed, sender=CourseStudyUnitTracker, dispatch_uid="vocab.studyunit")
m2m_changed.connect(Student.course_student_changed, sender=CourseStudentTracker, dispatch_uid="vocab.student")
post_save.connect(Student.create_student_profile, sender=User)
post_save.connect(StudyUnit.create_card_scheduler, sender=Card)
#TODO: insert signals for the following cases:
#handle all Course business in the course
#course drops a studyunit
#a new card is added
#course deletes a manytomany relation

