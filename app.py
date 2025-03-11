import enum
from flask import Flask
from flask.views import MethodView
import flask_smorest as smorest
import uuid

from marshmallow import Schema, fields

server = Flask(__name__)

class APIConfig:
    API_TITLE = "TODO API"
    API_VERSION = "v1"
    OPENAPI_VERSION = "3.0.3"
    OPENAPI_URL_PREFIX = '/'
    OPENAPI_SWAGGER_UI_PATH ='/docs'
    OPENAPI_SWAGGER_UI_URL = 'https://cdn.jsdelivr.net/npm/swagger-ui-dist/'
    OPENAPI_REDOC_PATH = '/redoc'
    OPENAPI_REDOC_UI_URL = 'https://cdn.jsdelivr.net/npm/redoc@next/bundles/redoc.standalone/'

server.config.from_object(APIConfig)

api = smorest.Api(server)

todo = smorest.Blueprint('todo', 'todo', url_prefix='/todo', description= 'TODO API')


tasks = [
    {
        'id': uuid.UUID('a92fd2b7-e8d0-4ad5-a607-9719f55612b2'),
        'task': "The first task",
        'completed': False
    },
    {
        'id': uuid.UUID('b65e58cc-4c52-4ac7-8b5a-e901a2421721'),
        'completed': False,
        'task': "The second task"
    }
]

class CreateTask(Schema):
    task = fields.String()

class UpdateTask(CreateTask):
    completed = fields.Bool()

class Task(UpdateTask):
    id = fields.UUID()
    created = fields.DateTime()

class ListTasks(Schema):
    tasks = fields.List(fields.Nested(Task))

class SortByEnum(enum.Enum):
    task = "task"
    created = "created"

class SortByDirectionEnum(enum.Enum):
    asc = 'asc'
    desc = 'desc'

class ListTaskParameters(Schema):
    order_by = fields.Enum(SortByEnum, load_default=SortByEnum.created)
    order = fields.Enum(SortByDirectionEnum, load_default=SortByDirectionEnum.asc)

@todo.route('/tasks')
class TodoCollection(MethodView):
    @todo.arguments(ListTaskParameters, location="query")
    @todo.response(status_code = 200, schema=ListTasks)
    def get(self, parameters):
        data = ListTasks().load({'tasks':tasks})
        pass
        return data

    @todo.arguments(CreateTask)
    @todo.response(status_code= 201, schema=Task)
    def post(self, task):
        print(task)
        task['id'] = uuid.uuid4()
        from datetime import datetime, timezone
        task['created'] = str(datetime.now(timezone.utc))
        task['completed'] = False
        tasks.append(task)
        return  Task().load(task)

@todo.route('/tasks/<string:task_id>')
class TodoById(MethodView):
    def search_task(self, task_id):
        for task in tasks:
            if task['id'] == uuid.UUID(task_id):
                return task
        return None

    @todo.arguments(UpdateTask)
    @todo.response(status_code = 200, schema=Task)
    def patch(self, task_update, task_id):
        to_update_task = self.search_task(task_id)
        if to_update_task:
            to_update_task.update(task_update)
            return to_update_task

        smorest.abort(404, message="Task not found")

    @todo.response(status_code=200, schema=Task)
    def get(self, task_id):
        to_update_task = self.search_task(task_id)
        if to_update_task:
            return to_update_task

        smorest.abort(404, message="Task not found")



api.register_blueprint(todo)


if __name__ == '__main__':
    server.run(host='0.0.0.0', port='8080', debug=True)
