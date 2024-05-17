import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Definir los ejercicios
exercises = [
      "FrontSquat",
      "BackSquat",
      "DeadLift",
      "Clean",
      "Snatch",
      "Clean&Jerk"
    ]

# Generar datos de prueba
data = []
end_date = datetime.now()
start_date = end_date - timedelta(days=30)

# Generar datos con saltos de 2 o 3 días
for exercise in exercises:
    date = start_date
    while date <= end_date:
        weight = np.random.randint(100, 200)  # Peso aleatorio entre 100 y 200 lbs

        # Generar una hora aleatoria entre las 08:00 AM y las 10:00 PM
        hour = np.random.randint(8, 22)
        minute = np.random.randint(0, 60)
        second = np.random.randint(0, 60)

        # Combinar la fecha y la hora
        date_with_time = datetime(date.year, date.month, date.day, hour, minute, second)

        record = {
            'ejercicio': exercise,
            'peso_rm': weight,
            'fechahora': date_with_time.isoformat() + 'Z'  # Formato ISO 8601 con 'Z' al final
        }
        data.append(record)
        # Saltar 2 o 3 días
        date += timedelta(days=int(np.random.choice([2, 3])))

# Crear un DataFrame
df = pd.DataFrame(data)

# Guardar a un archivo CSV
df.to_csv('weights_test_data.csv', index=False)

print("Archivo de prueba generado: 'weights_test_data.csv'")
