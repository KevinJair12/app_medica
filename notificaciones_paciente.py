import sqlite3
from datetime import datetime, timedelta

DB_NAME = "citas_medicas.db"

def conectar_bd():
    """Conecta a la base de datos y activa las claves foráneas."""
    conexion = sqlite3.connect(DB_NAME)
    conexion.execute("PRAGMA foreign_keys = ON;")
    return conexion

def crear_tabla_notificaciones():
    """Crea la tabla Notificaciones (si no existe)."""
    conexion = conectar_bd()
    cursor = conexion.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Notificaciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cita_id INTEGER,
            paciente_id INTEGER,
            message TEXT,
            leido INTEGER DEFAULT 0,
            FOREIGN KEY(cita_id) REFERENCES Citas(id) ON DELETE CASCADE,
            FOREIGN KEY(paciente_id) REFERENCES Usuarios(id) ON DELETE CASCADE
        );
    """)
    conexion.commit()
    conexion.close()

def generar_notificaciones(paciente_id):
    """
    Genera notificaciones para las citas en estado 'Pendiente' que ocurran en menos de 24 horas.
    Se inserta una notificación si aún no existe para la cita.
    """
    crear_tabla_notificaciones()
    conexion = conectar_bd()
    cursor = conexion.cursor()
    now = datetime.now()
    cursor.execute("""
        SELECT C.id, C.fecha, C.hora, E.nombre, (M.nombres || ' ' || M.apellidos)
        FROM Citas C
        JOIN Medicos M ON C.medico_id = M.id
        JOIN Especialidades E ON M.especialidad_id = E.id
        WHERE C.paciente_id = ? AND C.estado = 'Pendiente'
    """, (paciente_id,))
    citas = cursor.fetchall()
    for cita in citas:
        cita_id, fecha_str, hora_str, especialidad, medico = cita
        cita_dt = datetime.strptime(f"{fecha_str} {hora_str}", "%Y-%m-%d %H:%M")
        diff = cita_dt - now
        if timedelta(0) < diff <= timedelta(hours=24):
            cursor.execute("SELECT id FROM Notificaciones WHERE cita_id = ? AND paciente_id = ?", (cita_id, paciente_id))
            if cursor.fetchone() is None:
                message = f"Tienes una cita de {especialidad} con {medico} el {cita_dt.strftime('%d/%m/%Y')} a las {cita_dt.strftime('%H:%M')}."
                cursor.execute("""
                    INSERT INTO Notificaciones (cita_id, paciente_id, message, leido)
                    VALUES (?, ?, ?, 0)
                """, (cita_id, paciente_id, message))
    conexion.commit()
    conexion.close()

def obtener_notificaciones(paciente_id):
    """Retorna la lista de notificaciones para el paciente."""
    crear_tabla_notificaciones()
    conexion = conectar_bd()
    cursor = conexion.cursor()
    cursor.execute("""
        SELECT id, cita_id, message, leido
        FROM Notificaciones
        WHERE paciente_id = ?
        ORDER BY id DESC
    """, (paciente_id,))
    rows = cursor.fetchall()
    conexion.close()
    notifs = []
    for row in rows:
        notifs.append({
            "id": row[0],
            "cita_id": row[1],
            "message": row[2],
            "leido": row[3]
        })
    return notifs

def marcar_notificacion_leida(notif_id):
    """Marca la notificación como leída."""
    conexion = conectar_bd()
    cursor = conexion.cursor()
    cursor.execute("UPDATE Notificaciones SET leido = 1 WHERE id = ?", (notif_id,))
    conexion.commit()
    conexion.close()

def eliminar_notificacion(notif_id):
    """Elimina la notificación."""
    conexion = conectar_bd()
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM Notificaciones WHERE id = ?", (notif_id,))
    conexion.commit()
    conexion.close()
