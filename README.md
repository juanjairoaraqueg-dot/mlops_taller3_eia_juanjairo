# mlops_taller3_eia_juanjairo

Taller 3 de MLOps (Universidad EIA). Se aplica la metodología CRISP-DM / ASUM-DM sobre el
dataset de Kaggle **Data Science Salaries 2023** para predecir el salario (`salario_en_usd`)
de roles de ciencia de datos.

> Autor: Juan Jairo Araque Giraldo. Secciones de MLflow, Optuna, evaluación y despliegue
> completadas con asistencia de Claude (Anthropic).

## Contenido del repositorio

| Archivo | Descripción |
|---|---|
| `Taller_3_Juan_Jairo_MLops.ipynb` | Notebook con todo el desarrollo (negocio, EDA, preparación, modelación, evaluación, despliegue). |
| `app.py` | API FastAPI que expone el pipeline entrenado. |
| `taller3-fastapi.service` | Unit de systemd para mantener la API siempre arriba (daemon). |
| `requirements.txt` | Dependencias del proyecto. |
| `modelo_salarios.pkl` | Pipeline entrenado (se genera al ejecutar el notebook). |
| `ds_salaries.csv` | Dataset de Kaggle. |

## Reproducir el análisis (local)

```bash
python -m venv venv
source venv/bin/activate            # En Windows: venv\Scripts\activate
pip install -r requirements.txt
jupyter notebook Taller_3_Juan_Jairo_MLops.ipynb
```

Ejecuta el notebook completo (Kernel → Restart & Run All). Esto:
1. Entrena los modelos y registra todos los experimentos en **MLflow** (carpeta `./mlruns`).
2. Genera el pipeline de producción `modelo_salarios.pkl`.

Para ver los experimentos en MLflow:

```bash
mlflow ui            # abre http://127.0.0.1:5000
```

## Probar la API en local

```bash
uvicorn app:app --host 0.0.0.0 --port 7000
```

En otra terminal:

```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"año_trabajo":"2023","nivel_experiencia":"SE","tipo_empleo":"FT","titulo_trabajo":"Data Scientist","residencia_empleado":"US","ratio_remoto":"100","ubicacion_empresa":"US","tamaño_empresa":"M"}'
```

Respuesta esperada:

```json
{"salario_en_usd_estimado": 150000.0}
```

## Despliegue en EC2 (paso a paso)

### 1. Lanzar la instancia
- Crear una instancia **EC2** (p. ej. `t2.micro`/`t3.small`, Ubuntu 22.04).
- En el **Security Group**, agregar una regla de entrada: **TCP puerto 8000** desde tu IP
  (o `0.0.0.0/0` para pruebas).
- Descargar la llave `.pem` para conectarte por SSH.

### 2. Conectarse y copiar el proyecto
```bash
ssh -i mi-llave.pem ubuntu@<IP_PUBLICA_EC2>

# Clonar el repo (o usar scp para subir los archivos + modelo_salarios.pkl)
git clone <URL_DEL_REPO> mlops_taller3_eia_juanjairo
cd mlops_taller3_eia_juanjairo
```

> Si el `.pkl` no está versionado, súbelo con:
> `scp -i mi-llave.pem modelo_salarios.pkl ubuntu@<IP_PUBLICA_EC2>:/home/ubuntu/mlops_taller3_eia_juanjairo/`

### 3. Instalar dependencias en la instancia
```bash
sudo apt update && sudo apt install -y python3-venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 4. Probar manualmente (opcional)
```bash
uvicorn app:app --host 0.0.0.0 --port 8000
# Ctrl+C para detener antes de configurar el daemon
```

### 5. Levantar el daemon con systemd (servicio siempre arriba)
Editar `taller3-fastapi.service` si las rutas/usuario difieren (`User`, `WorkingDirectory`,
`ExecStart`), luego:

```bash
sudo cp taller3-fastapi.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now taller3-fastapi.service
sudo systemctl status taller3-fastapi.service   # debe verse "active (running)"
```

Con `enable --now` el servicio arranca al boot y se mantiene corriendo **aunque cierres
la terminal SSH**. `Restart=always` lo reinicia si se cae.

### 6. Probar el endpoint desde tu computador (curl remoto)
```bash
curl -X POST http://<IP_PUBLICA_EC2>:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"año_trabajo":"2023","nivel_experiencia":"SE","tipo_empleo":"FT","titulo_trabajo":"Data Scientist","residencia_empleado":"US","ratio_remoto":"100","ubicacion_empresa":"US","tamaño_empresa":"M"}'
```

Logs del servicio en EC2: `journalctl -u taller3-fastapi.service -f`.

## Foto punto 6

A continuación se muestra una prueba del endpoint usando curl desde local:

![Curl desde local a endpoint](Curl%20desde%20local%20a%20endpoint.png)
