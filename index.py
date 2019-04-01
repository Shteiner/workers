import os.path
import sqlite3
import tornado.ioloop
import tornado.web
from datetime import datetime
from models import Worker


class NoResultError(Exception):
    pass


def maybe_create_tables(conn):
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT COUNT(*) FROM workers LIMIT 1')
        cursor.fetchone()
    except sqlite3.OperationalError:
        with open('schema.sql', encoding='utf8') as f:
            schema = f.read()
        cursor.executescript(schema)
        conn.commit()


class BaseHandler(tornado.web.RequestHandler):
    def row_to_obj(self, row, cur):
        obj = tornado.util.ObjectDict()
        for val, desc in zip(row, cur.description):
            obj[desc[0]] = val
        return obj

    def execute(self, stmt, *args):
        cursor = self.application.conn.cursor()
        cursor.execute(stmt, args)
        self.application.conn.commit()
        if cursor.lastrowid:
            return cursor.lastrowid
        else:
            return

    def query(self, stmt, *args):
        cursor = self.application.conn.cursor()
        cursor.execute(stmt, args)
        return [self.row_to_obj(row, cursor) for row in cursor.fetchall()]

    def queryone(self, stmt, *args):
        results = self.query(stmt, *args)
        if len(results) == 0:
            raise NoResultError()
        elif len(results) > 1:
            raise ValueError('Expected 1 result, got {}'.format(len(results)))
        return results[0]


class ListHandler(BaseHandler):
    def get(self):
        archive = self.get_argument('archive', 0)
        if archive != 0:
            archive = 1
        entries = self.query("""
            SELECT w.*, d.`name` as `department_name`
            FROM `workers` AS w
                INNER JOIN `departments` AS d
            WHERE w.`department_id`=d.`id` AND w.`archive`=? ORDER BY w.`id`;
        """, archive)
        self.render('list.html', entries=[Worker(**entry) for entry in entries], url='/' if archive else '/?archive', archive=archive)


class ViewHandler(BaseHandler):
    def get(self, id):
        entry = self.queryone("""
            SELECT w.*, d.`name` as `department_name`
            FROM `workers` AS w
                INNER JOIN `departments` AS d
            WHERE w.`department_id`=d.`id` AND w.`id`=?;
        """, id)
        if not entry:
            raise tornado.web.HTTPError(404)
        self.render("view.html", entry=Worker(**entry))


class DeleteHandler(BaseHandler):
    def get(self, id):
        entry = self.queryone('SELECT * FROM `workers` WHERE `id`=?;', id)
        if not entry:
            self.redirect('/')
            return
        else:
            self.execute('DELETE FROM `workers` WHERE `id`=?;', id)
            self.application.conn.commit()
            self.redirect('/')
            return


class ArchiveHandler(BaseHandler):
    def get(self, id):
        entry = self.queryone('SELECT * FROM `workers` WHERE `id`=?;', id)
        if not entry:
            self.redirect('/')
            return
        else:
            self.execute('UPDATE `workers` SET `archive`=1 WHERE `id`=?;', int(id))
            self.redirect('/')
            return


class ActiveHandler(BaseHandler):
    def get(self, id):
        entry = self.queryone('SELECT * FROM `workers` WHERE `id`=?;', id)
        if not entry:
            self.redirect('/?archive')
            return
        else:
            self.execute('UPDATE `workers` SET `archive`=0 WHERE `id`=?;', int(id))
            self.redirect('/?archive')
            return


class EditHandler(BaseHandler):
    def get(self, id):
        entry = None
        id = int(id)
        if id:
            entry = self.queryone("""
                SELECT w.*, d.`name` as `department_name`
                FROM `workers` AS w
                    INNER JOIN `departments` AS d
                WHERE w.`department_id`=d.`id` AND w.`id`=?;
            """, id)
            if not entry:
                raise tornado.web.HTTPError(404)
        departments = self.query('SELECT * FROM `departments` ORDER BY `name` ASC;')
        self.render("edit.html",
                    entry=Worker(**entry) if entry else None,
                    test=entry,
                    departments=departments,
                    title='Редактирование сотрудника' if id else 'Добавление сотрудника')

    def post(self, id):
        id = int(id)
        firstname = self.get_argument('firstname')
        middlename = self.get_argument('middlename')
        lastname = self.get_argument('lastname')
        gender = self.get_argument('gender') if self.get_argument('gender') in ['М', 'Ж'] else ''
        department_id = self.get_argument('department_id')
        email = self.get_argument('email')
        birthday = datetime.strptime(self.get_argument('birthday'), '%Y-%m-%d')
        if id:
            try:
                entry = self.queryone("""
                    SELECT w.*, d.`name` as `department_name`
                    FROM `workers` AS w
                        INNER JOIN `departments` AS d
                    WHERE w.`department_id`=d.`id` AND w.`id`=?;
                """, id)
            except NoResultError:
                raise tornado.web.HTTPError(404)
            self.execute("""
                UPDATE `workers`
                SET `firstname`=?, `middlename`=?, `lastname`=?, `gender`=?, `department_id`=?, `email`=?, `birthday`=?
                WHERE `id`=?;""",
                firstname,
                middlename,
                lastname,
                gender,
                department_id,
                email,
                datetime.strftime(birthday, '%d.%m.%Y'),
                int(id))
        else:
            id = self.execute("""
                INSERT INTO `workers` VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, 0);""",
                firstname,
                lastname,
                middlename,
                datetime.strftime(birthday, "%d.%m.%Y"),
                gender,
                department_id,
                email)
        self.redirect('/edit/' + str(id) + '/')


class Application(tornado.web.Application):
    def __init__(self, conn):
        self.conn = conn
        handlers = [
            (r"/", ListHandler),
            (r"/view/([^/]+)/?", ViewHandler),
            (r"/delete/([^/]+)/?", DeleteHandler),
            (r"/edit/([^/]+)/?", EditHandler),
            (r"/add/([^/]+)/?", EditHandler),
            (r"/archive/([^/]+)/?", ArchiveHandler),
            (r"/active/([^/]+)/?", ActiveHandler),
        ]
        settings = dict(
            title='Система учёта персонала',
            template_path=os.path.join(os.path.dirname(__file__), 'templates'),
            static_path=os.path.join(os.path.dirname(__file__), 'static'),
            debug=True,
        )
        super(Application, self).__init__(handlers, **settings)


def make_app():
    conn = sqlite3.connect('database.db')
    maybe_create_tables(conn)
    return Application(conn)


if __name__ == '__main__':
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()