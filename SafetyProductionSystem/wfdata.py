from lbworkflow.core.datahelper import create_user


def load_data():
    init_users()


def init_users():
    users = {
        'admin': create_user('admin', is_superuser=True, is_staff=True),
        'yxfdadmin': create_user('yxfdadmin', is_superuser=True, is_staff=True),
        'nyrdadmin': create_user('nyrdadmin', is_superuser=True, is_staff=True),
        'zzfdadmin': create_user('zzfdadmin', is_superuser=True, is_staff=True),
        'pdrdadmin': create_user('pdrdadmin', is_superuser=True, is_staff=True),
        'pdsfdadmin': create_user('pdsfdadmin', is_superuser=True, is_staff=True),
        'kffdadmin': create_user('kffdadmin', is_superuser=True, is_staff=True),
        'hngsadmin': create_user('hngsadmin', is_superuser=True, is_staff=True),
    }
    return users
