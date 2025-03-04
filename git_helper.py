#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import subprocess
import sys
from datetime import datetime
from termcolor import colored

class GitHelper:
    def __init__(self, repo_path=None):
        """Inicializa el ayudante de Git con la ruta del repositorio"""
        self.repo_path = repo_path or os.getcwd()
        # Verifica que sea un repositorio git válido
        if not os.path.exists(os.path.join(self.repo_path, '.git')):
            print(colored(f"ERROR: {self.repo_path} no es un repositorio Git válido", "red", attrs=["bold"]))
            sys.exit(1)
        print(colored(f"✅ Repositorio Git encontrado en: {self.repo_path}", "green"))
    
    def run_command(self, command, show_output=True):
        """Ejecuta un comando de Git y devuelve su salida"""
        try:
            process = subprocess.Popen(
                command,
                cwd=self.repo_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=True,
                text=True
            )
            stdout, stderr = process.communicate()
            
            if process.returncode != 0 and stderr:
                print(colored(f"❌ Error al ejecutar: {command}", "red"))
                print(colored(f"Error: {stderr}", "red"))
                return None
            
            if show_output and stdout:
                print(stdout)
                
            return stdout.strip() if stdout else ""
        except Exception as e:
            print(colored(f"❌ Error al ejecutar el comando: {e}", "red"))
            return None
    
    def get_branches(self):
        """Obtiene la lista de ramas disponibles"""
        branches = self.run_command("git branch", show_output=False)
        if branches:
            # Convertir la salida en una lista de ramas
            branch_list = []
            for branch in branches.split('\n'):
                branch = branch.strip()
                is_current = False
                if branch.startswith('*'):
                    is_current = True
                    branch = branch[1:].strip()
                branch_list.append((branch, is_current))
            return branch_list
        return []
    
    def get_remote_branches(self):
        """Obtiene la lista de ramas remotas"""
        branches = self.run_command("git branch -r", show_output=False)
        if branches:
            # Convertir la salida en una lista de ramas remotas
            branch_list = []
            for branch in branches.split('\n'):
                branch = branch.strip()
                if branch:
                    branch_list.append(branch)
            return branch_list
        return []
    
    def checkout_branch(self, branch_name):
        """Cambia a la rama especificada"""
        print(colored(f"🔄 Cambiando a la rama: {branch_name}", "cyan"))
        return self.run_command(f"git checkout {branch_name}")
    
    def create_branch(self, branch_name):
        """Crea una nueva rama"""
        print(colored(f"🌱 Creando nueva rama: {branch_name}", "green"))
        return self.run_command(f"git checkout -b {branch_name}")
    
    def pull_branch(self, branch_name):
        """Actualiza la rama desde el remoto"""
        print(colored(f"⬇️ Actualizando rama {branch_name} desde el remoto...", "blue"))
        return self.run_command(f"git pull origin {branch_name}")
    
    def add_changes(self):
        """Añade todos los cambios al área de staging"""
        print(colored("➕ Añadiendo todos los cambios...", "yellow"))
        return self.run_command("git add .")
    
    def commit_changes(self, message=None):
        """Realiza un commit con los cambios en staging"""
        if not message:
            date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            message = f"Cambios realizados el {date_str}"
        
        print(colored(f"💾 Realizando commit: {message}", "magenta"))
        return self.run_command(f'git commit -m "{message}"')
    
    def push_changes(self, branch_name):
        """Sube los cambios al remoto"""
        print(colored(f"⬆️ Subiendo cambios a {branch_name}...", "cyan"))
        return self.run_command(f"git push origin {branch_name}")
    
    def get_status(self):
        """Obtiene el estado actual del repositorio"""
        print(colored("📊 Estado actual del repositorio:", "yellow"))
        return self.run_command("git status")
    
    def get_commit_history(self, count=10):
        """Obtiene el historial de commits"""
        print(colored(f"📜 Últimos {count} commits:", "blue"))
        return self.run_command(f"git log --pretty=format:'%h - %s (%cr) <%an>' -n {count}")
    
    def restore_to_commit(self, commit_hash):
        """Restaura el repositorio a un commit específico"""
        print(colored(f"⏪ Restaurando al commit: {commit_hash}", "red", attrs=["bold"]))
        return self.run_command(f"git reset --hard {commit_hash}")
    
    def merge_branches(self, source_branch, target_branch=None):
        """Fusiona una rama en otra"""
        if not target_branch:
            # Si no se especifica la rama objetivo, usar la rama actual
            current_branch = [b for b, is_current in self.get_branches() if is_current]
            if current_branch:
                target_branch = current_branch[0]
            else:
                print(colored("❌ No se pudo determinar la rama actual", "red"))
                return None
        
        print(colored(f"🔄 Fusionando {source_branch} en {target_branch}...", "magenta"))
        self.checkout_branch(target_branch)
        return self.run_command(f"git merge {source_branch}")


def show_menu():
    """Muestra el menú principal"""
    print("\n" + "="*60)
    print(colored("🚀 ASISTENTE DE GIT - SISTEMA DE ARANCELES 🚀".center(60), "cyan", attrs=["bold"]))
    print("="*60)
    print(colored("1.", "yellow") + " Ver ramas disponibles y seleccionar una")
    print(colored("2.", "yellow") + " Crear una nueva rama")
    print(colored("3.", "yellow") + " Actualizar rama actual desde el remoto")
    print(colored("4.", "yellow") + " Ver estado del repositorio")
    print(colored("5.", "yellow") + " Añadir cambios y hacer commit")
    print(colored("6.", "yellow") + " Subir cambios al remoto")
    print(colored("7.", "yellow") + " Ver historial de commits")
    print(colored("8.", "yellow") + " Restaurar a un commit anterior")
    print(colored("9.", "yellow") + " Fusionar ramas")
    print(colored("0.", "red") + " Salir")
    print("="*60)
    return input(colored("Selecciona una opción: ", "green"))


def main():
    print(colored("\n📂 ASISTENTE DE GIT - SISTEMA DE ARANCELES 📂", "cyan", attrs=["bold"]))
    print(colored("Desarrollado para simplificar el trabajo con Git\n", "cyan"))
    
    # Inicializar el ayudante de Git
    helper = GitHelper()
    
    while True:
        option = show_menu()
        
        # Procesar la opción seleccionada
        if option == "1":
            # Ver y seleccionar ramas
            branches = helper.get_branches()
            if branches:
                print(colored("\nRamas disponibles:", "green"))
                for i, (branch, is_current) in enumerate(branches, 1):
                    if is_current:
                        print(colored(f"{i}. * {branch} (actual)", "green", attrs=["bold"]))
                    else:
                        print(f"{i}.   {branch}")
                
                branch_option = input(colored("\nSelecciona el número de la rama (o presiona Enter para cancelar): ", "cyan"))
                if branch_option and branch_option.isdigit():
                    branch_idx = int(branch_option) - 1
                    if 0 <= branch_idx < len(branches):
                        branch_name = branches[branch_idx][0]
                        helper.checkout_branch(branch_name)
            else:
                print(colored("No se encontraron ramas", "red"))
        
        elif option == "2":
            # Crear nueva rama
            branch_name = input(colored("Ingresa el nombre para la nueva rama: ", "cyan"))
            if branch_name:
                helper.create_branch(branch_name)
        
        elif option == "3":
            # Actualizar rama desde el remoto
            branches = helper.get_branches()
            current_branch = next((branch for branch, is_current in branches if is_current), None)
            if current_branch:
                helper.pull_branch(current_branch)
            else:
                print(colored("No se pudo determinar la rama actual", "red"))
        
        elif option == "4":
            # Ver estado
            helper.get_status()
        
        elif option == "5":
            # Añadir y commit
            helper.add_changes()
            commit_msg = input(colored("Mensaje para el commit (Enter para usar mensaje predeterminado): ", "cyan"))
            helper.commit_changes(commit_msg if commit_msg else None)
        
        elif option == "6":
            # Push
            branches = helper.get_branches()
            current_branch = next((branch for branch, is_current in branches if is_current), None)
            if current_branch:
                helper.push_changes(current_branch)
            else:
                print(colored("No se pudo determinar la rama actual", "red"))
        
        elif option == "7":
            # Ver historial
            count = input(colored("¿Cuántos commits quieres ver? (Enter para 10): ", "cyan"))
            try:
                count = int(count) if count else 10
            except ValueError:
                count = 10
            helper.get_commit_history(count)
        
        elif option == "8":
            # Restaurar a commit
            helper.get_commit_history(10)
            commit_hash = input(colored("\nIngresa el hash del commit al que quieres volver: ", "cyan"))
            if commit_hash:
                confirmation = input(colored(f"⚠️ ADVERTENCIA: Esto eliminará todos los cambios posteriores a {commit_hash}. ¿Continuar? (s/N): ", "red", attrs=["bold"]))
                if confirmation.lower() == 's':
                    helper.restore_to_commit(commit_hash)
        
        elif option == "9":
            # Fusionar ramas
            branches = helper.get_branches()
            if branches:
                print(colored("\nRamas disponibles:", "green"))
                for i, (branch, is_current) in enumerate(branches, 1):
                    if is_current:
                        print(colored(f"{i}. * {branch} (actual)", "green", attrs=["bold"]))
                    else:
                        print(f"{i}.   {branch}")
                
                source_option = input(colored("\nSelecciona el número de la rama FUENTE (a fusionar): ", "cyan"))
                if source_option and source_option.isdigit():
                    source_idx = int(source_option) - 1
                    if 0 <= source_idx < len(branches):
                        source_branch = branches[source_idx][0]
                        
                        target_option = input(colored("\nSelecciona el número de la rama DESTINO (Enter para usar la rama actual): ", "cyan"))
                        if target_option and target_option.isdigit():
                            target_idx = int(target_option) - 1
                            if 0 <= target_idx < len(branches):
                                target_branch = branches[target_idx][0]
                                helper.merge_branches(source_branch, target_branch)
                        else:
                            helper.merge_branches(source_branch)
            else:
                print(colored("No se encontraron ramas", "red"))
        
        elif option == "0":
            # Salir
            print(colored("\n¡Hasta luego! 👋", "green", attrs=["bold"]))
            break
        
        else:
            print(colored("Opción no válida. Intenta de nuevo.", "red"))
        
        # Pausa antes de volver al menú
        input(colored("\nPresiona Enter para continuar...", "green"))


if __name__ == "__main__":
    main() 