from django.contrib.auth import get_user_model

User = get_user_model()

user = User.objects.get(username='danioso8329')
print(f'Usuario: {user.username}')
print(f'Superuser antes: {user.is_superuser}')

user.is_superuser = True
user.save()

print(f'Superuser después: {user.is_superuser}')
print('✅ Usuario danioso8329 ahora es superusuario')
