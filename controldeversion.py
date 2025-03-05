#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import subprocess
import sys
from datetime import datetime
from termcolor import colored
import re

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
        # Verificar si hay cambios sin confirmar
        status = self.run_command("git status --porcelain", show_output=False)
        
        if status:
            print(colored(f"\n⚠️ Tienes cambios sin confirmar que impiden cambiar a la rama {branch_name}", "yellow"))
            print(colored("Opciones disponibles:", "yellow"))
            print("1. Hacer commit de los cambios")
            print("2. Hacer stash de los cambios (guardarlos temporalmente)")
            print("3. Descartar los cambios")
            print("4. Cancelar la operación")
            
            option = input(colored("\nSelecciona una opción: ", "cyan"))
            
            if option == "1":
                # Hacer commit de los cambios
                self.add_changes()
                commit_msg = input(colored("Mensaje para el commit: ", "cyan"))
                if not commit_msg:
                    commit_msg = f"Cambios automáticos antes de cambiar a {branch_name}"
                self.commit_changes(commit_msg)
            elif option == "2":
                # Hacer stash de los cambios
                print(colored(f"📦 Guardando cambios en stash...", "blue"))
                stash_msg = f"Cambios automáticos antes de cambiar a {branch_name}"
                self.run_command(f'git stash push -m "{stash_msg}"')
            elif option == "3":
                # Descartar los cambios
                confirmation = input(colored("⚠️ ¿Estás seguro de que quieres DESCARTAR todos los cambios? (s/N): ", "red", attrs=["bold"]))
                if confirmation.lower() == "s":
                    print(colored("🗑️ Descartando cambios...", "red"))
                    self.run_command("git checkout -- .")
                else:
                    print(colored("Operación cancelada", "yellow"))
                    return None
            else:
                print(colored("Operación cancelada", "yellow"))
                return None
        
        # Ahora podemos cambiar de rama
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
    
    def get_last_version(self):
        """Extrae la última versión utilizada en los commits"""
        # Obtener los últimos 20 mensajes de commit para buscar versiones
        result = subprocess.run(
            f"git log --pretty=format:'%s' -n 20",
            shell=True,
            cwd=self.repo_path,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            return None
        
        # Buscar patrones de versión [vX.Y] en los mensajes
        version_pattern = r'\[v(\d{1,2}\.\d{1,2})\]'
        for line in result.stdout.strip().split('\n'):
            match = re.search(version_pattern, line)
            if match:
                return match.group(1)
        
        return None
    
    def restore_to_commit(self, commit_hash):
        """Restaura el repositorio a un commit específico"""
        # Verificar si hay cambios sin confirmar
        status = self.run_command("git status --porcelain", show_output=False)
        
        if status:
            print(colored(f"\n⚠️ Tienes cambios sin confirmar que se perderán al restaurar", "yellow"))
            print(colored("Opciones disponibles:", "yellow"))
            print("1. Hacer commit de los cambios antes de restaurar")
            print("2. Hacer stash de los cambios (guardarlos temporalmente)")
            print("3. Descartar los cambios y restaurar")
            print("4. Cancelar la operación")
            
            option = input(colored("\nSelecciona una opción: ", "cyan"))
            
            if option == "1":
                # Hacer commit de los cambios
                self.add_changes()
                commit_msg = input(colored("Mensaje para el commit: ", "cyan"))
                if not commit_msg:
                    commit_msg = f"Cambios automáticos antes de restaurar al commit {commit_hash}"
                self.commit_changes(commit_msg)
                # Después del commit, podemos continuar con la restauración
            elif option == "2":
                # Hacer stash de los cambios
                print(colored(f"📦 Guardando cambios en stash...", "blue"))
                stash_msg = f"Cambios automáticos antes de restaurar al commit {commit_hash}"
                self.run_command(f'git stash push -m "{stash_msg}"')
                # Mostrar un mensaje informativo sobre cómo recuperar el stash
                print(colored("Para recuperar los cambios guardados después de restaurar, usa:", "cyan"))
                print(colored("git stash apply", "cyan"))
            elif option == "3":
                # Ya está listo para restaurar, continuará con el proceso
                pass
            else:
                print(colored("Operación cancelada", "yellow"))
                return None
        
        print(colored(f"⏪ Restaurando al commit: {commit_hash}", "red", attrs=["bold"]))
        result = self.run_command(f"git reset --hard {commit_hash}")
        
        if result is not None:
            print(colored("\n✅ Restauración completada con éxito", "green"))
            # Obtener información del commit para mostrar detalles
            commit_info = self.run_command(f"git show --pretty=format:'%h - %s (%cr) <%an>' -s {commit_hash}", show_output=False)
            if commit_info:
                print(colored(f"Detalles del commit restaurado:", "blue"))
                print(colored(commit_info, "blue"))
        
        return result
    
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

    def workflow_complete(self):
        """Realiza todo el workflow de git: seleccionar/crear rama, añadir, commit y push"""
        print(colored("\n🚀 WORKFLOW COMPLETO DE GIT", "cyan", attrs=["bold"]))
        
        # 1. Seleccionar o crear rama
        branches = self.get_branches()
        current_branch = next((branch for branch, is_current in branches if is_current), None)
        
        print(colored("\nRamas disponibles:", "green"))
        for i, (branch, is_current) in enumerate(branches, 1):
            if is_current:
                print(colored(f"{i}. * {branch} (actual)", "green", attrs=["bold"]))
            else:
                print(f"{i}.   {branch}")
        
        print(colored("\n¿Qué deseas hacer?", "cyan"))
        print(colored("1: Usar rama actual", "cyan"))
        print(colored("2: Seleccionar otra rama", "cyan"))
        print(colored("3: Crear nueva rama", "cyan"))
        branch_action = input(colored("\nSelecciona una opción: ", "cyan"))
        
        selected_branch = current_branch
        
        # Verificar si hay cambios sin confirmar antes de cambiar de rama
        status = self.run_command("git status --porcelain", show_output=False)
        changes_handled = False
        
        if branch_action in ["2", "3"] and status:
            print(colored(f"\n⚠️ Tienes cambios sin confirmar. ¿Qué deseas hacer con ellos antes de cambiar de rama?", "yellow"))
            print("1. Hacer commit de los cambios")
            print("2. Hacer stash de los cambios (guardarlos temporalmente)")
            print("3. Descartar los cambios")
            
            changes_option = input(colored("\nSelecciona una opción: ", "cyan"))
            
            if changes_option == "1":
                # Hacer commit de los cambios
                self.add_changes()
                commit_msg = input(colored("Mensaje para el commit: ", "cyan"))
                if not commit_msg:
                    commit_msg = "Cambios automáticos antes de cambiar de rama"
                self.commit_changes(commit_msg)
                changes_handled = True
            elif changes_option == "2":
                # Hacer stash de los cambios
                print(colored(f"📦 Guardando cambios en stash...", "blue"))
                stash_msg = "Cambios automáticos antes de cambiar de rama"
                self.run_command(f'git stash push -m "{stash_msg}"')
                changes_handled = True
            elif changes_option == "3":
                # Descartar los cambios
                confirmation = input(colored("⚠️ ¿Estás seguro de que quieres DESCARTAR todos los cambios? (s/N): ", "red", attrs=["bold"]))
                if confirmation.lower() == "s":
                    print(colored("🗑️ Descartando cambios...", "red"))
                    self.run_command("git checkout -- .")
                    changes_handled = True
                else:
                    print(colored("Operación cancelada", "yellow"))
                    return
            else:
                print(colored("Operación cancelada", "yellow"))
                return
        
        # Continuar con la selección o creación de rama
        if branch_action == "2":
            # Seleccionar otra rama
            branch_option = input(colored("Selecciona el número de la rama: ", "cyan"))
            if branch_option and branch_option.isdigit():
                branch_idx = int(branch_option) - 1
                if 0 <= branch_idx < len(branches):
                    selected_branch = branches[branch_idx][0]
                    self.checkout_branch(selected_branch)
                else:
                    print(colored("Número de rama inválido", "red"))
                    return
        elif branch_action == "3":
            # Crear nueva rama
            new_branch = input(colored("Nombre para la nueva rama: ", "cyan"))
            if new_branch:
                self.create_branch(new_branch)
                selected_branch = new_branch
            else:
                print(colored("Nombre de rama inválido", "red"))
                return
        
        # 2. Preguntar si quiere actualizar la rama desde el remoto
        pull_option = input(colored(f"\n¿Deseas actualizar la rama {selected_branch} desde el remoto? (s/N): ", "cyan"))
        if pull_option.lower() == "s":
            self.pull_branch(selected_branch)
        
        # 3. Mostrar estado actual
        self.get_status()
        
        # 4. Añadir cambios si no se hicieron antes
        if not changes_handled:
            add_option = input(colored("\n¿Deseas añadir todos los cambios? (s/N): ", "cyan"))
            if add_option.lower() == "s":
                self.add_changes()
            
            # 5. Realizar commit si no se hizo antes
            commit_option = input(colored("\n¿Deseas realizar un commit? (s/N): ", "cyan"))
            if commit_option.lower() == "s":
                # Sistema de versiones simple
                last_version = self.get_last_version()
                version_prompt = "\nIngresa el número de versión (formato X.Y, ej: 1.1, 3.4)"
                if last_version:
                    version_prompt += f" [última versión: {last_version}]"
                version_prompt += ": "
                version_number = input(colored(version_prompt, "cyan"))
                
                # Validar el formato del número de versión
                if not version_number or not re.match(r'^\d{1,2}\.\d{1,2}$', version_number):
                    print(colored("Formato de versión inválido. Usando formato sin versión.", "yellow"))
                    version_prefix = ""
                else:
                    version_prefix = f"[v{version_number}] "
                
                commit_msg = input(colored("Mensaje para el commit: ", "cyan"))
                full_message = f"{version_prefix}{commit_msg}"
                self.commit_changes(full_message if commit_msg else None)
        
        # 6. Push al remoto
        push_option = input(colored(f"\n¿Deseas subir los cambios a la rama {selected_branch}? (s/N): ", "cyan"))
        if push_option.lower() == "s":
            self.push_changes(selected_branch)
        
        print(colored("\n✅ Workflow completo finalizado", "green", attrs=["bold"]))


def show_menu():
    """Muestra el menú principal con opciones reducidas"""
    print("\n" + "="*70)
    print(colored("🚀 ASISTENTE DE GIT SIMPLIFICADO 🚀".center(70), "cyan", attrs=["bold"]))
    print(colored("Gestiona tu repositorio con menos pasos y más seguridad".center(70), "cyan"))
    print("="*70)
    print(colored("1.", "yellow") + " Ver y seleccionar ramas (gestión básica)")
    print(colored("2.", "yellow") + " Workflow completo " + colored("(recomendado)", "green") + 
          " - Automatiza todo el proceso de Git")
    print(colored("3.", "yellow") + " Restaurar a versión estable " + colored("(recuperación)", "red") + 
          " - Vuelve a un commit anterior")
    print(colored("0.", "red") + " Salir del asistente")
    print("="*70)
    print(colored("NOTA: ", "cyan") + "El workflow completo te guiará por todo el proceso y manejará")
    print(colored("      ", "cyan") + "automáticamente situaciones comunes como cambios sin confirmar.")
    print("="*70)
    return input(colored("Selecciona una opción: ", "green"))


def main():
    print(colored("\n📂 ASISTENTE DE GIT SIMPLIFICADO 📂", "cyan", attrs=["bold"]))
    print(colored("Desarrollado para simplificar el trabajo con Git - Versión 2.0\n", "cyan"))
    
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
            # Workflow completo
            helper.workflow_complete()
        
        elif option == "3":
            # Restaurar a versión estable
            helper.get_commit_history(10)
            commit_hash = input(colored("\nIngresa el hash del commit al que quieres volver: ", "cyan"))
            if commit_hash:
                confirmation = input(colored(f"⚠️ ADVERTENCIA: Esto eliminará todos los cambios posteriores a {commit_hash}. ¿Continuar? (s/N): ", "red", attrs=["bold"]))
                if confirmation.lower() == 's':
                    helper.restore_to_commit(commit_hash)
        
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