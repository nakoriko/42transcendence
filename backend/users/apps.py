from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'

    # #SAB: codice viene eseguito ad ogni comando manage.py, anche migrazioni
    # def ready(self):
    #     from django.db import connection
    #     from django.db.utils import OperationalError, ProgrammingError

    #     try:
    #         # verifica che la tabella esista già (potrebbe non esistere
    #         # ancora durante il primissimo 'migrate')
    #         with connection.cursor():
    #             pass

    #         from .models import User
    #         User.objects.update(is_online=False)

    #         import redis
    #         r = redis.Redis(host='redis', port=6379)
    #         for key in r.scan_iter('ws_conn_count:*'):
    #             r.delete(key)

    #     except (OperationalError, ProgrammingError):
    #         # il DB non è ancora pronto (es. durante 'manage.py migrate'
    #         # iniziale) — non facciamo nulla, va bene così
    #         pass