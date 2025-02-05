# catalogo-lml

# Catálogo de Enlaces

Una aplicación web que permite a los usuarios gestionar un catálogo de enlaces organizados por categorías. Desarrollada con FastAPI en el backend y React en el frontend.

## Tabla de Contenidos

- [Características](#características)
- [Tecnologías Utilizadas](#tecnologías-utilizadas)
- [Instalación](#instalación)
- [Uso](#uso)
- [API](#api)
- [Contribución](#contribución)
- [Licencia](#licencia)

## Características

- Gestión de categorías y enlaces.
- Autenticación de usuarios con un superadministrador por defecto.
- Interfaz de usuario intuitiva construida con React.
- API RESTful desarrollada con FastAPI.
- Almacenamiento de datos utilizando MongoDB.

## Tecnologías Utilizadas

- **Frontend**: React
- **Backend**: FastAPI
- **Base de Datos**: MongoDB
- **Otros**: Motor (para MongoDB), Uvicorn, Pydantic, Passlib, Python-dotenv

## Instalación

Sigue estos pasos para instalar y ejecutar la aplicación localmente:


**Instala las dependencias del backend**:
pip install -r requirements.txt


**Instala las dependencias del frontend**:
npm install

**Configura las variables de entorno**:
Crea un archivo `.env` en la raíz del directorio del backend y agrega tus credenciales:

**Ejecuta la aplicación**:

- Para el backend:

  ```
  uvicorn main:app --host='0.0.0.0' --port=8000 --reload
  ```

- Para el frontend:

  ```
  npm start
  ```

## Uso

1. Abre tu navegador y ve a `http://localhost:3000` para acceder a la interfaz de usuario.
2. Puedes registrarte como superadministrador utilizando las credenciales configuradas en el archivo `.env`.
3. Una vez autenticado, podrás crear, leer, actualizar y eliminar categorías y enlaces.

## API

### Endpoints Principales

- **POST /login**: Autenticación de usuarios.
- **POST /superadmin/**: Crear un superadministrador.
- **GET /categorias/**: Obtener todas las categorías.
- **POST /categorias/**: Crear una nueva categoría.
- **PUT /categorias/{categoria_id}**: Actualizar una categoría existente.
- **GET /enlaces/**: Obtener todos los enlaces.
- **POST /enlaces/**: Crear un nuevo enlace.
- **PUT /enlaces/{enlace_id}**: Actualizar un enlace existente.
- **GET /enlaces/por-categoria/{categoria_id}**: Obtener enlaces filtrados por categoría.

### Ejemplo de Uso de la API

1. **Login**:
 - Endpoint: `POST /login`
 - Body:
   ```
   {
       "username": "admin",
       "password": "tu_contraseña_superadmin"
   }
   ```

2. **Crear Categoría**:
 - Endpoint: `POST /categorias/`
 - Body:
   ```
   {
       "nombre": "Nueva Categoría"
   }
   ```

3. **Crear Enlace**:
 - Endpoint: `POST /enlaces/`
 - Body:
   ```
   {
       "titulo": "Título del Enlace",
       "url": "http://ejemplo.com",
       "descripcion": "Descripción del enlace",
       "categoria_id": "ID_DE_LA_CATEGORIA"
   }
   ```
