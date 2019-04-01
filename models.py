from datetime import datetime

class Worker:
    def __init__(self, **kwargs):
        self.id = kwargs['id']
        self.firstname = kwargs['firstname']
        self.middlename = kwargs['middlename']
        self.lastname = kwargs['lastname']
        self.gender = kwargs['gender']
        self.birthday = datetime.strptime(kwargs['birthday'], "%d.%m.%Y")
        self.department = kwargs['department_name']
        self.department_id = kwargs['department_id']
        self.email = kwargs['email']
        self.archive = kwargs['archive']

    def get_name(self):
        if self.lastname:
            if self.firstname and self.middlename:
                return '{} {}.{}.'.format(self.lastname, self.firstname[0], self.middlename[0])
            else:
                return str(self.lastname)
        else:
            return str(self.id)

    def get_birthday(self):
        return datetime.strftime(self.birthday, "%d.%m.%Y")

    def get_department(self):
        return self.department

    def get_form_date(self):
        return datetime.strftime(self.birthday, "%Y-%m-%d")

    def get_full_name(self):
        return ' '.join(filter(lambda s: s, [self.lastname, self.firstname, self.middlename]))

    def get_gender(self):
        if self.gender in ['М']:
            return 'Мужской'
        elif self.gender in ['Ж']:
            return 'Женский'

    def get_view_url(self):
        return '/view/{id}/'.format(id=self.id)

    def get_edit_url(self):
        return '/edit/{id}/'.format(id=self.id)

    def get_delete_url(self):
        return '/delete/{id}/'.format(id=self.id)

    def get_archive_url(self):
        if not int(self.archive):
            return '/archive/{id}/'.format(id=self.id)
        else:
            return ''

    def get_active_url(self):
        if int(self.archive):
            return '/active/{id}/'.format(id=self.id)
        else:
            return ''