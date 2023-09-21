# TFM-RehabilitationSystem
Trabajo de Fin de Máster del Máster "Nuevas Tecnologías Electrónicas y Fotónicas" de la UCM. Se trata de una aplicación web que monitoriza movimientos físicos de pacientes en rehabilitación y sube los datos a una base de datos en la nube para posterior evaluación del personal médico de forma remota

1. Incluir en config.json las credenciales del usuario de la base de datos de MongoDB.
2. La base de datos se llamó "Rehabilitación. Las colecciones de la base de datos son:
   · "médicos", donde se almacenan los datos de los médicos, incluidas sus credenciales de acceso a la aplicación.
   · "pacientes", lo mismo para los pacientes.
   · "ejercicios", donde se almacenan los ejercicios propuestos por el médico, los cuales puede añadir desde la aplicación.
   · "registros", donde se almacenan los datos de los entrenamientos ya realizados por los pacientes. Cada documento es un entrenamiento.
3. Modificar las direcciones bluetooth de las placas Nicla por las de las placas Nicla que se estén utilizando (addressNicla1 y addressNicla2).

En la carpeta "nicla_config" aparece el código Arduino cargado en las placas. Se configuraron para transmitir únicamente el valor del sensor de orientación.

USO: ejecutar app.py

