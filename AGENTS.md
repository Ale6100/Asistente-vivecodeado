# AGENTS.md

Instrucciones y convenciones para los agentes de IA que trabajan en este proyecto. Además de ejecutar lo que se les pide, se espera que asesoren: que expliquen el porqué de sus decisiones, adviertan riesgos y propongan mejores alternativas.

---

## Documentación del proyecto (README.md y este archivo)

El **README.md es la documentación única** del proyecto: sirve tanto para humanos como para agentes de IA. Explica qué es el proyecto, cómo está armado y cómo desarrollarlo.

- Al empezar una tarea, leé el README para entender el contexto del proyecto antes de tocar código.
- **Si el README no existe o está vacío**: si el historial de git tiene una versión anterior, partí de ella. Si no, creá una base mínima con lo que se verifica rápido sin recorrer todo el proyecto (cómo instalar y ejecutar, scripts, variables de entorno) y preguntale al programador de qué se trata el proyecto para escribir la introducción. A partir de ahí, completalo de a poco con lo que toquen las tareas, siguiendo las reglas de esta sección. Un README completo desde el principio requiere recorrer todo el proyecto: hacelo solo si el programador te lo pide.
- **Obligación proactiva de edición del README**: cuando un cambio afecte cualquier cosa que el README documente o debería documentar (instalación, scripts, variables de entorno, arquitectura, endpoints, estructura de carpetas, permisos, decisiones de diseño, etc.) o detectes cualquier discrepancia con la realidad del código, **actualizá el README.md en esa misma iteración, sin esperar a que el programador te lo pida ni pedirle confirmación**. No alcanza con mencionarlo en tu respuesta: tenés que editar el archivo.
- **README completo pero conciso, con recorte proactivo**: el README describe qué hace el proyecto, cómo está organizado y el *porqué* de las decisiones, no *cómo* está implementada cada cosa. No van:
  - información repetida en más de un lugar;
  - lo que se deduce leyendo el código en segundos (listados exhaustivos, pasos triviales);
  - explicaciones de herramientas estándar que cualquier programador del stack conoce o puede buscar (cómo usar un gestor de versiones, qué es el hot reload);
  - detalles de implementación: qué función, técnica o método del lenguaje o de una librería se usa internamente para lograr algo, o la cadena de llamadas entre funciones o archivos. Duplican el código y quedan viejos con cualquier cambio interno;
  - detalles anecdóticos que no ayudan a entender ni a desarrollar el proyecto (sonidos, easter eggs, curiosidades).

  **Cada vez que encuentres algo de esto en el README, recortalo vos mismo** (fusionando, resumiendo o quitando), aunque no tenga que ver con la tarea actual y sin esperar a que te lo pidan. Recortá forma, no contenido: no elimines información que no esté en otro lado del README y que no se deduzca fácilmente del código.
- **Única excepción a lo anterior, con umbral alto**: se explica cómo funciona algo internamente solo cuando es tan poco intuitivo que un programador lo usaría mal sin esa explicación (por ejemplo, dos estados globales que deben mantenerse sincronizados de una forma no obvia). Que algo sea complejo o importante no alcanza, y que el README ya explique la implementación de otra parte no justifica agregar más: ante la duda, no va.
- **Partí del README existente**: al actualizarlo, conservá su estructura, su tono y todo el contenido que siga siendo correcto y cumpla estos criterios. Corregí y recortá sobre esa base; no lo reescribas desde cero. Nunca quites por tu cuenta recomendaciones, convenciones o advertencias del equipo (por ejemplo, "correr el build antes de mergear"): si creés que alguna ya no aplica, preguntáselo al programador antes de sacarla.
- **Sistemas externos**: al mencionar APIs, servicios o sistemas que no forman parte de este repositorio, describilos por el uso que les da este proyecto ("se usa para obtener X"), sin dar a entender que eso es todo lo que hacen: de lo que no se ve en este código no sabés nada.
- **Tono neutral sobre el trabajo del equipo**: describí los parches, workarounds y decisiones del equipo como la solución a un problema concreto. En el README evitá redacciones que puedan leerse como que algo del equipo está mal hecho o es un error; si ves un problema real, decíselo al programador en la conversación.
- **Checklist obligatorio de cierre de turno**: antes de terminar cualquier respuesta donde se haya tocado o analizado código, preguntate: *¿Cambiaron archivos, tipos, endpoints, rutas o funcionalidades documentadas, o que deberían documentarse, en el README?* Si la respuesta es sí, **editá el `README.md` de inmediato antes de responder**. Si lo editaste, releé el archivo final completo: que siga cumpliendo el criterio de concisión y que no haya quedado roto (tablas desarmadas, bloques de código sin cerrar, fragmentos sueltos o duplicados).
- Si algo que debería documentarse no se entiende leyendo el código (el propósito de una variable de entorno, el porqué de una decisión), preguntáselo al programador y documentalo con su respuesta.
- El README tiene que leerse como escrito por el equipo: nunca dejes notas sobre lo que falta explicar, lo que no entendiste o lo que te resultó confuso. Esas dudas van en la conversación, no en el archivo.
- El README puede tocar cualquier tema interno del desarrollo sin censurarlo (cuánto detallarlo lo define el punto sobre concisión). La única excepción: secretos reales (claves de API, tokens, contraseñas), que nunca se incluyen.
- Evitá afirmaciones perecederas ("en breve", "por ahora", "actualmente") tanto en este archivo como en el README: quedan viejas y dependen de que alguien se acuerde de actualizarlas. Escribí solo lo que siga siendo cierto con el tiempo.
- **Este mismo archivo (`AGENTS.md`) solo se modifica con aprobación previa del programador**: si notás que una regla de trabajo cambió de forma duradera (no una excepción puntual de una sola tarea), proponé el cambio concreto y aplicalo solo si lo aprueba. Integrá la regla nueva en la sección temática que corresponda, no suelta al final del archivo.
- **`AGENTS.md` tiene que seguir siendo genérico y portable a otros proyectos**: es una guía de proceso y buenas prácticas, no una referencia de este stack o de este repo. Los ejemplos que ilustren una regla tienen que ser inventados (como el de `sendNotification()`/`isProduction` más abajo), nunca una función, archivo o feature real del proyecto. Las convenciones propias del proyecto (stack, patrones elegidos, herramientas) van en el README.

## Regla de verificación obligatoria

No des nada por hecho por cómo se ve o se llama algo (una función, una variable, un archivo, un endpoint, un flag de config). Entrá al código, leé la implementación real, y contrastá qué hace de verdad antes de confiar en ello, documentarlo, o explicárselo al programador.

Ejemplo ilustrativo (no es necesariamente real en este repo): si existe una función `sendNotification()` o un flag `isProduction`, no asumas que la primera manda una notificación de verdad ni que el segundo refleja el ambiente real solo por el nombre — leé el cuerpo y confirmá que hacen lo que dicen (y no, por ejemplo, que solo loguean, que están sin terminar, o que el flag está hardcodeado en `true`).

Esta misma regla aplica a las **versiones de las dependencias**: antes de proponer, escribir o analizar código que use una librería, framework o herramienta, fijate qué versión está realmente declarada o instalada (manifiesto de dependencias, lockfile o su equivalente), no la que asumís por defecto. Tu conocimiento puede fallar en dos direcciones: sugerir una API más nueva que la versión del proyecto, o ignorar cambios posteriores a tu fecha de corte. Ante la duda, si podés buscar en internet, confirmalo ahí.

La fuente de la verdad es **siempre el código (y las versiones que declara)**. El README (y este mismo archivo) son solo una vista de él y pueden estar desactualizados: verificá cada dato contra el código antes de confiar en él. Si el README contradice al código, manda el código y corregí el README en la misma iteración para que vuelva a reflejarlo.

## Regla contra la invención de datos

No completes con suposiciones lo que no esté respaldado por el código o por una inferencia razonable y explícita a partir de él. Si no podés determinar algo leyendo el código (por ejemplo, *por qué* se tomó una decisión de diseño puntual, o una regla de negocio que solo vive en la cabeza de alguien del equipo), preguntáselo al programador — nunca lo presentes como un hecho, ni en el README ni en tus respuestas.

Esto incluye especialmente **siglas y nombres propios** (del proyecto, de organismos, áreas, roles o sistemas): no los expandas ni interpretes su significado si el código no lo dice explícitamente, aunque parezca obvio. Tampoco los renombres ni fusiones: si el proyecto se llama de una forma o trata dos cosas como separadas, respetalo tal cual.

## Git: solo lectura salvo pedido explícito

- **Prohibido ejecutar comandos git que modifiquen el repositorio** (`add`, `commit`, `push`, `pull`, `merge`, `rebase`, `reset`, `checkout`/`restore`, `stash`, crear o borrar ramas y tags, etc.) a menos que el programador lo pida explícitamente en ese momento. Que lo haya pedido antes para otra tarea no vale como permiso para la siguiente.
- Los comandos de solo lectura (`status`, `diff`, `log`, `show`, `blame`, listar ramas) sí se pueden usar libremente.
- Al terminar un cambio, dejalo sin commitear.

## Cambios del programador entre pedidos

- Desde el segundo pedido de la sesión en adelante, antes de empezar revisá si el programador modificó código por su cuenta desde tu respuesta anterior: si el proyecto usa git, mirá `git status`/`git diff` y descontá los cambios que hiciste vos.
- Si esos cambios afectan al README, actualizalo. Si ves problemas en ellos (riesgos, malas prácticas, decisiones que van a complicar el futuro), mencionáselos brevemente. No reescribas su código salvo que te lo pida.

## Estilo del código

- **Consistencia con el proyecto**: el código nuevo o modificado tiene que encajar naturalmente con el resto, como si lo hubiera escrito el mismo equipo. Seguí las convenciones que ya usa el proyecto (nombres, estructura de archivos, patrones, manejo de errores, librerías) en vez de introducir un estilo propio. La excepción son las malas prácticas: si el código existente hace algo mal, no lo imites; hacelo bien y señalá el problema.
- **Código autoexplicativo, comentarios solo como último recurso**: el propósito de la lógica tiene que quedar claro por los nombres de variables, constantes y funciones y por un buen diseño de tipos y estructuras. Si una porción de código parece necesitar un comentario, primero refactorizala para que se explique sola. Solo si eso realmente no alcanza (un algoritmo no trivial, un workaround de un bug externo, una restricción que no se puede expresar en el código), agregá un comentario breve que explique el *porqué*, con el formato estándar del proyecto si existe (JSDoc, docstrings, etc.). Nunca comentes lo que el código ya dice (ej. narrar qué hace una condición, un mapeo o un hook).
- **Preservar comentarios preexistentes**: no borres ni alteres comentarios ya existentes en los archivos del repositorio (a menos que el programador lo pida expresamente), ya que pueden haber sido escritos por personas del equipo y contener contexto valioso.
- **La explicación va al programador o al README**: si hay una decisión de diseño, un comportamiento no obvio o una justificación técnica que amerite documentarse, comunicala en tu respuesta al programador o incorporala al `README.md`, no en comentarios dentro del código (salvo el caso excepcional del punto anterior).

## Asesorar, no solo ejecutar

El proyecto lo construye un equipo con experiencia variable según el dominio. Las tareas se hacen en contexto real de producción, lo que exige calidad desde el inicio. Por eso:

- Al introducir un concepto nuevo o tomar una decisión con peso de arquitectura, explicá brevemente el **porqué**: qué problema resuelve, qué patrón clásico de la industria aplica (no reinventar la rueda).
- **Distinguí explícitamente si algo es una decisión propia de este equipo/proyecto, o si viene impuesta desde afuera** (una librería, un framework, un protocolo o estándar, una convención del lenguaje). Así el programador no confunde una elección arbitraria del equipo con algo que viene de afuera, o viceversa.
- **Antes de programar algo desde cero, fijate si ya está resuelto**: primero, si alguna dependencia ya instalada lo hace o sirve de base; si no, si existe una librería gratuita, madura y mantenida que lo resuelva. Verificá que sea compatible con el stack y las versiones del proyecto (y que su licencia lo permita), y sugerísela al programador con sus pros y contras frente a hacerlo a mano, en vez de instalarla por tu cuenta.
- Anticipá riesgos típicos de producción en lo que implementes y avisalos explícitamente si algo se puede hacer mal sin darse cuenta: seguridad (autenticación, autorización, validación de inputs, secrets), integridad de datos (FKs, constraints, transaccionalidad), costos (servicios con facturación por uso, ancho de banda, almacenamiento) y deuda técnica (acumulación de atajos que complican el futuro).
- Si una decisión actual va a complicar el futuro (modelado flojo, acoplamiento innecesario, dependencias pesadas, etc.), señalalo en el momento, aunque nadie lo pregunte, y ofrecé la alternativa correcta concretamente.
- No des nada por sabido: los conceptos del dominio pueden necesitar explicación la primera vez que aparezcan.
- Preferí siempre el camino canónico y simple por encima de soluciones exóticas o prematuramente escaladas.

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
