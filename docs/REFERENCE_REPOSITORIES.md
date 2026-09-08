# 🔎 Repositorios de referencia y decisiones adoptadas

Esta revisión responde “¿cómo enseñan pagos otros proyectos y qué debe hacer distinto PayLab?”. Las referencias se usan como contraste de producto; no constituyen certificación ni sustituyen documentación oficial.

## Proyectos revisados

### Stripe Samples — Accept a payment

[Repositorio oficial](https://github.com/stripe-samples/accept-a-payment)

El ejemplo separa alternativas de checkout, ofrece varios lenguajes de servidor con un contrato equivalente y documenta credenciales/test mode. La lección adoptada es que **el lenguaje es intercambiable, pero la frontera navegador/backend no**.

PayLab añade algo que el ejemplo deliberadamente no intenta: comparar familias no-Stripe y enseñar ledger, estados desconocidos y conciliación.

### Adyen — Step-by-step integration workshop

[Repositorio oficial](https://github.com/adyen-examples/adyen-step-by-step-integration-workshop)

El workshop declara prerrequisitos, objetivos de aprendizaje, endpoints y webhook antes de pedir cambios de código. La lección adoptada es comenzar cada práctica con **pregunta, resultado esperado y criterio de aprobación**.

PayLab aplica ese patrón en [la ruta de aprendizaje](LEARNING_PATH.md) y en la explicación que aparece después de ejecutar.

### Adyen — Python online payments

[Repositorio oficial](https://github.com/adyen-examples/adyen-python-online-payments)

Este demo muestra checkout local, tarjetas de prueba y configuración explícita de HMAC para webhooks. La lección adoptada es tratar **el webhook como parte del recorrido principal**, no como apéndice.

### Moov PayGate

[Repositorio oficial](https://github.com/moov-io/paygate)

PayGate expone ACH mediante REST para evitar que cada consumidor deba dominar el formato de archivos subyacente. La lección adoptada es separar **API pedagógica común** de los protocolos propios de cada rail.

PayLab no afirma procesar ACH: su adapter transversal es un contrato de aprendizaje y su matriz marca las capacidades externas que aún faltan.

### LangGraph RealWorld

[Repositorio comparado](https://github.com/vladimiracunadev-create/langgraph-realworld)

Su separación visible entre DEMO y LIVE, el diagnóstico previo y la capacidad de funcionar sin credenciales inspiraron la regla de PayLab: **DEMO siempre disponible; SANDBOX/LIVE explícitos; nunca fallback silencioso después de enviar**.

## Matriz comparativa

| Capacidad pedagógica | Stripe Samples | Adyen Workshop | Moov PayGate | LangGraph RealWorld | PayLab |
|---|---:|---:|---:|---:|---:|
| ejecución localhost | sí | sí | sí | sí | sí |
| modo sin credenciales | test limitado | ejercicio/test | servicio local | DEMO | DEMO determinista |
| varios lenguajes | sí | no | Go/API | Python | explicación agnóstica |
| webhook explicado | sí | sí | según rail | eventos del agente | sí |
| fallos inyectables | parcial | ejercicios | operación | degradación | cuatro escenarios |
| ledger y conciliación visibles | no es su foco | no es su foco | infraestructura ACH | no aplica | sí |
| comparación de rails | medios del PSP | medios del PSP | ACH | backends IA | 28 familias |

## Principios de producto resultantes

1. **Objetivo antes del comando.** La primera pantalla explica qué aprender y qué no demuestra.
2. **Una práctica guiada.** Webpay + timeout permite comprender el riesgo de duplicación.
3. **Lenguaje común.** Actor, estado, evidencia, ledger y conciliación se definen junto al resultado.
4. **Contrato estable.** La API local ofrece la misma forma pedagógica para 28 familias.
5. **Límites visibles.** DEMO, SANDBOX y LIVE nunca se mezclan.
6. **Fuentes primarias.** La implementación enlaza proveedor o estándar oficial.
7. **Código y documentación juntos.** Los verificadores fallan si desaparecen guías o marcadores educativos.

## Diferenciador de PayLab

Los repositorios de proveedor enseñan muy bien a consumir **su** API. PayLab enseña a razonar sobre el sistema que rodea cualquier API: resultado incierto, efecto único, evidencia, contabilidad, liquidación y discrepancias. Su valor no está en fingir 28 integraciones productivas, sino en hacer comparable y ejecutable el modelo mental común.
