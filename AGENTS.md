# AGENTS.md

Instrucciones para agentes de IA que trabajen en este proyecto. Cumple dos funciones: mantener la documentación (`README.md`) siempre al día, y guiar el desarrollo con buenas prácticas — no solo ejecutar lo que se pide, sino asesorar como lo haría alguien senior del equipo.

---

## Documentación del proyecto (README.md y este archivo)

El **README.md es la documentación única** del proyecto: sirve tanto para humanos como para agentes de IA. Explica qué es el proyecto, cómo está armado y cómo desarrollarlo.

- Al empezar una tarea, leé el README para entender el contexto del proyecto antes de tocar código.
- El README debe estar **muy bien detallado**: cuanto más completo y preciso, mejor fuente de contexto será (aunque el código siempre manda sobre él).
- **Obligación proactiva de edición del README**: cuando un cambio afecte cualquier cosa que documente el README (instalación, scripts, variables de entorno, arquitectura, endpoints, estructura de carpetas, conteo de archivos, permisos, decisiones de diseño, etc.) o detectes cualquier discrepancia con la realidad del código, **actualizá el README.md directamente en esa misma iteración usando tus herramientas de edición, sin esperar a que el usuario te lo pida ni pedirle confirmación previa**. NO alcanza con solo avisarlo o mencionarlo en tu reporte: tu deber es aplicar el cambio en el archivo `README.md`.
- **Checklist obligatorio de cierre de turno**: antes de dar por terminada tu respuesta en cualquier interacción donde se haya tocado, migrado o analizado código, preguntate: *¿Cambiaron archivos, cantidades, tipos, endpoints, rutas o funcionalidades documentadas en el README?* Si la respuesta es sí, **editá el `README.md` de inmediato antes de responder**.
- No agregues al README nada que no puedas verificar en el código.
- El README puede incluir detalles internos del desarrollo sin censurarlos. La única excepción: secretos reales (claves de API, tokens, contraseñas), que nunca se incluyen.
- Evitá afirmaciones perecederas ("en breve", "por ahora", "actualmente") tanto en este archivo como en el README: quedan viejas y dependen de que alguien se acuerde de actualizarlas. Escribí solo lo que siga siendo cierto con el tiempo.
- **Este mismo archivo (`AGENTS.md`) también se mantiene al día**, no solo el README: si durante el trabajo notás que una convención cambió de forma duradera (no una excepción puntual de una sola tarea), actualizalo vos mismo o avisá explícitamente que conviene actualizarlo. Al hacerlo, integrá la regla nueva en la sección temática que corresponda — no la cuelgues suelta al final del archivo, porque así termina siendo una lista desordenada en vez de una guía clara.

## Regla de verificación obligatoria

No des nada por hecho por cómo se ve o se llama algo (una función, una variable, un archivo, un endpoint, un flag de config). Entrá al código, leé la implementación real, y contrastá qué hace de verdad antes de confiar en ello, documentarlo, o explicárselo al usuario.

Ejemplo ilustrativo (no es necesariamente real en este repo): si existe una función `sendNotification()` o un flag `isProduction`, no asumas que la primera manda una notificación de verdad ni que el segundo refleja el ambiente real solo por el nombre — leé el cuerpo y confirmá que hacen lo que dicen (y no, por ejemplo, que solo loguean, que están sin terminar, o que el flag está hardcodeado en `true`).

La fuente de la verdad es **siempre el código**. El README (y este mismo archivo) son solo una vista de él y pueden estar desactualizados: verificá cada dato contra el código antes de confiar en él. Si el README contradice al código, manda el código y corregí el README en la misma iteración para que vuelva a reflejarlo.

## Regla contra la invención de datos

No completes con suposiciones lo que no esté respaldado por el código o por una inferencia razonable y explícita a partir de él. Si no podés determinar algo leyendo el código (por ejemplo, *por qué* se tomó una decisión de diseño puntual, o una regla de negocio que solo vive en la cabeza de alguien del equipo), decilo explícitamente como una zona gris o un supuesto a confirmar — nunca lo presentes como un hecho, ni en el README, ni explicándoselo al usuario.

## Código autoexplicativo (prohibición de comentarios generados por IA)

El código fuente debe ser **autoexplicativo** por su propia claridad, estructura y forma de nombrar variables, constantes y funciones.

- **Prohibido agregar comentarios nuevos**: La IA no debe escribir comentarios explicativos en el código nuevo o modificado (ej. notas que narren qué hace una condición, un mapeo o un hook).
- **Código autoexplicativo**: La legibilidad y el propósito de la lógica deben quedar claros a través de nombres descriptivos e intencionales de variables, constantes y funciones, junto con un diseño de tipos y estructuras riguroso. Si una porción de código parece requerir un comentario para entenderse, la prioridad es refactorizarla para que se explique por sí misma.
- **Preservar comentarios preexistentes**: No borrar ni alterar comentarios ya existentes en los archivos del repositorio (a menos que el usuario lo solicite expresamente), ya que pueden haber sido escritos por personas del equipo y contener contexto valioso.
- **La explicación va al usuario o al README**: Si hay una decisión de diseño, un comportamiento no obvio o una justificación técnica que amerite documentarse, debe comunicarse en la respuesta al usuario o incorporarse al `README.md`, nunca como texto suelto dentro del código fuente.

## Perfil del desarrollador: asesorar, no solo ejecutar

El proyecto lo construye un equipo con experiencia variable según el dominio. Las tareas se hacen en contexto real de producción, lo que exige calidad desde el inicio. Por eso:

- Al introducir un concepto nuevo o tomar una decisión con peso de arquitectura, explicar brevemente el **porqué**: qué problema resuelve, qué patrón clásico de la industria aplica (no reinventar la rueda).
- **Distinguir explícitamente si algo es una decisión propia de este equipo/proyecto, o si viene impuesta desde afuera** (una librería, un framework, un protocolo o estándar, una convención del lenguaje). Evita que el desarrollador piense que todo lo que ve es una elección arbitraria del equipo cuando en realidad viene de afuera, o viceversa.
- Anticipar riesgos típicos de producción en lo que se implemente y avisarlos explícitamente si algo se puede hacer mal sin darse cuenta: seguridad (autenticación, autorización, validación de inputs, secrets), integridad de datos (FKs, constraints, transaccionalidad), costos (servicios con facturación por uso, ancho de banda, almacenamiento) y deuda técnica (acumulación de atajos que complican el futuro).
- Si una decisión actual va a complicar el futuro (modelado flojo, acoplamiento innecesario, dependencias pesadas, etc.), señalarlo en el momento, aunque nadie lo pregunte, y ofrecer la alternativa correcta concretamente.
- No dar nada por sabido: los conceptos del dominio pueden necesitar explicación la primera vez que aparezcan.
- Preferir siempre el camino canónico y simple por encima de soluciones exóticas o prematuramente escaladas.

## Autonomía técnica: programar y ejecutar soluciones ante limitaciones

Siempre que se solicite una acción o tarea para la cual no exista un comando directo, herramienta nativa o función preconstruida en el sistema:

- **Programar la solución por iniciativa propia**: No limitarse a responder con una limitación, imposibilidad o falta de comando nativo. Si es técnicamente viable resolverlo mediante software o automatización, el agente debe idear, escribir y ejecutar su propia solución a medida (creando scripts o utilidades en Python, PowerShell, C# u otra tecnología adecuada).
- **Ejecución y verificación completa**: Desarrollar el código necesario, compilarlo si aplica, ejecutarlo para cumplir la orden y validar el resultado final de punta a punta.
- **Ubicación organizada en `tools/`**: Todo script auxiliar, programa a medida, código fuente compilable o binario (`.cs`, `.exe`, scripts de automatización externos) debe ubicarse de forma ordenada dentro de la carpeta `tools/` (o subcarpetas específicas dentro de ella), **nunca suelto en la raíz del proyecto**. Si el código principal del asistente necesita invocar el ejecutable o script, debe buscarlo dentro del directorio `tools/`.
- **Utilidad real y eliminación de redundancias**: No mantener archivos intermedios o en desuso. Todo archivo que resida en el proyecto o en `tools/` debe tener una función activa y justificada. Si una tarea genera un binario ejecutable que es el único consumido en ejecución, se debe evitar dejar archivos de código intermedios en desuso que confundan o generen redundancia, a menos que exista una necesidad explícita de compilación dinámica.
- **Transparencia y prolijidad**: Explicar con naturalidad y claridad al usuario qué mecanismo se diseñó para resolver el problema, manteniendo el entorno de trabajo limpio y ordenado.

## Limpieza estricta de archivos y recursos temporales

Cualquier recurso, archivo o artefacto transitorio generado para resolver una consulta, análisis, prueba o tarea operativa —incluyendo, pero no limitándose a: capturas de pantalla para inspección visual, scripts efímeros de prueba, volcados de memoria, archivos scratch, imágenes intermedias o registros temporales— debe ser **eliminado de inmediato** una vez cumplido su propósito.

- **Cero basura residual**: Bajo ninguna circunstancia deben quedar archivos transitorios o capturas obsoletas en la carpeta `screenshots/`, en `tools/`, en la raíz del proyecto ni en ubicaciones temporales del sistema una vez finalizada la acción.
- **Ciclo de vida efímero garantizado**: Si un archivo se crea exclusivamente como apoyo transitorio (por ejemplo, para que la IA inspeccione la pantalla, valide una salida o corra un test puntual), su ciclo de vida concluye en la misma iteración: se procesa/analiza y se purga del disco antes de emitir la respuesta final.
- **Diferenciación estricta entre permanente y transitorio**: Solo persisten en el repositorio aquellos archivos de código, utilidades activas en `tools/` o documentación que formen parte deliberada y duradera de la arquitectura del proyecto. Todo lo demás es efímero y se elimina automáticamente sin requerir recordatorio del usuario.


## Portabilidad absoluta y compatibilidad universal (Windows 10 y 11)

El asistente y todas las herramientas complementarias que se desarrollen deben ser **100% portables** y operar de forma transparente en cualquier equipo con Windows 10 o Windows 11 sin requerir modificaciones ni configuraciones manuales:

- **Prohibición estricta de referencias locales**: Queda totalmente prohibido incluir rutas absolutas fijas (como `C:\Users\<usuario>`), nombres de usuario, identificadores de máquina o referencias a dispositivos de hardware específicos.
- **Resolución dinámica de rutas y recursos**: Todas las rutas deben obtenerse de forma relativa o dinámica utilizando `os.path.dirname(os.path.abspath(__file__))`, `os.path.expanduser("~")`, variables de entorno estándar de Windows (`%USERPROFILE%`, `%APPDATA%`, `%TEMP%`) o APIs de Windows (`CSIDL_DESKTOP`, COM Shell, etc.).
- **Diseño agnóstico en `tools/` y scripts auxiliares**: Las utilidades nuevas que se desarrollen deben apoyarse exclusivamente en APIs estándar de Windows, interfaces COM nativas o librerías universales, asegurando que funcionen idénticamente en cualquier instalación limpia de Windows 10 u 11.


