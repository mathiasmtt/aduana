from app import get_app, db
from app.models.user import User
from datetime import datetime
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

app = get_app()
with app.app_context():
    print("=== Corrigiendo nombres de usuario ===")
    
    # Mapeo de correcciones (email -> nuevo username)
    corrections = {
        'free@aduana.com': 'free_user',
        'vip@aduana.com': 'vip_user',
        'admin@aduana.com': 'admin'
    }
    
    # Actualizar nombres de usuario
    updated_count = 0
    for email, new_username in corrections.items():
        user = User.query.filter_by(email=email).first()
        
        if not user:
            print(f"❌ Usuario con email {email} no encontrado")
            continue
            
        old_username = user.username
        
        # Verificar si es necesario actualizar
        if old_username == new_username:
            print(f"✓ Usuario {email} ya tiene el nombre correcto: {old_username}")
            continue
            
        # Actualizar nombre de usuario
        print(f"Actualizando usuario {email}: {old_username} -> {new_username}")
        user.username = new_username
        
        # Actualizar también la expiración de sesión para usuarios gratuitos
        if user.role in ['free', 'user']:
            user.update_session_expiry()
            print(f"  Nueva expiración: {user.session_expires_at}")
            
        updated_count += 1
    
    # Guardar cambios
    if updated_count > 0:
        db.session.commit()
        print(f"\n✅ Se actualizaron {updated_count} usuarios")
    else:
        print("\n✓ No fue necesario realizar cambios")
        
    # Verificar estado actual
    print("\nEstado actual de los usuarios:")
    users = User.query.all()
    for user in users:
        print(f"- ID: {user.id}, Username: {user.username}, Email: {user.email}, Rol: {user.role}")
        if user.role in ['free', 'user']:
            print(f"  Expiración: {user.session_expires_at}")
            
    print("\nPara completar la solución:")
    print("1. Reinicia el servidor Flask")
    print("2. Borra las cookies del navegador")
    print("3. Intenta iniciar sesión con el usuario free_user y contraseña freepass123") 