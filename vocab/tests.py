"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from vocab.models import *
from django.contrib.auth.models import User
from django import forms
from django.db import IntegrityError

class VocabTestCase(TestCase):
	def setUp(self):
		self.user = User.objects.create(username="yourmom", password="yourdad")
		self.sp = self.user.get_profile()

	def assertZero(self, expr):
		self.assertEqual(expr, 0)

	def assertSchedulerNum(self, course, student):
		self.assertEqual(course.num_studyunit_cards(),
				 student.scheduler_set.all().count())
		
class StudentTest(VocabTestCase):
	fixtures = ['studentprofile.json']

	def testProfileCreated(self):
		"""test saving a user"""
		self.assertNotIsInstance(Student.objects.get(user=self.user), 
							Student.DoesNotExist)

		u1 = User(username="mom", password="yourd")
		u1.save()
		sp1 = Student.objects.get(user=u1)
		self.assertEqual(sp1.user, u1)

	def testCourseAddAndRemove(self):
		self.assertEqual(self.sp.num_courses(), 0)
		co = Course.objects.create(name="bullshit")
		studenttracker = CourseStudentTracker.objects.create(course=co, student=self.sp)
		self.assertEqual(self.sp.num_courses(), 1)
		studenttracker.delete()
		self.assertEqual(self.sp.num_courses(), 0)

class SchedulerPropagationTest(VocabTestCase):
	fixtures = ['studentprofile.json']

class CourseTest(TestCase):
	"""tests basic Course functionality"""
	def testCreate(self):
		name = "Gay couRse"
		course = Course.objects.create(name=name)
		self.assertNotIsInstance(Course.objects.get(name=name), Course.DoesNotExist)
		self.assertEqual(name, course.name)
		self.assertEqual(course.students.all().count(), 0)
		self.assertEqual(course.studyunits.all().count(), 0)

#tests the Course model, along with its m2m_changed signals
class CourseManyToManyTest(VocabTestCase):
	fixtures = ['m2mtest.json']

	def setUp(self):
		self.course = Course.objects.create(name="Course2")
		self.studyunit1 = StudyUnit.objects.all()[0]
		self.studyunit2 = StudyUnit.objects.all()[1]
		super(CourseManyToManyTest, self).setUp()
				
	def testStudyUnitsAddDelete(self):
		"""make sure adding and removing StudyUnits work.
		Also ensure that the clear() method cannot be used"""

		#make sure that there are no studyunits or students yet
		self.assertEqual(self.course.studyunits.all().count(), 0)
		self.assertEqual(self.course.students.all().count(), 0)

		self.course.add_studyunit(self.studyunit1)
		self.assertEqual(self.course.studyunits.all().count(), 1)

		#can't add duplicate studyunit
		with self.assertRaises(forms.ValidationError):
			self.course.studyunits.clear()

		#no schedulers should propagate at this point
		self.assertZero(Scheduler.objects.all().count())
		
		self.assertEqual(self.course.studyunits.all().count(), 1)
		self.course.add_student(self.sp)
		self.assertEqual(self.course.students.all().count(), 1)
		#make sure can't add a duplicate student
		with self.assertRaises(IntegrityError):
			self.course.add_student(self.sp)
		with self.assertRaises(forms.ValidationError):
			self.course.students.clear()

		self.course.delete_student(self.sp)
		self.assertZero(self.course.students.all().count())

	def testStudyUnitPropagationDeletion(self):
		"""Make sure that Schedulers are added when Students change the courses
		they have"""
		self.assertEqual(self.course.studyunits.all().count(), 0)
		self.assertEqual(self.course.students.all().count(), 0)

		self.course.add_studyunit(self.studyunit1)
		self.assertZero(Scheduler.objects.all().count())
		
		#make sure that the Schedulers happen when a student is added
		self.course.add_student(self.sp)
		self.assertSchedulerNum(self.course, self.sp)
		
		#now add a StudyUnit
		self.course.add_studyunit(self.studyunit2)
		self.assertSchedulerNum(self.course, self.sp)

		#make sure adding duplicates doesn't break stuff	
		with self.assertRaises(IntegrityError):
			self.course.add_studyunit(self.studyunit2)

		#check deletions
		self.course.delete_studyunit(self.studyunit2)
		self.assertSchedulerNum(self.course, self.sp)

		self.course.delete_student(self.sp)
		self.assertZero(self.sp.scheduler_set.all().count())
