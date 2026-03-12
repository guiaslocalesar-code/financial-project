---
description: Guardar y subir cambios a GitHub
---

Este flujo de trabajo se encarga de empaquetar todos los cambios realizados durante la conversación y subirlos de forma segura a tu repositorio de GitHub. 
Puedes llamarlo diciendo comandos como: "/workflow github_sync", "Aplica el workflow de GitHub", o "Hace el deployment a git".

Sigue estos exactos pasos:

// turbo-all

1. Revisa el estado de los archivos modificados ejecutando:
   `git status`

2. Agrega todos los cambios al staging area ejecutando:
   `git add .`

3. Analiza los cambios realizados durante la sesión actual y redacta un mensaje de commit claro y conciso en español. Luego ejecuta el commit:
   `git commit -m "feat/fix/docs: [tu mensaje descriptivo]"`

4. Finalmente, sube los cambios al repositorio remoto ejecutando:
   `git push origin master`

5. Notifica al usuario que los cambios han sido subidos con éxito a GitHub y proporciona el mensaje de commit utilizado.
