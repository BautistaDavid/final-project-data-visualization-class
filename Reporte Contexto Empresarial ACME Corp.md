# Reporte de Diseño Metodológico: Contexto Empresarial y Matriz de Roles
## Dinámica "MythBusters" de Adopción Digital en ACME Corp.

---

## 1. Contexto Empresarial: ACME Corp. (Edición *Looney Tunes*)

### 1.1. Antecedentes
Tras décadas de operaciones basadas en prototipos físicos, pruebas de campo volátiles y lanzamientos guiados por la intuición corporativa (con un alto índice de fallos operativos), la Junta Directiva de **ACME Corp.** ha decretado la **Transformación Digital Inmediata**. El objetivo es migrar de una toma de decisiones por "corazonada" a una cultura impulsada por la analítica de datos.

### 1.2. El Desafío
Dentro de las áreas clave de la organización (**Investigación y Desarrollo, Gerencia, Ventas, Comercial y Gestión Humana**) han surgido diversos sesgos, mitos y resistencias sobre la Adopción Digital. Para abordar esta tensión, se ha convocado a los líderes y colaboradores a la dinámica **"Cazadores de Mitos Analíticos"**.

### 1.3. Reglas de la Dinámica a Ciegas
1. **Asignación de Barajas (STAUT):** Cada participante asume un rol corporativo definido por Edad, Género, Experiencia y Perfil Psicológico.
2. **Evaluación de Mitos a Ciegas:** Los equipos debaten y votan sobre 9 afirmaciones de adopción digital sin ver el panel de control (*dashboard*).
3. **Consenso en Mesas:** Se busca llegar a un veredicto de equipo (Confirmado, Plausible o Desmentido).
4. **Revelación:** Se revela la visualización de datos definitiva (`data/dataset_sintetico_500.csv`) para contrastar las creencia del perfil frente a la evidencia estadística.

---

## 2. Matriz de los 15 Roles Disruptivos (3 Equipos de 5 Personas)

Cada equipo estará compuesto por un representante de cada una de las 5 áreas clave de ACME Corp.

```
+--------------------------------------------------------------------------------------------------+
|                                    MATRIZ GENERAL DE ROLES STAUT                                 |
+----+--------------------+------+--------+-------+-----------------------------+------------------+
| ID | Rol Empresarial    | Edad | Género | Exp.  | Personaje / Puesto ACME     | Equipo           |
+----+--------------------+------+--------+-------+-----------------------------+------------------+
| 01 | I+D                |  48  |    M   | 22 a. | Wile E. Yunques             | Equipo 1         |
| 02 | Gerencia           |  29  |    F   |  4 a. | Speedy Cohete               | Equipo 1         |
| 03 | Ventas             |  55  |    F   | 29 a. | Lola Pistas                 | Equipo 1         |
| 04 | Comercial          |  36  |   NB   | 11 a. | Marvin Radar                | Equipo 1         |
| 05 | GH                 |  42  |    M   | 16 a. | Foghorn "Cluck" Humano      | Equipo 1         |
| 06 | I+D                |  31  |    F   |  6 a. | Beep-Beep Data              | Equipo 2         |
| 07 | Gerencia           |  61  |    M   | 35 a. | Sam Bigotes                 | Equipo 2         |
| 08 | Ventas             |  26  |    M   |  2 a. | Taz Clicks                  | Equipo 2         |
| 09 | Comercial          |  45  |    F   | 18 a. | Petunia Mercado             | Equipo 2         |
| 10 | GH                 |  33  |   NB   |  7 a. | Porky Sensible              | Equipo 2         |
| 11 | I+D                |  24  |    M   |  1 a. | Tweety Prototipos           | Equipo 3         |
| 12 | Gerencia           |  40  |    F   | 14 a. | Penelope Audit              | Equipo 3         |
| 13 | Ventas             |  49  |    M   | 23 a. | Sylvester Rutas             | Equipo 3         |
| 14 | Comercial          |  52  |    F   | 26 a. | Elmer Margen                | Equipo 3         |
| 15 | GH                 |  39  |    M   | 12 a. | Daffy Culture               | Equipo 3         |
+----+--------------------+------+--------+-------+-----------------------------+------------------+
```

### Detalle por Equipos y Perfiles Psicológicos

#### Equipo 1: "Los Yunques Tecnológicos" (Enfoque: Adopción y Experiencia)
*   **01. Wile E. Yunques (I+D | 48 años, M, 22 a. exp.):** *El Saboteador Analógico.* Considera que el valor real de ACME está en la fuerza física del producto. Cuestiona la validez de los modelos predictivos.
*   **02. Speedy Cohete (Gerencia | 29 años, F, 4 a. exp.):** *La Impaciente del ROI.* Quiere resultados instantáneos y automatización total. No tiene paciencia para las curvas de aprendizaje.
*   **03. Lola Pistas (Ventas | 55 años, F, 29 a. exp.):** *La Leyenda del Asfalto.* Negociadora intuitiva que confía en su libreta de notas antes que en un CRM centralizado.
*   **04. Marvin Radar (Comercial | 36 años, NB, 11 a. exp.):** *El Sensor de Tendencias.* Adicto al análisis de datos masivos y tendencias del mercado intergaláctico.
*   **05. Foghorn "Cluck" Humano (GH | 42 años, M, 16 a. exp.):** *El Protector de la Parvada.* Defensor del bienestar del personal; teme que la tecnología cause desempleo o agotamiento laboral.

#### Equipo 2: "Los Correcaminos Analíticos" (Enfoque: Innovación y Escalamiento)
*   **06. Beep-Beep Data (I+D | 31 años, F, 6 a. exp.):** *La Creadora de Algoritmos.* Evangelista digital. Cree que la tecnología útil se adopta por sí sola y sin resistencia.
*   **07. Sam Bigotes (Gerencia | 61 años, M, 35 a. exp.):** *El Patriarca del Consejo.* Defensor del dogma jerárquico. Asume que la alta dirección es la más avanzada tecnológicamente.
*   **08. Taz Clicks (Ventas | 26 años, M, 2 a. exp.):** *El Cazador de Clicks.* Impaciente nativo digital que busca automatizar interacciones a través de scripts y bots.
*   **09. Petunia Mercado (Comercial | 45 años, F, 18 a. exp.):** *La Maestra del Posicionamiento.* Analista pragmática guiada estrictamente por el rigor de la participación de mercado.
*   **10. Porky Sensible (GH | 33 años, NB, 7 a. exp.):** *El Diseñador Minimalista.* Enfocado en la accesibilidad y sensibilidad sensorial. Defiende interfaces sobrias e instruccionales.

#### Equipo 3: "Los Cazadores de Mitos" (Enfoque: Eficiencia y Transformación)
*   **11. Tweety Prototipos (I+D | 24 años, M, 1 a. exp.):** *El Becario Autónomo.* Prefiere la autoexperimentación antes que capacitaciones guiadas o estructuradas.
*   **12. Penelope Audit (Gerencia | 40 años, F, 14 a. exp.):** *La Auditora de Métricas.* Fiscalizadora del dato. Exige correlaciones estadísticas sólidas antes de aprobar decisiones.
*   **13. Sylvester Rutas (Ventas | 49 años, M, 23 a. exp.):** *El Distribuidor Escéptico.* Sostiene que la falta de adopción se debe únicamente a la falta de recursos y presupuesto.
*   **14. Elmer Margen (Comercial | 52 años, F, 26 a. exp.):** *La Realista Financiera.* Mide el éxito digital según la reducción directa de costes operativos.
*   **15. Daffy Culture (GH | 39 años, M, 12 a. exp.):** *El Coach de Cultura Digital.* Facilitador lúdico centrado en eliminar sesgos y garantizar la participación democrática en las mesas.

---

## 3. Matriz de Mitos, Evidencia Estadística y Dinámicas de Juego

| ID | Mito Planteado | Preguntas del Dataset | Indicador / Estadístico | Veredicto Real | Dinámica de Juego en Mesa |
|---|---|---|---|---|---|
| **M1** | Los mayores se resisten a lo digital. | Q3 | Índice Adopción (4.52 en 18-29 vs 4.95 en 50-59). Diff: 0.43. | ✖ **DESMENTIDO** | Votación con tarjetas por rangos de edad. |
| **M2** | Más capacitación = más adopción. | Q12 | Índice Adopción (4.38 nunca vs 4.91 frecuente). Spearman $\rho = 0.11$. | ? **PLAUSIBLE** | Termómetro humano (0 a 5 dedos de intensidad). |
| **M3** | Si la herramienta es útil, la gente la adopta. | Q15_1, Q15_2 | Adopción alta: 19% (utilidad baja) vs 44% (alta). Spearman $\rho = 0.31$. | ✔ **CONFIRMADO** | Apuesta de fichas (estimar diferencia de puntos). |
| **M4** | Lo presencial enseña mejor que lo virtual. | Q14, Q24, Q29 | Presencial 4.76 vs Autoaprendizaje 4.54. Diff máx: 0.22. | ✖ **DESMENTIDO** | Ranking por equipos según efectividad. |
| **M5** | Los jefes son los más digitales. | Q7, Q10 | Gerencia 4.57 (la más baja) vs Coordinador 4.93 (la más alta). | ✖ **DESMENTIDO** | Votación con el cuerpo (posicionamiento en sala). |
| **M6** | A todos les gusta lo llamativo y animado. | Q30, Q31-34 | Sensibilidad alta prefiere lo sobrio (3.44) y estático (3.62). $\rho = -0.11$ a $-0.29$. | ✖ **DESMENTIDO** | Diseña el material con deslizadores visuales. |
| **R1** | Hombres y mujeres adoptan distinto. | Q4 | Femenino 4.85 (±0.16) vs Masculino 4.67 (±0.13). IC 95% superpuestos. | ✖ **DESMENTIDO** | Tarjeta express (10 segundos). |
| **R2** | Recursos y tiempo incrementan la adopción. | Q18_1, Q18_3 | Recursos bajos 4.42 vs altos 5.17. Spearman $\rho = 0.21$. | ✔ **CONFIRMADO** | Tarjeta express (10 segundos). |
| **R3** | Todos prefieren demostración guiada antes que solos. | Q35_1, Q36_1 | Distribución en tercios (36% guiado, 28% neutral, 35% autónomo). | ✖ **DESMENTIDO** | Tarjeta express (10 segundos). |

---

## 4. Guía de Facilitación para el Taller

1. **Fase 1: Enrolamiento (10 min):** Entregar a cada participante la tarjeta de su personaje. Cada uno debe presentarse brevemente asumiendo su edad, experiencia y sesgo corporativo.
2. **Fase 2: Debate a Ciegas por Mosaico (35 min):** El facilitador presenta los mitos uno a uno. Los integrantes discuten desde la postura de su personaje y emiten sus votos/apuestas por equipo.
3. **Fase 3: Revelación Analítica (20 min):** Se proyecta el *dashboard* interactivo. Se analizan los matices estadísticos (ejes recortados, superposición de intervalos de confianza y coeficientes de correlación $\rho$).
4. **Fase 4: Retrospectiva de Adopción (15 min):** Reflexión sobre cómo los prejuicios de cada rol en ACME Corp. afectan la adopción digital real y la toma de decisiones basada en datos.