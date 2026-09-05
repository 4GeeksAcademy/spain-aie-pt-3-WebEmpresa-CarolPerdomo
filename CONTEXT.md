# CONTEXT.md — Nexova

## Hito 1: Sitio Web Público de tu Empresa

_These instructions are [available in English](./CONTEXT-nexova.md)._

> Este documento describe tu empresa y la situación concreta para la que estás construyendo este hito. Léelo completo antes de escribir ningún código. Todo lo que construyas debe reflejar este contexto.

---

## Tu empresa

**Nexova** es una consultora de recursos humanos y adquisición de talento fundada en 2011, con sede en Valencia, España, y una oficina de expansión en Miami, Florida. Opera en tres líneas de negocio: headhunting ejecutivo y de mandos medios, outsourcing de equipos de atención al cliente para empresas tecnológicas, y formación corporativa en soft skills y liderazgo. Tiene aproximadamente 120 empleados y genera 8 millones de dólares en facturación anual. Sus clientes son principalmente empresas medianas de tecnología, retail y servicios financieros.

---

## Tu departamento y el problema que debes resolver

Trabajas en el equipo de **Marketing y Comunicaciones**, liderado por Carmen Ruiz. El sitio web corporativo de Nexova fue construido en 2019 y no ha tenido actualizaciones significativas. Es lento, no es accesible, y no refleja el posicionamiento actual de la empresa. Además, no existe un sistema para capturar leads: las personas interesadas en oportunidades laborales o servicios deben enviar un email genérico a <info@nexova.com>. Carmen necesita un sitio web moderno que presente profesionalmente los servicios de Nexova y capture información de candidatos potenciales de forma estructurada.

---

## Tu stakeholder

**Carmen Ruiz**, Head of Marketing

> Hola,
>
> Necesito que construyas nuestro nuevo sitio web corporativo. Debe tener una landing page que presente quiénes somos, qué hacemos, y por qué las empresas nos eligen para gestionar su talento. También necesito una página separada con un formulario para que profesionales interesados en oportunidades laborales puedan registrarse. Actualmente recibimos CVs por email sin ninguna estructura y es un caos. Quiero capturar: datos de contacto, experiencia profesional, sector de interés, nivel de inglés, y disponibilidad. El sitio debe ser responsive, accesible, y estar optimizado para SEO. Usa Tailwind para el diseño y asegúrate de que las validaciones del formulario funcionen correctamente.

---

## Alcance de idioma

- El soporte multiidioma es **opcional pero altamente recomendado** por la operación de Nexova entre España y Miami.
- Debes escoger un **idioma base** para toda la experiencia del sitio y del formulario.
- Si implementas un segundo idioma, trátalo como una mejora (sin reducir la calidad/completitud del idioma base).

## Contenido de la landing page

Tu landing page debe incluir las siguientes secciones, en este orden:

### Header

- Logo o nombre "Nexova"
- Navegación: Inicio | Servicios | Talento | Contacto

### Hero

- **Titular:** "Construimos equipos excepcionales para empresas en crecimiento"
- **Subtítulo:** "Consultora de recursos humanos y adquisición de talento con más de 10 años ayudando a empresas de tecnología, retail y servicios financieros a encontrar y desarrollar el mejor talento."
- **Call to action:** Botón "Únete a nuestro banco de talento" que enlace al formulario

### Servicios (3 columnas)

1. **Headhunting Ejecutivo**
   - Búsqueda y selección de perfiles ejecutivos y mandos medios
   - Proceso personalizado con garantía de reemplazo
2. **Outsourcing de Atención al Cliente**
   - Equipos especializados para empresas tecnológicas
   - Formación continua y supervisión dedicada

3. **Formación Corporativa**
   - Programas de soft skills y liderazgo
   - Cursos presenciales y en línea adaptados a cada organización

### Por qué Nexova (2 columnas)

- **12 años de experiencia** en el mercado latinoamericano
- **Presencia regional:** España y Estados Unidos
- **+500 procesos exitosos** de selección completados
- **Especialización sectorial** en tecnología, retail y finanzas

### Contacto

- Email: <contacto@nexova.com>
- Valencia: +34 960 123 456
- Miami: +1 305 555 0191

### Footer

- © 2025 Nexova. Todos los derechos reservados.
- LinkedIn | Instagram

---

## Campos del formulario de registro de talento

Tu formulario debe capturar la siguiente información:

| Campo                         | Tipo     | Validación                                                       | Obligatorio |
| ----------------------------- | -------- | ---------------------------------------------------------------- | ----------- |
| **Nombre completo**           | text     | Mínimo 2 palabras                                                | Sí          |
| **Email**                     | email    | Formato válido de email                                          | Sí          |
| **Teléfono**                  | tel      | Formato: +[código país] [número] (ej: +34 612 345 678)           | Sí          |
| **País de residencia**        | select   | España / Estados Unidos / Otro                                   | Sí          |
| **Años de experiencia**       | number   | Entre 0 y 50                                                     | Sí          |
| **Sector de interés**         | select   | Tecnología / Retail / Servicios Financieros / Consultoría / Otro | Sí          |
| **Nivel de inglés**           | select   | Básico / Intermedio / Avanzado / Nativo                          | Sí          |
| **Disponibilidad**            | radio    | Inmediata / 1 mes / 2-3 meses / Solo explorando                  | Sí          |
| **LinkedIn (URL del perfil)** | url      | Formato URL válido                                               | No          |
| **Comentarios adicionales**   | textarea | Máximo 500 caracteres                                            | No          |
| **Acepto política de datos**  | checkbox | Debe estar marcado para enviar                                   | Sí          |

---

## Validaciones específicas

1. **Email:** Debe validar que contenga @ y un dominio válido (ej: <usuario@dominio.com>)
2. **Teléfono:** Debe comenzar con + seguido del código de país
3. **Años de experiencia:** No puede ser negativo ni mayor a 50
4. **LinkedIn:** Si se proporciona, debe ser una URL válida (comenzar con http:// o https://)
5. **Comentarios:** Limitar a 500 caracteres con contador visible
6. **Política de datos:** El checkbox debe estar marcado; si no, mostrar error: "Debes aceptar la política de tratamiento de datos para continuar"

---

## Mensajes de error esperados

Cuando un campo no cumpla la validación, muestra estos mensajes específicos:

- **Nombre completo:** "El nombre debe contener al menos nombre y apellido"
- **Email:** "Ingresa un email válido (ejemplo: <nombre@empresa.com>)"
- **Teléfono:** "El teléfono debe incluir código de país (ejemplo: +34 612 345 678)"
- **País:** "Selecciona tu país de residencia"
- **Años de experiencia:** "Los años de experiencia deben estar entre 0 y 50"
- **Sector:** "Selecciona el sector de tu interés"
- **Nivel de inglés:** "Indica tu nivel de inglés"
- **Disponibilidad:** "Selecciona tu disponibilidad"
- **LinkedIn:** "Si incluyes LinkedIn, debe ser una URL válida"
- **Comentarios:** "Los comentarios no pueden exceder 500 caracteres (quedan X)"
- **Política de datos:** "Debes aceptar la política de tratamiento de datos para continuar"

---

## Mensaje de éxito

Cuando el formulario se valide correctamente (simular envío), mostrar:

> **¡Gracias por tu interés en Nexova!**
>
> Hemos recibido tu información. Nuestro equipo de selección la revisará y te contactaremos en caso de que tu perfil encaje con alguna de nuestras oportunidades actuales o futuras.
>
> Mientras tanto, síguenos en LinkedIn para estar al día de nuestras vacantes y contenido sobre desarrollo profesional.

---

## Restricción específica

El formulario está diseñado para **profesionales en búsqueda activa o pasiva de oportunidades laborales**, no para empresas que buscan contratar servicios de Nexova. Si un usuario pregunta sobre contratar servicios de headhunting o formación, el formulario debe incluir un mensaje visible que diga: "¿Eres una empresa buscando talento? Escríbenos a <contacto@nexova.com>"

---

## Schema.org markup requerido

Implementa el siguiente marcado Schema.org en tu landing page:

```json
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "Nexova",
  "description": "Consultora de recursos humanos y adquisición de talento",
  "url": "https://nexova.com",
  "foundingDate": "2011",
  "address": [
    {
      "@type": "PostalAddress",
      "addressCountry": "ES",
      "addressLocality": "Valencia",
      "addressRegion": "Comunidad Valenciana"
    },
    {
      "@type": "PostalAddress",
      "addressCountry": "US",
      "addressLocality": "Miami",
      "addressRegion": "Florida"
    }
  ],
  "contactPoint": {
    "@type": "ContactPoint",
    "telephone": "+34-960-123-456",
    "contactType": "customer service",
    "availableLanguage": ["Spanish", "English"]
  },
  "sameAs": [
    "https://linkedin.com/company/nexova",
    "https://instagram.com/nexova"
  ]
}
```
# CONTEXT — Nexova · Hito 3: Talent Pipeline Tracker

> **Ruta en el repositorio:** `03-talent-pipeline-tracker/CONTEXT-nexova.es.md`

---

## Tu empresa

Eres parte del equipo de Ingeniería de IA de **Nexova**, una consultora de recursos humanos y adquisición de talento con oficinas en Valencia y Miami. El negocio principal de Nexova es exactamente lo que esta herramienta soporta: encontrar a las personas adecuadas. Construir este frontend no es solo un proyecto interno — es una demostración directa de las propias capacidades de Nexova.

---

## El encargo

Elena Vargas, L&D Manager, ha enviado el siguiente correo con copia a Sergio Molina, CTO:

> **Para:** Sergio Molina (CTO)
> **CC:** Equipo de Ingeniería de IA
> **Asunto:** URGENTE — Necesitamos la herramienta de gestión de candidaturas esta semana
>
> Sergio,
>
> Te escribo directamente porque la situación con el proceso de selección del **Asistente de Dirección** se ha vuelto inmanejable. Hemos recibido más de cien candidaturas y mi equipo sigue trabajando desde una hoja de cálculo compartida. Ayer encontramos entradas duplicadas y al menos un candidato cuyo estado no se había actualizado en dos semanas.
>
> Sé que el backend está listo — hablé con Javier y me lo confirmó. Necesito que alguien de tu equipo monte el frontend ahora. No podemos seguir llevando un proceso de selección para nuestra propia empresa en una hoja de cálculo. Es un problema de imagen y nos está costando candidatos.
>
> Lo que necesito que haga la herramienta:
>
> - Mostrar todas las candidaturas en un listado con nombre, puesto, estado y etapa de un vistazo.
> - Filtrar por estado y etapa, y buscar por nombre o email sin recargar la página.
> - Abrir el detalle de un candidato y actualizar su estado o etapa desde ahí.
> - Añadir notas internas después de cada llamada o entrevista, y eliminarlas cuando ya no sean necesarias.
> - Registrar candidatos que llegan por otras vías y corregir datos cuando vienen mal.
>
> Por favor, ponlo como prioridad.
>
> Elena

---

## Contexto del proceso de selección

| Campo          | Valor                                                                                           |
| -------------- | ----------------------------------------------------------------------------------------------- |
| Puesto         | Asistente de Dirección                                                                          |
| Empresa        | Nexova                                                                                          |
| Ubicación      | Sede de Valencia                                                                                |
| Perfil buscado | Experiencia en asistencia ejecutiva, gestión de agenda y viajes, inglés y español profesionales |

---

## API y datos

La API mock está desplegada de forma centralizada y es compartida por todos los contextos del curso. Los campos, valores y estructura son los definidos en la especificación técnica del backend. No es necesario adaptarlos.

### Valores de `status`

| Valor API     | Etiqueta en la UI |
| ------------- | ----------------- |
| `received`    | Recibida          |
| `in_progress` | En proceso        |
| `selected`    | Seleccionada      |
| `discarded`   | Descartada        |

### Valores de `stage`

| Valor API             | Etiqueta en la UI     |
| --------------------- | --------------------- |
| `pending`             | Pendiente de revisión |
| `review`              | En revisión           |
| `personal_interview`  | Entrevista personal   |
| `technical_interview` | Entrevista técnica    |
| `offer_presented`     | Oferta presentada     |

> Los valores crudos de la API (`in_progress`, `personal_interview`, etc.) no deben aparecer nunca en la interfaz. Usa siempre las etiquetas de esta tabla.

---

## Criterios de aceptación específicos

- Los estados y etapas muestran etiquetas legibles, nunca valores de API.
- Las notas internas son visibles únicamente en el detalle del candidato.
- El formulario de registro incluye todos los campos requeridos por la API.

---

