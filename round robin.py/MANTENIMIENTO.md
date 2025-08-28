# Guía para mantener el repositorio

## 1. Clonar el repositorio

Para trabajar con este repositorio en otra computadora:

```bash
git clone https://github.com/jheymilsonvt/cloud-computing-projects.git
cd cloud-computing-projects
```

## 2. Actualizar cambios locales

Siempre que realices cambios, deberás:

```bash
# Ver qué archivos han cambiado
git status

# Agregar archivos modificados o nuevos
git add .  # O especifica archivos individuales: git add archivo.js

# Hacer commit de los cambios
git commit -m "Descripción breve de los cambios"


# Subir los cambios a GitHub
git push
```

## 3. Actualizar tu copia local

Si has hecho cambios en GitHub o alguien más ha contribuido:

```bash
# Obtener los cambios del repositorio remoto
git pull
```

## 4. Estructura de proyectos

- `/appChat`: Aplicación de chat con Firebase
- `/reposteria rosita`: Sitio web para repostería
- `/round robin.py`: Implementación del algoritmo Round Robin en Python

## 5. Solución de problemas comunes

- Si recibes un error de permisos al hacer push, verifica que estés autenticado correctamente.
- Si hay conflictos al hacer pull, Git te notificará. Deberás resolver los conflictos manualmente.
- Para deshacer el último commit (local): `git reset HEAD~1`

## 6. Buenas prácticas

- Haz commits frecuentes con mensajes descriptivos
- Actualiza el README.md cuando agregues nuevos proyectos
- Mantén el código organizado en directorios separados por proyecto
