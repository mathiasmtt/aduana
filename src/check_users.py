from app import get_app
from app.models.user import User

app = get_app()
with app.app_context():
    print('Usuarios en la base de datos:')
    users = User.query.all()
    for u in users:
        print(f'- Username: {u.username}, Email: {u.email}, Rol: {u.role}, Hash: {u.password_hash[:20]}...') 