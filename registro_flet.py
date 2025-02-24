import flet as ft
import re
from bd_medica import registrar_usuario_en_bd

def main(page: ft.Page, prefill_data=None):
    """
    prefill_data: dict con "first_name", "second_name", "last_name",
                  "second_last_name", "email", "phone"
    """
    page.title = "Registro de Usuario - Citas Médicas"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window_width = 800  
    page.window_height = 700
    page.window_resizable = True
    page.padding = 15

    # Interfaces a las que rediriges tras el registro:
    import interfaz_paciente
    import interfaz_medico  # Administrador

    left_width = 450
    right_width = 380
    full_width = left_width
    half_width = (left_width - 10) / 2

    # --- Selección de usuario y especialidad ---
    user_type = ft.RadioGroup(
        content=ft.Row([
            ft.Radio(value="Paciente", label="Paciente"),
            ft.Radio(value="Administrador", label="Administrador"),
        ], alignment=ft.MainAxisAlignment.SPACE_AROUND),
        value="Paciente"
    )
    specialty_dropdown = ft.Dropdown(
        label="Especialidad (solo Administrador)",
        width=220,
        options=[
            ft.dropdown.Option("Seleccionar"),
            ft.dropdown.Option("Medicina General"),
            ft.dropdown.Option("Medicina Familiar"),
            ft.dropdown.Option("Odontología"),
            ft.dropdown.Option("Obstetricia"),
            ft.dropdown.Option("Ginecología"),
        ],
        value="Seleccionar",
        visible=False
    )

    def toggle_specialty_visibility(_):
        specialty_dropdown.visible = (user_type.value == "Administrador")
        page.update()
    user_type.on_change = toggle_specialty_visibility

    # Campos del formulario
    first_name = ft.TextField(label="Primer Nombre *", width=half_width)
    second_name = ft.TextField(label="Segundo Nombre", width=half_width)
    last_name = ft.TextField(label="Primer Apellido *", width=half_width)
    second_last_name = ft.TextField(label="Segundo Apellido", width=half_width)
    email_input = ft.TextField(label="Correo Electrónico *", width=full_width)
    phone_input = ft.TextField(label="Teléfono (10 dígitos) *", width=half_width)
    cedula_input = ft.TextField(label="Cédula (10 dígitos) *", width=half_width)

    # --- Indicadores de requisitos de contraseña ---
    requirement_min_length = ft.Text("• Al menos 8 caracteres", size=13, color="red")
    requirement_uppercase = ft.Text("• Al menos 1 mayúscula", size=13, color="red")
    requirement_digit = ft.Text("• Al menos 1 dígito", size=13, color="red")
    requirement_special = ft.Text("• Al menos 1 carácter especial (@$!%*?&)", size=13, color="red")

    password_input = ft.TextField(
        label="Contraseña *",
        password=True,
        can_reveal_password=True,
        width=half_width
    )
    confirm_password_input = ft.TextField(
        label="Repetir Contraseña *",
        password=True,
        can_reveal_password=True,
        width=half_width
    )

    # --- Prellenar si viene de Google ---
    if prefill_data:
        first_name.value = prefill_data.get("first_name", "")
        second_name.value = prefill_data.get("second_name", "")
        last_name.value = prefill_data.get("last_name", "")
        second_last_name.value = prefill_data.get("second_last_name", "")
        email_input.value = prefill_data.get("email", "")
        phone_input.value = prefill_data.get("phone", "")

    # Preguntas de seguridad
    security_q1_dropdown = ft.Dropdown(
        label="Pregunta 1 🔒",
        width=right_width * 0.9,
        options=[
            ft.dropdown.Option("Seleccionar"),
            ft.dropdown.Option("¿Cuál es el nombre de tu primera mascota?"),
            ft.dropdown.Option("¿Cuál es el apellido de soltera de tu madre?"),
            ft.dropdown.Option("¿En qué ciudad naciste?"),
            ft.dropdown.Option("¿Cuál es tu comida favorita?"),
            ft.dropdown.Option("¿Cuál es el nombre de tu escuela secundaria?")
        ],
        value="Seleccionar"
    )
    security_q1_answer = ft.TextField(label="Respuesta 1 *", width=right_width * 0.9)
    security_question1 = ft.Column([security_q1_dropdown, security_q1_answer], spacing=4)

    security_q2_dropdown = ft.Dropdown(
        label="Pregunta 2 🔒",
        width=right_width * 0.9,
        options=[
            ft.dropdown.Option("Seleccionar"),
            ft.dropdown.Option("¿Cuál es el nombre de tu primera mascota?"),
            ft.dropdown.Option("¿Cuál es el apellido de soltera de tu madre?"),
            ft.dropdown.Option("¿En qué ciudad naciste?"),
            ft.dropdown.Option("¿Cuál es tu comida favorita?"),
            ft.dropdown.Option("¿Cuál es el nombre de tu escuela secundaria?")
        ],
        value="Seleccionar"
    )
    security_q2_answer = ft.TextField(label="Respuesta 2 *", width=right_width * 0.9)
    security_question2 = ft.Column([security_q2_dropdown, security_q2_answer], spacing=4)

    security_q3_dropdown = ft.Dropdown(
        label="Pregunta 3 🔒",
        width=right_width * 0.9,
        options=[
            ft.dropdown.Option("Seleccionar"),
            ft.dropdown.Option("¿Cuál es el nombre de tu primera mascota?"),
            ft.dropdown.Option("¿Cuál es el apellido de soltera de tu madre?"),
            ft.dropdown.Option("¿En qué ciudad naciste?"),
            ft.dropdown.Option("¿Cuál es tu comida favorita?"),
            ft.dropdown.Option("¿Cuál es el nombre de tu escuela secundaria?")
        ],
        value="Seleccionar"
    )
    security_q3_answer = ft.TextField(label="Respuesta 3 *", width=right_width * 0.9)
    security_question3 = ft.Column([security_q3_dropdown, security_q3_answer], spacing=4)

    block2 = ft.Column(
        controls=[
            ft.Text("Preguntas de seguridad:", weight=ft.FontWeight.BOLD, size=16),
            security_question1,
            security_question2,
            security_question3,
        ],
        spacing=15
    )

    global_message = ft.Text("", size=14)

    # -- Función para verificar y colorear requisitos de contraseña --
    def refresh_password_requirements_colors():
        pwd = password_input.value or ""
        # Requisitos
        r_min_len = len(pwd) >= 8
        r_uppercase = bool(re.search(r'[A-Z]', pwd))
        r_digit = bool(re.search(r'\d', pwd))
        r_special = bool(re.search(r'[@$!%*?&]', pwd))

        requirement_min_length.color = "green" if r_min_len else "red"
        requirement_uppercase.color = "green" if r_uppercase else "red"
        requirement_digit.color = "green" if r_digit else "red"
        requirement_special.color = "green" if r_special else "red"

    def update_password_requirements(_):
        refresh_password_requirements_colors()
        page.update()

    password_input.on_change = update_password_requirements

    def limpiar_campos(_):
        for field in [
            first_name, second_name, last_name, second_last_name,
            email_input, phone_input, cedula_input,
            password_input, confirm_password_input,
            security_q1_answer, security_q2_answer, security_q3_answer
        ]:
            field.value = ""
            field.error_text = ""
            field.border_color = None
        security_q1_dropdown.value = "Seleccionar"
        security_q2_dropdown.value = "Seleccionar"
        security_q3_dropdown.value = "Seleccionar"
        global_message.value = ""
        specialty_dropdown.value = "Seleccionar"
        specialty_dropdown.visible = (user_type.value == "Administrador")
        # Reseteamos los colores de requisitos
        requirement_min_length.color = "red"
        requirement_uppercase.color = "red"
        requirement_digit.color = "red"
        requirement_special.color = "red"
        page.update()

    def cancelar(_):
        page.clean()
        import login_flet
        login_flet.main(page)

    def registrar(_):
        # Validaciones
        for field in [first_name, last_name, email_input, cedula_input, phone_input,
                      password_input, confirm_password_input,
                      security_q1_answer, security_q2_answer, security_q3_answer]:
            field.error_text = ""
            field.border_color = None
        security_q1_dropdown.error_text = None
        security_q2_dropdown.error_text = None
        security_q3_dropdown.error_text = None
        global_message.value = ""
        has_error = False

        if not first_name.value.strip():
            first_name.error_text = "El primer nombre es obligatorio"
            first_name.border_color = "red"
            has_error = True
        if not last_name.value.strip():
            last_name.error_text = "El primer apellido es obligatorio"
            last_name.border_color = "red"
            has_error = True
        if not email_input.value.strip():
            email_input.error_text = "El correo es obligatorio"
            email_input.border_color = "red"
            has_error = True
        elif "@" not in email_input.value:
            email_input.error_text = "Correo inválido"
            email_input.border_color = "red"
            has_error = True

        if not cedula_input.value.strip():
            cedula_input.error_text = "La cédula es obligatoria"
            cedula_input.border_color = "red"
            has_error = True
        elif not re.match(r'^\d{10}$', cedula_input.value.strip()):
            cedula_input.error_text = "La cédula debe tener 10 dígitos"
            cedula_input.border_color = "red"
            has_error = True

        if not phone_input.value.strip():
            phone_input.error_text = "El teléfono es obligatorio"
            phone_input.border_color = "red"
            has_error = True
        elif not re.match(r'^\d{10}$', phone_input.value.strip()):
            phone_input.error_text = "El teléfono debe tener 10 dígitos"
            phone_input.border_color = "red"
            has_error = True

        # Validación de contraseña
        if not password_input.value:
            password_input.error_text = "La contraseña es obligatoria"
            password_input.border_color = "red"
            has_error = True
        elif not re.match(r'^(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&]).{8,}$', password_input.value):
            password_input.error_text = "La contraseña no cumple los requisitos"
            password_input.border_color = "red"
            has_error = True

        if not confirm_password_input.value:
            confirm_password_input.error_text = "Debe repetir la contraseña"
            confirm_password_input.border_color = "red"
            has_error = True
        elif password_input.value != confirm_password_input.value:
            confirm_password_input.error_text = "Las contraseñas no coinciden"
            confirm_password_input.border_color = "red"
            has_error = True

        # Validación de preguntas
        if security_q1_dropdown.value == "Seleccionar":
            security_q1_dropdown.error_text = "Seleccione una pregunta"
            has_error = True
        if not security_q1_answer.value.strip():
            security_q1_answer.error_text = "La respuesta es obligatoria"
            has_error = True

        if security_q2_dropdown.value == "Seleccionar":
            security_q2_dropdown.error_text = "Seleccione una pregunta"
            has_error = True
        if not security_q2_answer.value.strip():
            security_q2_answer.error_text = "La respuesta es obligatoria"
            has_error = True

        if security_q3_dropdown.value == "Seleccionar":
            security_q3_dropdown.error_text = "Seleccione una pregunta"
            has_error = True
        if not security_q3_answer.value.strip():
            security_q3_answer.error_text = "La respuesta es obligatoria"
            has_error = True

        # Evitar que la misma pregunta se repita
        if (security_q1_dropdown.value != "Seleccionar" and
            security_q2_dropdown.value != "Seleccionar" and
            security_q3_dropdown.value != "Seleccionar"):
            if len({security_q1_dropdown.value, security_q2_dropdown.value, security_q3_dropdown.value}) < 3:
                global_message.value = "Las preguntas de seguridad deben ser diferentes."
                global_message.color = "red"
                has_error = True

        page.update()
        if has_error:
            return

        global_message.value = "Registrando usuario..."
        global_message.color = "blue"
        page.update()

        # Construir nombres completos
        nombres = first_name.value.strip()
        if second_name.value.strip():
            nombres += " " + second_name.value.strip()
        apellidos = last_name.value.strip()
        if second_last_name.value.strip():
            apellidos += " " + second_last_name.value.strip()

        # Especialidad
        especialidad_seleccionada = (
            specialty_dropdown.value 
            if (user_type.value == "Administrador" and specialty_dropdown.value != "Seleccionar")
            else None
        )

        # Registrar en la BD
        exito, mensaje, new_user_id = registrar_usuario_en_bd(
            user_type.value,
            nombres,
            apellidos,
            email_input.value.strip(),
            phone_input.value.strip(),
            cedula_input.value.strip(),
            password_input.value,
            especialidad_seleccionada,
            security_q1_dropdown.value, security_q1_answer.value.strip(),
            security_q2_dropdown.value, security_q2_answer.value.strip(),
            security_q3_dropdown.value, security_q3_answer.value.strip(),
            None  # Sin fotografía
        )

        global_message.value = mensaje
        global_message.color = "green" if exito else "red"
        page.update()

        if exito and new_user_id:
            # Limpia y entra a la interfaz correspondiente
            page.clean()
            if user_type.value == "Paciente":
                interfaz_paciente.main(page, new_user_id)
            else:
                interfaz_medico.main(page, new_user_id)

    # Estructura visual
    row_user_type = ft.Row([user_type, specialty_dropdown], alignment=ft.MainAxisAlignment.SPACE_AROUND, spacing=10)
    row_names = ft.Row([first_name, second_name], spacing=8)
    row_surnames = ft.Row([last_name, second_last_name], spacing=8)
    row_email = email_input
    row_contact = ft.Row([phone_input, cedula_input], spacing=8)

    # Bloque con requisitos de contraseña
    password_requirements_column = ft.Column(
        [
            requirement_min_length,
            requirement_uppercase,
            requirement_digit,
            requirement_special
        ],
        spacing=5
    )

    row_passwords = ft.Column(
        [
            ft.Row([password_input, confirm_password_input], spacing=8),
            password_requirements_column
        ],
        spacing=5
    )

    block1 = ft.Column(
        [
            row_user_type,
            row_names,
            row_surnames,
            row_email,
            row_contact,
            row_passwords
        ],
        spacing=15
    )

    blocks_row = ft.Row(
        controls=[
            ft.Container(content=block1, width=left_width, padding=5),
            ft.Container(content=block2, width=right_width, padding=5)
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=20
    )

    register_button = ft.ElevatedButton(
        "Registrar",
        on_click=registrar,
        bgcolor="blue",
        color="white",
        width=150,
        height=40
    )
    clear_button = ft.OutlinedButton(
        "Limpiar",
        on_click=limpiar_campos,
        width=150,
        height=40
    )
    cancel_button = ft.ElevatedButton(
        "Cancelar",
        on_click=cancelar,
        bgcolor="red",
        color="white",
        width=150,
        height=40
    )

    form = ft.Column(
        [
            ft.Text("Registro de Usuario", size=24, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
            blocks_row,
            global_message,
            ft.Row([register_button, clear_button, cancel_button], alignment=ft.MainAxisAlignment.CENTER, spacing=10)
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=15
    )

    container = ft.Container(content=form, alignment=ft.alignment.center, padding=15)
    scrollable = ft.ListView(controls=[container], expand=True)
    page.add(scrollable)
    page.update()

    # Inicializar la verificación de la contraseña (por si ya viene prellenada)
    refresh_password_requirements_colors()
    page.update()
