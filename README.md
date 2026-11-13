# Sitio demostrativo · I.E. 82641 Simón Bolívar (Cajamarca)
Este sitio está marcado como DEMOSTRATIVO y sus datos requieren validación por Dirección.

## Añadir insignia y fotos reales
Copia el archivo original de la insignia a `assets/insignia.png`.
Copia fotografías autorizadas a `assets/` siguiendo la lista en `assets/LEEME.txt`.
Las imágenes aparecerán automáticamente en portada y en la galería interactiva.
No usar fotos identificables de menores sin consentimiento y autorización.

## GitHub Pages: gratis
1. Crea un repositorio (ej.: `web-simon-bolivar`) en GitHub.
2. Sube TODOS los archivos y la carpeta `assets`, conservando su estructura.
3. En el repositorio, ve a `Settings > Pages > Build and deployment`.
4. Selecciona `Deploy from a branch`, rama `main`, carpeta `/ (root)` y guarda.
5. El sitio será accesible mediante `https://TUUSUARIO.github.io/web-simon-bolivar/`.
La publicación en GitHub Pages es pública; obtener autorización antes de difundir.

## Streamlit: vista alternativa
```
pip install -r requirements.txt
streamlit run app.py
```
Necesita Streamlit >= 1.56. `st.iframe` muestra el HTML local con sus archivos.
Para una web institucional definitiva se recomienda GitHub Pages por su navegación HTML directa.

## WhatsApp / chatbot
En `config.js`, añade **solo el número público del colegio** a `whatsappNumber`, por ejemplo
`51XXXXXXXXX` (sin +, espacios ni guiones). Se habilitan el botón y el acceso flotante.
Ese botón ABRE UN CHAT de WhatsApp, no llama por sí solo a la API de n8n.
El chatbot responderá únicamente cuando el mismo número esté enlazado a WAHA,
el flujo n8n esté activo y la sesión funcionando.
No publiques claves API de n8n, WAHA o Gemini en el repositorio ni en JavaScript.
La integración de un chat incrustado en la web requiere un backend HTTPS seguro.

## Facebook
El vínculo está puesto hacia:
https://www.facebook.com/colegiosimonbolivarcajamarca/
Confirma que la página pertenezca al colegio antes de publicarla oficialmente.

## Dominio propio más adelante
NO hay que cambiar el diseño.
1. Dirección registra o administra un dominio institucional, con costo normal anual.
2. GitHub > repositorio > Settings > Pages > Custom domain: añade el dominio.
3. El administrador del dominio ajusta DNS (CNAME para www, A/ALIAS para dominio raíz), siguiendo la documentación oficial.
4. Espera propagación, verifica y habilita HTTPS.
https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/managing-a-custom-domain-for-your-github-pages-site

## Antes de publicar oficialmente
Aprobar logo, fotos, texto, autoridad actual, dirección, horario, teléfono,
matrícula, vacantes, canales, control de accesos y mantenimiento.
