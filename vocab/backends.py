from vocab.models import Student

class StudentAuthenticationBackend(object):
	def authenticate(self, username=None, password=None):
		try:
			student = Student.objects.get(username=username)
			if student.check_password(password):
				return student
		except Student.DoesNotExist:
			pass

			return None

	def get_user(self, user_id):
		try:
			return Student.objects.get(pk=user_id)
		except Student.DoesNotExist:
			return None
