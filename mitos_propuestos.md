# Mitos propuestos: Cazadores de Mitos, edición adopción digital

Fuente: `data/dataset_sintetico_500.csv` (500 respuestas sintéticas). Escalas de 1 a 7.
**Índice de Adopción** = promedio de Q21_1, Q21_3 y Q21_4.

## 1. Veredictos y evidencia

| ID | Mito | Preguntas | Indicador comparado | Veredicto | Dato clave | Estadístico | Visualización |
|---|---|---|---|---|---|---|---|
| M1 | Los mayores se resisten a lo digital | Q3 | Índice de Adopción | ✖ **DESMENTIDO** | Adopción alta: 19 % (18 a 29) frente a 34 % (50 a 59). Índice 4.52 frente a 4.95 | Diferencia de 0.43 puntos | Barras ordenadas por edad con línea de promedio |
| M2 | Más capacitación = más adopción | Q12 | Índice de Adopción | ? **PLAUSIBLE** | Índice 4.38 (nunca) a 4.91 (varias veces por semana) | Spearman ρ = 0.11 | Línea con puntos (eje desde 4.0) |
| M3 | Si la herramienta es útil, la gente la adopta | Q15_1, Q15_2 | Índice de Adopción | ✔ **CONFIRMADO** | Índice 4.27 (utilidad baja) frente a 5.28 (alta). Adopción alta: 19 % frente a 44 % | Spearman ρ = 0.31 | Heatmap Utilidad × Adopción |
| M4 | Lo presencial enseña mejor que lo virtual | Q14 | Experiencia de aprendizaje (Q24_2, Q24_3, Q29_1, Q29_2, Q29_4) | ✖ **DESMENTIDO** | Presencial 4.76 frente a autoaprendizaje 4.54 | Diferencia máxima de 0.22 puntos | Barras horizontales con eje completo y versión con eje recortado |
| M5 | Los jefes son los más digitales | Q7, Q10 | Índice de Adopción y experiencia digital | ✖ **DESMENTIDO** | Jefatura/Gerencia 4.57 (la más baja) frente a Líder/Coordinador 4.93 (la más alta) | Diferencia de 0.36 puntos | Slope chart: lo que creíamos frente a lo que dicen los datos |
| M6 | A todos les gusta lo llamativo y animado | Q30_1 a Q30_4, Q31_1 a Q34_1 | Preferencias de diseño según sensibilidad | ✖ **DESMENTIDO** | Con sensibilidad alta: simple 3.36, sobrio 3.44, estático 3.62, sin sonido 3.36 (centro = 4). 106 de 500 personas | ρ entre −0.11 y −0.29; sensibilidad frente a adopción ρ = −0.05 | Barras divergentes centradas en 4 |
| R1 | Hombres y mujeres adoptan la tecnología de forma distinta | Q4 | Índice de Adopción | ✖ **DESMENTIDO** | Femenino 4.85 (±0.16) frente a masculino 4.67 (±0.13) | Intervalos de confianza del 95 % que se superponen | Puntos con intervalo de confianza |
| R2 | Si la empresa da licencias y tiempo, la gente usa más la herramienta | Q18_1, Q18_3 | Índice de Adopción | ✔ **CONFIRMADO** | Recursos bajos 4.42, medios 4.72, altos 5.17 | Spearman ρ = 0.21 | Barras por nivel de recursos |
| R3 | Todos prefieren una demostración guiada antes que experimentar solos | Q35_1, Q36_1 | Distribución de preferencias | ✖ **DESMENTIDO** | Q35: 36 % guiado, 28 % neutral, 35 % autónomo. Q36: 32 % demostración, 30 % neutral, 38 % experimentar | Distribución en tercios | Barras 100 % apiladas |

## 2. Dinámicas de juego

| ID | Dinámica | Reto para la audiencia | Respuesta |
|---|---|---|---|
| M1 | Votación con tarjetas | ¿Qué grupo de edad tiene la mayor adopción? | 50 a 59 años |
| M2 | Termómetro humano (0 a 5 dedos) | ¿Qué tan fuerte es la relación entre capacitarse y adoptar? | Medio dedo (relación débil) |
| M3 | Apuesta de fichas | ¿Cuántos puntos separan utilidad baja de utilidad alta? | Cerca de 1.0 punto |
| M4 | Ranking por equipos | ¿La diferencia entre la primera y la última modalidad es menor a 0.5 puntos? | Sí: 0.22 puntos |
| M5 | Votación con el cuerpo (izquierda / centro / derecha) | ¿Jefatura/Gerencia tiene la adopción más alta? | No |
| M6 | Diseña tu material (deslizadores) | ¿Hacia dónde se van las personas más sensibles a los estímulos? | Hacia lo simple y sobrio |
| R1 a R3 | Tarjetas en 10 segundos | ¿Desmentido, plausible o confirmado? | Ver tabla 1 |

## 3. Matices para la sustentación

| ID | Matiz |
|---|---|
| M1 | La diferencia es pequeña: decir que la edad no predice resistencia, no que los mayores adoptan más. |
| M2 | La tendencia existe pero es suave; en la escala completa (1 a 7) casi no se ve. |
| M3 | Correlación no implica causalidad; la teoría (TAM / UTAUT) respalda la dirección utilidad → adopción. |
| M4 | Sirve para mostrar cómo un eje recortado puede fabricar un mito. |
| M5 | Diferencias pequeñas: el nivel jerárquico no predice la adopción. |
| M6 | La sensibilidad no reduce la adopción; pide otro diseño (modo simple, sonido opcional, ritmo propio). |

## Resumen

| Veredicto | Cantidad | Mitos |
|---|---|---|
| ✖ Desmentido | 6 | M1, M4, M5, M6, R1, R3 |
| ? Plausible | 1 | M2 |
| ✔ Confirmado | 2 | M3, R2 |
