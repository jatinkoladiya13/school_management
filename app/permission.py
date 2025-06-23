from rest_framework.permissions import BasePermission

class Custompermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        print(f"User: {user}")
        print(f"User Permissions: {user.permission}")
        
        has_create_permission = False
        has_update_permission = False
        has_view_permission = False 
        has_delete_permission = False

        permission = user.permission
        
        if request.method == 'POST' and permission.create == 'true':
            has_create_permission = True
        if request.method == 'PUT' and permission.update == 'true':
            has_update_permission = permission.update
        if request.method == 'GET' and permission.view == 'true':
            has_view_permission = True
        if request.method == 'DELETE' and permission.delete_permission == 'true':
            has_delete_permission = True
                
        print(f"Method: {request.method}")
        print(f"Create Permission: {has_create_permission}")
        print(f"Update Permission: {has_update_permission}")
        print(f"View Permission: {has_view_permission}")
        print(f"Delete Permission: {has_delete_permission}")

        if request.method == 'POST':
            return has_create_permission
        if request.method == 'PUT':
            return has_update_permission
        if request.method == 'GET':
            return has_view_permission
        if request.method == 'DELETE':
            return has_delete_permission        

                        
        return False
    

class CustomPermissionAdmin(BasePermission):

    def has_permission(self, request, view):
        user = request.user
        
        if str(user.rolle) =="admin":
            return True

        return False