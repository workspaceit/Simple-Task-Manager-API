from django.db import connection


def dictfetchall(cursor):
    '''Return all rows from a cursor as a dict'''
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]


def get_permissoins_by_userid_orgid(uid, organization_id):
    with connection.cursor() as cursor:
        query = "Select p.id,p.title from permissions_permissiont as p " \
                "inner join permissions_rolepermission as r_p on p.id = permission_id " \
                "inner join permissions_role as r on r.id=r_p.role_id " \
                "inner join permissions_userrole as u_r on r_p.role_id=u_r.role_id " \
                "inner join user_profiles as u on u.uid=u_r.user_id " \
                "where u.uid = '%s' " \
                "and r.organization_id = '%s' " \
                "and p.status = true " \
                "and r_p.status = true " \
                "and r.status = true " \
                "and u_r.status = true " % (uid, organization_id)
        cursor.execute(query)
        return dictfetchall(cursor)


def is_parmitted_by_permission_title(user, title):
    with connection.cursor() as cursor:
        query = "Select p.id,p.title from permissions_permissiont as p " \
                "inner join permissions_rolepermission as r_p on p.id = permission_id " \
                "inner join permissions_role as r on r.id=r_p.role_id " \
                "inner join permissions_userrole as u_r on r_p.role_id=u_r.role_id " \
                "inner join user_profiles as u on u.uid=u_r.user_id " \
                "where u.uid = '%s' " \
                "and p.status = true " \
                "and p.title = '%s'" \
                "and r_p.status = true " \
                "and r.status = true " \
                "and u_r.status = true " % (user.userprofile.uid, title)
        cursor.execute(query)
        rows = dictfetchall(cursor)
        if len(rows) > 0:
            return True
        else:
            return False


def is_parmitted_by_permission_id(user, id):
    with connection.cursor() as cursor:
        query = "Select p.id,p.title from permissions_permissiont as p " \
                "inner join permissions_rolepermission as r_p on p.id = permission_id " \
                "inner join permissions_role as r on r.id=r_p.role_id " \
                "inner join permissions_userrole as u_r on r_p.role_id=u_r.role_id " \
                "inner join user_profiles as u on u.uid=u_r.user_id " \
                "where u.uid = '%s' " \
                "and p.status = true " \
                "and p.id = '%d'" \
                "and r_p.status = true " \
                "and r.status = true " \
                "and u_r.status = true " % (user.userprofile.uid, id)
        cursor.execute(query)
        rows = dictfetchall(cursor)
        if len(rows) > 0:
            return True
        else:
            return False


def is_user_member_of_organization_and_project_and_permission(organization_id, user, project_id, title):
    with connection.cursor() as cursor:
        query = "Select p.id, p.title from permissions_permissiont as p " \
                "inner join permissions_rolepermission as r_p on p.id = permission_id " \
                "inner join permissions_role as r on r.id=r_p.role_id " \
                "inner join permissions_userrole as u_r on r_p.role_id=u_r.role_id " \
                "inner join user_profiles as u on u.uid=u_r.user_id " \
                "where u.uid = '%s' " \
                "and r.organization_id = '%s' " \
                "and r.project_id= '%s' " \
                "and p.title = '%s'" \
                "and p.status = true " \
                "and r_p.status = true " \
                "and r.status = true " \
                "and u_r.status = true " % (user.uid, organization_id, project_id, title)
        cursor.execute(query)
        rows = dictfetchall(cursor)
        if len(rows) > 0:
            return True
        else:
            return False


def is_user_authorize_for_revoking_permission_from_role(user, organization_id, title):
    with connection.cursor() as cursor:
        query = "Select p.id, p.title from permissions_permissiont as p " \
                "inner join permissions_rolepermission as r_p on p.id = permission_id " \
                "inner join permissions_role as r on r.id=r_p.role_id " \
                "inner join permissions_userrole as u_r on r_p.role_id=u_r.role_id " \
                "inner join user_profiles as u on u.uid=u_r.user_id " \
                "where u.uid = '%s' " \
                "and r.organization_id = '%s' " \
                "and p.title = '%s' " \
                "and p.status = true " \
                "and r_p.status = true " \
                "and r.status = true " \
                "and u_r.status = true " % (user.uid, organization_id, title)
        print(query)
        cursor.execute(query)
        rows = dictfetchall(cursor)
        if len(rows) > 0:
            return True
        else:
            return False


def is_user_authorize_for_assigning_permission_to_role(user, organization_id, title):
    with connection.cursor() as cursor:
        query = "Select p.id, p.title from permissions_permissiont as p " \
                "inner join permissions_rolepermission as r_p on p.id = permission_id " \
                "inner join permissions_role as r on r.id=r_p.role_id " \
                "inner join permissions_userrole as u_r on r_p.role_id=u_r.role_id " \
                "inner join user_profiles as u on u.uid=u_r.user_id " \
                "where u.uid = '%s' " \
                "and r.organization_id = '%s' " \
                "and p.title = '%s' "\
                "and p.status = true " \
                "and r_p.status = true " \
                "and r.status = true " \
                "and u_r.status = true " % (user.uid, organization_id, title)
        print(query)
        cursor.execute(query)
        rows = dictfetchall(cursor)
        if len(rows) > 0:
            return True
        else:
            return False


def get_permissoins_by_user():
    pass
