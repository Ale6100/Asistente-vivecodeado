# AGENTS.md

Instrucciones para agentes de IA que trabajen en este proyecto. Cumple dos funciones: mantener la documentación (`README.md`) siempre al día, y guiar el desarrollo con buenas prácticas — no solo ejecutar lo que se pide, sino asesorar como lo haría alguien senior del equipo.

---

## Documentación del proyecto (README.md y este archivo)

El **README.md es la documentación única** del proyecto: sirve tanto para humanos como para agentes de IA. Explica qué es el proyecto, cómo está armado y cómo desarrollarlo.

- Al empezar una tarea, leé el README para entender el contexto del proyecto antes de tocar código.
- El README debe estar **muy bien detallado en cobertura, no en narración de implementación**: cuanto más completo y preciso sea describiendo qué existe, qué patrón se usa y el *porqué* de una decisión, mejor fuente de contexto será (ejemplo ilustrativo, no necesariamente real en este repo: "las preferencias del usuario se guardan en un storage accesible también desde el backend, en vez de uno exclusivo del cliente, para que el backend no dependa de que el cliente se las envíe" alcanza y sobra) — aunque el código siempre manda sobre él. No es lugar para trazar la cadena de llamadas entre funciones/archivos (ej. enumerar que tal setter llama a tal función de refresco, que tal archivo le pasa tal prop a tal otro, en qué orden se ejecuta cada cosa). Ese nivel de detalle duplica lo que ya cuenta el código, queda desactualizado en cuanto cambia un detalle interno de la implementación (no el contrato/patrón), y agrega carga de mantenimiento sin aportar contexto nuevo. Si al escribir una sección notás que estás describiendo un flujo de llamadas entre piezas internas en vez de un concepto, contrato o decisión, es señal de resumir a una o dos oraciones o de sacarlo directamente del README.
- **Obligación proactiva de edición del README**: cuando un cambio afecte cualquier cosa que documente el README (instalación, scripts, variables de entorno, arquitectura, endpoints, estructura de carpetas, conteo de archivos, permisos, decisiones de diseño, etc.) o detectes cualquier discrepancia con la realidad del código, **actualizá el README.md directamente en esa misma iteración usando tus herramientas de edición, sin esperar a que el usuario te lo pida ni pedirle confirmación previa**. NO alcanza con solo avisarlo o mencionarlo en tu reporte: tu deber es aplicar el cambio en el archivo `README.md`.
- **Checklist obligatorio de cierre de turno**: antes de dar por terminada tu respuesta en cualquier interacción donde se haya tocado, migrado o analizado código, preguntate: *¿Cambiaron archivos, cantidades, tipos, endpoints, rutas o funcionalidades documentadas en el README?* Si la respuesta es sí, **editá el `README.md` de inmediato antes de responder**.
- No agregues al README nada que no puedas verificar en el código.
- El README puede incluir detalles internos del desarrollo sin censurarlos: ningún tema es tabú por sí solo (esto es sobre *qué* temas se pueden tocar, no sobre *cuánto* detallarlos — para eso ver el punto sobre nivel de detalle, más arriba). La única excepción real: secretos (claves de API, tokens, contraseñas), que nunca se incluyen.
- Evitá afirmaciones perecederas ("en breve", "por ahora", "actualmente") tanto en este archivo como en el README: quedan viejas y dependen de que alguien se acuerde de actualizarlas. Escribí solo lo que siga siendo cierto con el tiempo.
- **Este mismo archivo (`AGENTS.md`) también se mantiene al día**, no solo el README: si durante el trabajo notás que una convención cambió de forma duradera (no una excepción puntual de una sola tarea), actualizalo vos mismo o avisá explícitamente que conviene actualizarlo. Al hacerlo, integrá la regla nueva en la sección temática que corresponda — no la cuelgues suelta al final del archivo, porque así termina siendo una lista desordenada en vez de una guía clara.
- **`AGENTS.md` tiene que seguir siendo genérico y portable a otros proyectos**: es una guía de proceso y buenas prácticas, no una referencia de este stack o de este repo en particular. Cualquier ejemplo que agregues acá para ilustrar una regla tiene que ser sintético/inventado (como el de `sendNotification()`/`isProduction` de la regla de verificación más abajo), nunca una función, archivo o feature real de este proyecto. Si necesitás ilustrar una regla con algo concreto de este repo, esa mención va en el README o en la respuesta al usuario — no en `AGENTS.md`.

## Regla de verificación obligatoria

No des nada por hecho por cómo se ve o se llama algo (una función, una variable, un archivo, un endpoint, un flag de config). Entrá al código, leé la implementación real, y contrastá qué hace de verdad antes de confiar en ello, documentarlo, o explicárselo al usuario.

Ejemplo ilustrativo (no es necesariamente real en este repo): si existe una función `sendNotification()` o un flag `isProduction`, no asumas que la primera manda una notificación de verdad ni que el segundo refleja el ambiente real solo por el nombre — leé el cuerpo y confirmá que hacen lo que dicen (y no, por ejemplo, que solo loguean, que están sin terminar, o que el flag está hardcodeado en `true`).

Esta misma regla aplica a las **versiones de las dependencias**: antes de proponer, escribir o analizar código que use una librería, framework o herramienta del proyecto, fijate qué versión está realmente declarada/instalada (manifiesto de dependencias, lockfile, o el equivalente del ecosistema que corresponda) — no la que tu conocimiento interno asume por defecto. Un conocimiento genérico de una herramienta falla en dos direcciones posibles: sugerir una API o un patrón de una versión más nueva que la que el proyecto tiene fijada (rompe compatibilidad), o asumir que el proyecto usa la versión vieja/clásica que más conocés cuando en realidad usa una más nueva (perdiéndote features o cambios de esa versión que tu conocimiento no tiene por su fecha de corte). Si tenés dudas sobre cómo se comporta específicamente la versión real que usa el proyecto y contás con capacidad de búsqueda en internet, usala para confirmarlo en vez de asumir.

La fuente de la verdad es **siempre el código (y las versiones que declara)**. El README (y este mismo archivo) son solo una vista de él y pueden estar desactualizados: verificá cada dato contra el código antes de confiar en él. Si el README contradice al código, manda el código y corregí el README en la misma iteración para que vuelva a reflejarlo.

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
