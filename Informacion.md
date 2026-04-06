Sistema de Recomendación de Cine basado en Similitud Semántica (TMDB).




Autores 
- María José Pérez Zamora 
- Josué David Hernández Martínez 





Proyecto de curso
Principios y Tecnologías Inteligencia Artificial
Grupo 01 

Programa de Ingeniería en Sistemas


Abril, 2026  
DECLARACIÓN FIRMADA


“Declaro que he escrito este trabajo de investigación por mí mismo, y que no he utilizado otras fuentes o recursos que los indicados para su preparación. Declaro que he indicado claramente todas las citas directas e indirectas, y que este documento no se ha presentado en otro lugar para fines de examen o publicación".




17/02/2026 Josué Hernández 
…………………………………….


 

18/02/2026 María José Pérez Zamora  
…………………………………….
 
TABLA DE CONTENIDO
Contenido

DECLARACIÓN FIRMADA	2
LISTA DE FIGURAS	4
LISTA DE TABLAS	5
LISTA DE ABREVIATURAS	6
LISTA DE ANEXOS	7
INTRODUCCIÓN	8
TRABAJOS RELACIONADOS	9
DESCRIPCIÓN DEL PROBLEMA	10
JUSTIFICACIÓN	11
ALCANCE Y OBJETIVOS	12
DISEÑO METODOLÓGICO	13
ANÁLISIS DE RESULTADOS	14
CONCLUSIONES	15
BIBLIOGRAFÍA	16














LISTA DE ABREVIATURAS

El uso de terminología técnica especializada requiere una normalización de siglas para facilitar la lectura y comprensión del documento.
•	PTIA: Principios y Tecnologías de Inteligencia Artificial.
•	IA: Inteligencia Artificial.
•	AA: Aprendizaje Automático (Traducción de Machine Learning).
•	SBC: Sistema Basado en el Contenido (Estrategia principal del proyecto).
•	NLP: Procesamiento de Lenguaje Natural (Natural Language Processing).
•	kNN: k-Vecinos más Cercanos (k-Nearest Neighbors).
•	PCA: Análisis de Componentes Principales (Principal Component Analysis).
•	TMDB: La Base de Datos de Películas (The Movie Database).
•	TF-IDF: Frecuencia de Término – Frecuencia Inversa de Documento.
•	CSV: Valores Separados por Comas (Comma-Separated Values).

 
LISTA DE ANEXOS 

Los anexos contienen la documentación técnica y las fuentes de datos que sirven como evidencia y soporte para el desarrollo del sistema.
1.	Anexo A: Dataset de TMDB 5000. Enlace al repositorio oficial de datos utilizado para el entrenamiento del modelo: https://www.kaggle.com/datasets/tmdb/tmdb-movie-metadata







 
INTRODUCCIÓN

En el marco de la asignatura Principios y Tecnologías de Inteligencia Artificial (PTIA), este proyecto busca aplicar modelos avanzados para transformar datos en conocimiento estratégico, permitiendo que los sistemas asistan en procesos de decisión donde la programación tradicional es insuficiente.


Definición de los problemas
Para establecer un punto de partida, se han identificado tres áreas críticas donde el procesamiento inteligente de datos puede mitigar ineficiencias actuales:

¿Cuáles serían tres problemas que les interesaría resolver?

1.	Predicción de Deserción Escolar: La dificultad de las instituciones para cruzar variables académicas y socioeconómicas en tiempo real, lo que impide generar alertas preventivas antes de que el retiro del estudiante sea irreversible.

2.	Clasificación de Quejas y Soporte (NLP): El "cuello de botella" en el triaje manual de mensajes masivos de clientes, provocando que urgencias críticas queden sepultadas bajo consultas generales.

3.	Fatiga de Decisión en Medios: La "parálisis por análisis" del usuario ante catálogos masivos, debido a que los buscadores convencionales no interpretan afinidades semánticas profundas (trama o tono).







La naturaleza de estos retos justifica el uso de arquitecturas de IA por las siguientes razones técnicas:

¿Por qué como proyecto de PTIA?
•	Necesidad de Inferencia: Estos escenarios requieren que el sistema infiera resultados (niveles de riesgo o sentimientos) analizando patrones complejos que no se resuelven con reglas fijas.

•	Gestión de Conocimiento: Cada caso utiliza una base de conocimiento (historiales o metadatos) que la IA estructura para extraer características que un algoritmo simple pasaría por alto.


•	Prototipo Funcional: Permiten desarrollar una Prueba de Concepto tangible que demuestra viabilidad técnica mediante un sistema que recomienda, clasifica o predice de manera adaptativa.











TRABAJOS RELACIONADOS

Para fundamentar la viabilidad del proyecto, se analizan soluciones actuales que emplean arquitecturas de aprendizaje supervisado y redes profundas para la resolución de estos problemas.

¿Cuáles son dos trabajos relacionados a cada problema?

1. Predicción de Deserción Escolar
•	Support Vector Machines (SVM): Utilizadas para realizar una clasificación binaria precisa entre alumnos en riesgo y alumnos estables, encontrando el hiperplano óptimo en un espacio de múltiples variables (notas, faltas, edad).
•	Long Short-Term Memory (LSTM): Aplicadas para analizar el historial académico como una secuencia temporal. Las LSTM permiten detectar tendencias de caída en el rendimiento a través de varios semestres, superando a los modelos estáticos.

2. Clasificador de Quejas (NLP)
•	Arquitectura Transformer: Es el estándar actual en procesamiento de lenguaje. Gracias a su mecanismo de atención, identifica urgencias en los mensajes analizando la relación entre todas las palabras de una queja simultáneamente.
•	Hopfield Neural Network (HNN): Empleada en investigaciones de memoria asociativa para recuperar categorías de quejas similares almacenadas previamente, facilitando la clasificación de casos nuevos por analogía.

3. Recomendador de Películas
•	k-nearest neighbors (kNN): Técnica fundamental del filtrado colaborativo que identifica a los "k" usuarios con gustos más parecidos para sugerir contenidos que estos ya han aprobado, garantizando personalización.
•	Principal Component Analysis (PCA): Utilizado para la reducción de dimensionalidad en grandes bases de datos (como TMDB). El PCA simplifica cientos de géneros y etiquetas en componentes clave, acelerando el cálculo de similitud entre películas.
  
DESCRIPCIÓN DEL PROBLEMA

Una vez analizadas las diversas problemáticas y las tecnologías disponibles, es fundamental establecer un marco de selección que garantice la viabilidad y el rigor académico del proyecto final.


¿Cuáles criterios van a usar para seleccionar el problema a resolver?

Para determinar cuál de los tres retos planteados es el más adecuado para desarrollar durante el semestre, se han definido los siguientes criterios de evaluación:

1.	Disponibilidad y Calidad de la Base de Conocimiento: Se dará prioridad al problema que cuente con un conjunto de datos (dataset) extenso, público y bien estructurado, lo cual es esencial para aplicar algoritmos de Aprendizaje Supervisado y No Supervisado.

2.	Afinidad con el Temario de PTIA: El problema debe permitir la implementación de múltiples arquitecturas vistas en clase, tales como k-nearest neighbors (kNN) para filtrado, Principal Component Analysis (PCA) para reducción de dimensiones o Arquitecturas Transformer para el análisis de texto.

3.	Escalabilidad y Visualización: Se evaluará qué problema permite crear un Prototipo Funcional (MVP) que sea fácil de validar y que demuestre claramente cómo el sistema de IA razona para entregar una solución al usuario.
























¿Cuál es el problema seleccionado?

Tras evaluar las opciones frente a los criterios mencionados, el problema seleccionado es: La fatiga de decisión y la falta de personalización en plataformas de entretenimiento.


Este reto se abordará mediante el desarrollo de un Sistema de Recomendación Inteligente basado en Contenido. Se ha elegido esta problemática por las siguientes razones técnicas:

•	Riqueza de Datos: Permite trabajar con metadatos complejos (tramas, géneros, elencos), lo que facilita el uso de técnicas de Procesamiento de Lenguaje Natural (NLP).

•	Aplicación Multimodelo: Es el escenario perfecto para combinar algoritmos de Aprendizaje No Supervisado (como k-means para agrupar géneros) y Aprendizaje Supervisado (como kNN para encontrar similitudes entre películas).

•	Impacto Directo: Resuelve un problema real de "parálisis por análisis", transformando una búsqueda de palabras clave en un sistema de Razonamiento por Similitud, donde la IA entiende la esencia de lo que el usuario desea ver.
























JUSTIFICACIÓN

El gran problema a resolver es la ineficiencia en la recuperación de información personalizada dentro de entornos de sobreabundancia digital. Actualmente, la mayoría de los sistemas de entretenimiento operan bajo filtros lineales (género, año, popularidad) que no logran capturar la afinidad semántica ni los matices subjetivos de los gustos humanos. Esto genera lo que se conoce como "parálisis por análisis", donde el usuario se siente abrumado por opciones irrelevantes, reduciendo el valor del servicio y el tiempo de consumo efectivo.


Desde la perspectiva de PTIA, el problema es la falta de un modelo de razonamiento que entienda la relación entre el contenido (tramas, temas, tonos) y el perfil del usuario, limitándose a una simple coincidencia de palabras clave en lugar de una comprensión del contexto cinematográfico.

¿Por qué es importante resolverlo?
La resolución de este problema es fundamental por tres razones principales:

1.	Optimización de la Experiencia de Usuario (UX): Al reducir el tiempo de búsqueda y aumentar la precisión de las sugerencias, se mejora la satisfacción del consumidor. Un sistema que "entiende" lo que el usuario quiere antes de que este lo exprese, crea una relación de confianza y fidelidad con la plataforma.

2.	Democratización del Contenido (Long Tail): Resolver este problema permite que películas de alta calidad, pero con menor presupuesto de marketing, salgan a la luz. Al analizar el contenido intrínseco (usando NLP y PCA), la IA puede recomendar "joyas ocultas" que coinciden con los gustos del usuario, fomentando la diversidad cultural en el consumo.

3.	Avance en el Procesamiento de Datos Complejos: Implementar una solución mediante Principios y Tecnologías de IA (como kNN para similitud o Transformers para análisis de tramas) permite demostrar que es posible automatizar el razonamiento humano sobre gustos subjetivos, validando la utilidad de estas arquitecturas en problemas de la vida real.
 
ALCANCE Y OBJETIVOS

Definir el alcance permite concentrar los esfuerzos técnicos en una solución ejecutable, asegurando que los objetivos propuestos sean medibles y alcanzables dentro del marco académico del curso.
¿Cuál es el problema que efectivamente van a resolver?
El proyecto se centrará específicamente en la optimización del descubrimiento de contenido mediante un sistema de recomendación basado en el análisis de metadatos (Content-Based Filtering).
En lugar de intentar resolver la deserción escolar o el triaje de quejas, este sistema resolverá la parálisis por análisis del usuario procesando la "semántica" de las películas (tramas, palabras clave, géneros y elenco) para encontrar similitudes matemáticas profundas entre títulos. Además, el proyecto contará con una base de datos de apoyo para organizar y consultar la información de las películas de manera estructurada.

¿Por qué consideran que es una simplificación adecuada?
Se considera una simplificación adecuada por tres razones técnicas vinculadas al temario de PTIA:
1.	Enfoque en el Ítem, no en el Usuario: Al centrarnos en las características de la película (Contenido), evitamos la complejidad de gestionar millones de perfiles de usuarios reales, permitiendo que el modelo funcione incluso con un solo dato de entrada (la película que le gustó al usuario).
2.	Uso de Datos Estructurados: Utilizar un dataset curado (como TMDB) permite aplicar directamente algoritmos de Aprendizaje Supervisado (kNN) y Reducción de Dimensionalidad (PCA) sin las inconsistencias de datos de encuestas o redes sociales.
3.	Viabilidad Computacional: Procesar una base de conocimiento de ~5,000 registros es suficiente para demostrar el razonamiento por similitud sin requerir una infraestructura de servidores masiva.






Objetivos del Proyecto
Objetivo General
Desarrollar un sistema de inteligencia artificial capaz de generar recomendaciones personalizadas de películas mediante el análisis de la similitud vectorial de sus metadatos, optimizando el proceso de toma de decisiones del usuario.
Objetivos Específicos
•	Cualitativo: Proveer una experiencia de descubrimiento fluida donde las sugerencias mantengan una coherencia temática y emocional con los gustos del usuario, superando la precisión de las búsquedas por palabras clave simples.
•	Cuantitativo: Lograr una precisión en la métrica de Similitud del Coseno superior al 85% en las primeras 5 recomendaciones generadas, y reducir el tiempo de búsqueda manual del usuario mediante un tiempo de respuesta del sistema inferior a 2 segundos.


 
DISEÑO METODOLÓGICO

Este diseño establece la arquitectura lógica para transformar datos crudos en inferencias semánticas, integrando técnicas de Aprendizaje Automático y NLP.
Estrategia General y Justificación
•	Estrategia: Filtrado Basado en Contenido (SBC) mediante Similitud Vectorial.
•	Justificación: A diferencia del filtrado colaborativo, el SBC razona sobre el perfil del ítem (trama, género). Esto permite que la IA genere recomendaciones precisas desde el primer momento, resolviendo el problema del "arranque en frío" sin depender de una masa crítica de usuarios.

Concentración de la Inteligencia
1.	El Conocimiento (Base de Datos): Reside en el dataset de TMDB 5000. Es la "memoria semántica" que contiene los atributos que la IA debe aprender a distinguir.
2.	El Razonamiento (Algoritmo): Se concentra en la Similitud del Coseno. La IA "razona" mediante geometría analítica, midiendo la proximidad de los vectores en un espacio multidimensional. No busca coincidencias exactas de palabras, sino afinidad temática.

Herramientas Seleccionadas y Justificación
•	Lenguaje: Python (Librerías: Pandas, NumPy, Scikit-learn).
•	Justificación: Es el estándar industrial para implementar las arquitecturas del temario (kNN, PCA) con alta eficiencia en el manejo de matrices y cálculos de distancia.






Arquitectura de la Solución
La solución opera en tres capas interconectadas:
•	Capa de Datos: Repositorio estático de TMDB.
•	Capa de Lógica (Middleware): Transformación de texto a vectores y ejecución del motor matemático.
•	Capa de Presentación: Interfaz que recibe la consulta y despliega el ranking de afinidad.

Interfaz de usuario (aplicación web)
La capa de presentación se implementa como una aplicación web con **Streamlit** (`app.py`), conectada al repositorio local (SQLite generado desde los CSV TMDB) y al motor de recomendación en tiempo de ejecución.

Características principales:
•		Consulta por título del catálogo o por fragmento de texto, con actualización explícita de resultados.
•		Visualización del ranking de películas similares con similitud del coseno, nota media TMDB, fecha de estreno, tagline y resumen.
•		Recarga de la base de datos desde los CSV y reconstrucción del modelo desde la barra lateral.
•		Avisos claros cuando no hay coincidencia de título o la consulta está vacía (listado por defecto del catálogo).

Componente Principal: Motor de Vectorización y Similitud
Es el Núcleo Inteligente del proyecto. Su función es realizar la Abstracción del Conocimiento, mapeando características textuales a coordenadas espaciales. Este componente es el responsable de convertir el lenguaje humano en vectores matemáticos comparables, permitiendo que la máquina "entienda" la esencia de una película por encima de su descripción literal.
 
ANÁLISIS DE RESULTADOS

Recomendaciones:
Detallar los resultados
¿Cuáles son los dos mejores casos de prueba? (Secuencia de entradas y salidas esperadas y logradas)
¿Cuál es el caso de prueba más significativo? (Además de la secuencia de entradas y salidas, analicen el resultado)
 
CONCLUSIONES

Recomendaciones:
Presentar una reflexión sobre los resultados y hallazgos de su trabajo.
Lecciones aprendidas
¿Cuáles son los dos aciertos y dos errores más relevantes? [Aprendizaje de cada uno de ellos)
Conclusiones y trabajo futuro
¿Cuáles son las tres conclusiones más evidentes?
¿Cuál es una buena idea de trabajo futuro?

Las conclusiones son una oportunidad para resumir los resultados y hallazgos de una investigación o un proyecto, y para hacer énfasis en la idea o punto principal del escrito al final de su argumento. 
BIBLIOGRAFÍA
-	Banik, R. (2018). Hands-On Recommendation Systems with Python: Start building powerful and personalized recommendation engines with Python. Packt Publishing Ltd.
-	Google. (2024). Gemini: A family of highly capable multimodal models. Google DeepMind. https://blog.google/technology/ai/google-gemini-ai/
-	Manning, C. D., Raghavan, P., y Schütze, H. (2008). Introduction to Information Retrieval. Cambridge University Press.
-	Microsoft. (2024). GitHub Copilot: Your AI pair programmer. https://github.com/features/copilot
-	OpenAI. (2024). ChatGPT: Optimizing Language Models for Dialogue. https://openai.com/chatgpt
-	Russell, S. J., y Norvig, P. (2020). Artificial Intelligence: A Modern Approach (4.ª ed.). Pearson.
-	The Movie Database [TMDB]. (2017). TMDB 5000 Movie Dataset. Kaggle. https://www.kaggle.com/datasets/tmdb/tmdb-movie-metadata

 

